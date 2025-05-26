#include <jni.h>
#include <string>
#include <android/log.h>
#include <vector>
#include <fstream>
#include <thread>

// Include dr_wav for WAV file reading
#define DR_WAV_IMPLEMENTATION
#include "dr_wav.h"

#define WHISPER_IMPLEMENTATION
#include "whisper.h"

#define TAG "WhisperJNI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

static whisper_context* ctx = nullptr;

// Function declaration
bool read_audio_file(const char* filename, std::vector<float>& pcmf32);

extern "C" {

// Initialize whisper model
JNIEXPORT jboolean Java_com_example_myapplication_WhisperManager_nativeInitModel(
    JNIEnv* env, jobject /* this */, jstring modelPath) {
    const char* path = env->GetStringUTFChars(modelPath, nullptr);
    
    // Initialize whisper context with the model
    if (ctx != nullptr) {
        whisper_free(ctx);
        ctx = nullptr;
    }
    
    LOGI("Loading model from: %s", path);
    ctx = whisper_init_from_file(path);
    env->ReleaseStringUTFChars(modelPath, path);
    
    if (ctx == nullptr) {
        LOGE("Failed to initialize whisper context");
        return JNI_FALSE;
    }
    
    LOGI("Model loaded successfully");
    return JNI_TRUE;
}

// Transcribe audio file
JNIEXPORT jstring Java_com_example_myapplication_WhisperManager_nativeTranscribeAudio(
    JNIEnv* env, jobject /* this */, jstring audioPath) {
    if (ctx == nullptr) {
        LOGE("Whisper context not initialized");
        return env->NewStringUTF("Error: Model not initialized");
    }
    
    const char* path = env->GetStringUTFChars(audioPath, nullptr);
    LOGI("Transcribing audio from: %s", path);
    
    // Load audio file and convert to 16kHz mono float
    std::vector<float> pcmf32;
    if (!read_audio_file(path, pcmf32)) {
        LOGE("Failed to read audio file: %s", path);
        env->ReleaseStringUTFChars(audioPath, path);
        return env->NewStringUTF("Error: Failed to read audio file");
    }
    
    LOGI("Successfully loaded audio with %zu samples", pcmf32.size());
    
    // Check if we have enough audio data
    if (pcmf32.size() < 1000) {
        LOGE("Audio file too short: %zu samples", pcmf32.size());
        env->ReleaseStringUTFChars(audioPath, path);
        return env->NewStringUTF("Error: Audio file too short");
    }
    
    // Initialize whisper parameters
    whisper_full_params params = whisper_full_default_params(WHISPER_SAMPLING_GREEDY);
    params.print_realtime = true;
    params.print_progress = true;
    params.print_timestamps = true;
    params.translate = false;
    params.language = "en"; // Can be changed based on user preference
    params.n_threads = std::min(4, (int)std::thread::hardware_concurrency());
    
    LOGI("Starting whisper_full with %zu samples", pcmf32.size());
    
    // Process the audio file
    if (whisper_full(ctx, params, pcmf32.data(), pcmf32.size()) != 0) {
        LOGE("Failed to process audio");
        env->ReleaseStringUTFChars(audioPath, path);
        return env->NewStringUTF("Error: Failed to process audio");
    }
    
    // Get the transcription result
    std::string result;
    const int n_segments = whisper_full_n_segments(ctx);
    LOGI("Transcription complete with %d segments", n_segments);
    
    if (n_segments == 0) {
        LOGI("No transcription segments found");
        env->ReleaseStringUTFChars(audioPath, path);
        return env->NewStringUTF("No speech detected");
    }
    
    for (int i = 0; i < n_segments; ++i) {
        const char* text = whisper_full_get_segment_text(ctx, i);
        LOGI("Segment %d: %s", i, text);
        result += text;
        result += " ";
    }
    
    env->ReleaseStringUTFChars(audioPath, path);
    return env->NewStringUTF(result.c_str());
}

// Free whisper context
JNIEXPORT void Java_com_example_myapplication_WhisperManager_nativeFreeModel(
    JNIEnv* env, jobject /* this */) {
    if (ctx != nullptr) {
        whisper_free(ctx);
        ctx = nullptr;
        LOGI("Whisper context freed");
    }
}

} // extern "C"

// Helper function to read audio file (supports WAV)
bool read_audio_file(const char* filename, std::vector<float>& pcmf32) {
    const char* ext = strrchr(filename, '.');
    
    // Check if it's a WAV file
    if (ext && strcmp(ext, ".wav") == 0) {
        // Try to read as WAV file using dr_wav
        drwav wav;
        if (drwav_init_file(&wav, filename, nullptr)) {
            LOGI("Reading WAV file: channels=%d, sampleRate=%d, totalFrames=%llu", 
                 wav.channels, wav.sampleRate, (unsigned long long)wav.totalPCMFrameCount);
            
            // Only mono files are supported for now
            if (wav.channels != 1) {
                LOGE("WAV file must be mono, got %d channels", wav.channels);
                drwav_uninit(&wav);
                return false;
            }
            
            // Only 16kHz sample rate is supported for now
            if (wav.sampleRate != 16000) {
                LOGE("WAV file must be 16kHz, got %d Hz", wav.sampleRate);
                drwav_uninit(&wav);
                return false;
            }
            
            // Read the samples
            const uint64_t n_samples = wav.totalPCMFrameCount;
            pcmf32.resize(n_samples);
            
            // Convert to 32-bit float
            drwav_read_pcm_frames_f32(&wav, n_samples, pcmf32.data());
            drwav_uninit(&wav);
            
            LOGI("Successfully read %zu samples from WAV file", pcmf32.size());
            
            // Analyze the first few samples to check if they're valid
            if (pcmf32.size() > 10) {
                LOGI("First 10 samples: %f, %f, %f, %f, %f, %f, %f, %f, %f, %f",
                     pcmf32[0], pcmf32[1], pcmf32[2], pcmf32[3], pcmf32[4],
                     pcmf32[5], pcmf32[6], pcmf32[7], pcmf32[8], pcmf32[9]);
            }
            
            return true;
        } else {
            LOGE("Failed to open WAV file: %s", filename);
            
            // Try to read as raw PCM file
            std::ifstream file(filename, std::ios::binary);
            if (!file.is_open()) {
                LOGE("Failed to open file as raw PCM: %s", filename);
                return false;
            }
            
            // Get file size
            file.seekg(0, std::ios::end);
            const size_t file_size = file.tellg();
            file.seekg(0, std::ios::beg);
            
            LOGI("Reading as raw PCM file: size=%zu bytes", file_size);
            
            // Read the entire file as 16-bit PCM
            std::vector<int16_t> pcm16;
            pcm16.resize(file_size / sizeof(int16_t));
            file.read(reinterpret_cast<char*>(pcm16.data()), file_size);
            file.close();
            
            // Convert 16-bit PCM to 32-bit float
            pcmf32.resize(pcm16.size());
            for (size_t i = 0; i < pcm16.size(); i++) {
                pcmf32[i] = static_cast<float>(pcm16[i]) / 32768.0f;
            }
            
            LOGI("Read %zu samples from raw PCM file", pcmf32.size());
            return true;
        }
    } else {
        LOGE("Unsupported file format: %s", filename);
        return false;
    }
}
