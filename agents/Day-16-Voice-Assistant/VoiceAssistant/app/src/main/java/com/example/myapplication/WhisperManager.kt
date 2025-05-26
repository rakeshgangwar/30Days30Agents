package com.example.myapplication

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.IOException

class WhisperManager(private val context: Context) {
    companion object {
        private const val TAG = "WhisperManager"
        
        // Load the native library
        init {
            System.loadLibrary("whisper_android")
        }
    }
    
    private var modelInitialized = false
    private var currentModelPath: String? = null
    
    /**
     * Initialize the whisper model
     * @param modelPath Full path to the model file
     * @return true if initialization was successful
     */
    suspend fun initModel(modelPath: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val modelFile = File(modelPath)
            if (!modelFile.exists()) {
                Log.e(TAG, "Model file does not exist: $modelPath")
                return@withContext false
            }
            
            Log.i(TAG, "Initializing model from: $modelPath (${modelFile.length()} bytes)")
            
            // Initialize the model
            modelInitialized = nativeInitModel(modelFile.absolutePath)
            if (modelInitialized) {
                currentModelPath = modelPath
                Log.i(TAG, "Model initialized successfully from: $modelPath")
            } else {
                Log.e(TAG, "Failed to initialize model from: $modelPath")
            }
            
            modelInitialized
        } catch (e: Exception) {
            Log.e(TAG, "Error initializing model", e)
            false
        }
    }
    
    /**
     * Transcribe audio file to text
     * @param audioFile Audio file to transcribe
     * @return Transcribed text or error message
     */
    suspend fun transcribeAudio(audioFile: File): String = withContext(Dispatchers.IO) {
        if (!modelInitialized) {
            Log.e(TAG, "Cannot transcribe: Model not initialized")
            return@withContext "Error: Model not initialized"
        }
        
        if (!audioFile.exists()) {
            Log.e(TAG, "Audio file does not exist: ${audioFile.absolutePath}")
            return@withContext "Error: Audio file not found"
        }
        
        Log.i(TAG, "Transcribing audio file: ${audioFile.absolutePath} (${audioFile.length()} bytes)")
        
        try {
            val result = nativeTranscribeAudio(audioFile.absolutePath)
            Log.i(TAG, "Transcription result: $result")
            
            if (result.startsWith("Error:")) {
                Log.e(TAG, "Transcription failed: $result")
            } else if (result.isEmpty()) {
                Log.w(TAG, "Transcription returned empty result")
                return@withContext "No speech detected or audio too short"
            }
            
            result
        } catch (e: Exception) {
            Log.e(TAG, "Error transcribing audio", e)
            "Error: ${e.message}"
        }
    }
    
    /**
     * Get the current model path
     * @return Current model path or null if no model is initialized
     */
    fun getCurrentModelPath(): String? {
        return currentModelPath
    }
    
    /**
     * Check if a model is initialized
     * @return true if a model is initialized
     */
    fun isModelInitialized(): Boolean {
        return modelInitialized
    }
    
    /**
     * Release resources when no longer needed
     */
    fun release() {
        if (modelInitialized) {
            nativeFreeModel()
            modelInitialized = false
            currentModelPath = null
            Log.i(TAG, "Model released")
        }
    }
    
    // Native methods - renamed to avoid conflicts
    private external fun nativeInitModel(modelPath: String): Boolean
    private external fun nativeTranscribeAudio(audioPath: String): String
    private external fun nativeFreeModel()
}
