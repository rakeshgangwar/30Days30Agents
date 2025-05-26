package com.example.myapplication

import android.Manifest
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Build
import android.util.Log
import androidx.annotation.RequiresPermission
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder

class AudioRecorder(private val context: Context) {
    companion object {
        private const val TAG = "AudioRecorder"
        private const val SAMPLE_RATE = 16000 // 16kHz
        private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        private const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
    }
    
    private var recorder: AudioRecord? = null
    private var isRecording = false
    private var recordingThread: Thread? = null
    private var outputFile: File? = null
    
    /**
     * Start recording audio
     * @return File where the audio is being recorded, or null if there was an error
     */
    @RequiresPermission(Manifest.permission.RECORD_AUDIO)
    fun startRecording(): File? {
        if (isRecording) {
            Log.w(TAG, "Already recording")
            return outputFile
        }
        
        try {
            // Create output directory if it doesn't exist
            val outputDir = File(context.filesDir, "audio")
            if (!outputDir.exists()) {
                outputDir.mkdirs()
            }
            
            // Create output file with .raw extension
            outputFile = File(outputDir, "recording_${System.currentTimeMillis()}.raw")
            
            // Get minimum buffer size
            val bufferSize = AudioRecord.getMinBufferSize(
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT
            )
            
            if (bufferSize == AudioRecord.ERROR || bufferSize == AudioRecord.ERROR_BAD_VALUE) {
                Log.e(TAG, "Invalid buffer size")
                return null
            }
            
            // Initialize AudioRecord
            recorder = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize
            )
            
            if (recorder?.state != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "AudioRecord not initialized")
                recorder?.release()
                recorder = null
                return null
            }
            
            recorder?.startRecording()
            isRecording = true
            
            // Start recording thread
            recordingThread = Thread {
                writeAudioDataToFile(bufferSize)
            }
            recordingThread?.start()
            
            Log.i(TAG, "Started recording to ${outputFile?.absolutePath}")
            return outputFile
        } catch (e: Exception) {
            Log.e(TAG, "Error starting recording", e)
            stopRecording()
            return null
        }
    }
    
    private fun writeAudioDataToFile(bufferSize: Int) {
        val data = ByteArray(bufferSize)
        val outputStream = FileOutputStream(outputFile)
        
        try {
            while (isRecording) {
                val read = recorder?.read(data, 0, bufferSize) ?: -1
                if (read > 0) {
                    outputStream.write(data, 0, read)
                }
            }
        } catch (e: IOException) {
            Log.e(TAG, "Error writing audio data", e)
        } finally {
            try {
                outputStream.close()
            } catch (e: IOException) {
                Log.e(TAG, "Error closing output stream", e)
            }
        }
    }
    
    /**
     * Convert raw PCM data to WAV format
     * @param rawFile Raw PCM file
     * @return WAV file or null if conversion failed
     */
    private fun convertRawToWav(rawFile: File): File? {
        val wavFile = File(rawFile.parent, rawFile.name.replace(".raw", ".wav"))
        
        try {
            val rawData = rawFile.readBytes()
            val wavOutputStream = FileOutputStream(wavFile)
            
            // Write WAV header
            val totalDataLen = rawData.size + 36
            val byteRate = SAMPLE_RATE * 2 // 16-bit mono
            
            wavOutputStream.write(byteArrayOf(
                'R'.code.toByte(), 'I'.code.toByte(), 'F'.code.toByte(), 'F'.code.toByte(), // RIFF header
                (totalDataLen and 0xff).toByte(),
                (totalDataLen shr 8 and 0xff).toByte(),
                (totalDataLen shr 16 and 0xff).toByte(),
                (totalDataLen shr 24 and 0xff).toByte(),
                'W'.code.toByte(), 'A'.code.toByte(), 'V'.code.toByte(), 'E'.code.toByte(), // WAVE
                'f'.code.toByte(), 'm'.code.toByte(), 't'.code.toByte(), ' '.code.toByte(), // fmt chunk
                16, 0, 0, 0, // 16 bytes PCM
                1, 0, // PCM format
                1, 0, // Mono channel
                (SAMPLE_RATE and 0xff).toByte(),
                (SAMPLE_RATE shr 8 and 0xff).toByte(),
                (SAMPLE_RATE shr 16 and 0xff).toByte(),
                (SAMPLE_RATE shr 24 and 0xff).toByte(),
                (byteRate and 0xff).toByte(),
                (byteRate shr 8 and 0xff).toByte(),
                (byteRate shr 16 and 0xff).toByte(),
                (byteRate shr 24 and 0xff).toByte(),
                2, 0, // Block align
                16, 0, // 16 bits per sample
                'd'.code.toByte(), 'a'.code.toByte(), 't'.code.toByte(), 'a'.code.toByte(), // data chunk
                (rawData.size and 0xff).toByte(),
                (rawData.size shr 8 and 0xff).toByte(),
                (rawData.size shr 16 and 0xff).toByte(),
                (rawData.size shr 24 and 0xff).toByte()
            ))
            
            // Write audio data
            wavOutputStream.write(rawData)
            wavOutputStream.close()
            
            Log.i(TAG, "Converted RAW to WAV: ${wavFile.absolutePath} (${wavFile.length()} bytes)")
            return wavFile
        } catch (e: Exception) {
            Log.e(TAG, "Error converting RAW to WAV", e)
            return null
        }
    }
    
    /**
     * Stop recording audio
     * @return File containing the recorded audio, or null if there was an error
     */
    fun stopRecording(): File? {
        if (!isRecording) {
            Log.w(TAG, "Not recording")
            return outputFile
        }
        
        try {
            isRecording = false
            recorder?.stop()
            recorder?.release()
            recorder = null
            
            try {
                recordingThread?.join(2000) // Wait for recording thread to finish
            } catch (e: InterruptedException) {
                Log.e(TAG, "Error joining recording thread", e)
            }
            recordingThread = null
            
            Log.i(TAG, "Stopped recording")
            
            // Convert RAW to WAV
            val rawFile = outputFile
            if (rawFile != null && rawFile.exists()) {
                val wavFile = convertRawToWav(rawFile)
                if (wavFile != null) {
                    // Delete the raw file
                    rawFile.delete()
                    outputFile = wavFile
                }
            }
            
            return outputFile
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping recording", e)
            return null
        }
    }
    
    /**
     * Check if recording is in progress
     * @return true if recording is in progress
     */
    fun isRecording(): Boolean {
        return isRecording
    }
    
    /**
     * Release resources when no longer needed
     */
    fun release() {
        stopRecording()
    }
}
