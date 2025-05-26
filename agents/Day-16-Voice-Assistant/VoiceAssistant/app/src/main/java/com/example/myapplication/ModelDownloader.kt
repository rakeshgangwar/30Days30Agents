package com.example.myapplication

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL

class ModelDownloader(private val context: Context) {
    companion object {
        private const val TAG = "ModelDownloader"
        
        // Base URL for downloading whisper.cpp models
        private const val WHISPER_MODELS_BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/"
        
        // Available models with their file names and human-readable names
        val AVAILABLE_MODELS = listOf(
            WhisperModel("ggml-tiny.en.bin", "Tiny (English)", 75),
            WhisperModel("ggml-tiny.bin", "Tiny (Multilingual)", 75),
            WhisperModel("ggml-base.en.bin", "Base (English)", 142),
            WhisperModel("ggml-base.bin", "Base (Multilingual)", 142),
            WhisperModel("ggml-small.en.bin", "Small (English)", 466),
            WhisperModel("ggml-small.bin", "Small (Multilingual)", 466),
            WhisperModel("ggml-medium.en.bin", "Medium (English)", 1500),
            WhisperModel("ggml-medium.bin", "Medium (Multilingual)", 1500),
            WhisperModel("ggml-large.bin", "Large (Multilingual)", 2900)
        )
    }
    
    // Directory to store downloaded models
    private val modelsDir = File(context.filesDir, "whisper_models")
    
    init {
        // Create models directory if it doesn't exist
        if (!modelsDir.exists()) {
            modelsDir.mkdirs()
        }
    }
    
    /**
     * Get a list of all downloaded models
     */
    fun getDownloadedModels(): List<WhisperModel> {
        val downloadedFiles = modelsDir.listFiles() ?: return emptyList()
        return AVAILABLE_MODELS.filter { model ->
            downloadedFiles.any { it.name == model.filename }
        }
    }
    
    /**
     * Check if a specific model is downloaded
     */
    fun isModelDownloaded(model: WhisperModel): Boolean {
        return File(modelsDir, model.filename).exists()
    }
    
    /**
     * Get the file path for a model
     */
    fun getModelPath(model: WhisperModel): String? {
        val file = File(modelsDir, model.filename)
        return if (file.exists()) file.absolutePath else null
    }
    
    /**
     * Download a model
     * @param model The model to download
     * @param progressCallback Callback for download progress (0-100)
     * @return True if download was successful
     */
    suspend fun downloadModel(
        model: WhisperModel,
        progressCallback: (Int) -> Unit
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            val outputFile = File(modelsDir, model.filename)
            
            // Skip if already downloaded
            if (outputFile.exists()) {
                progressCallback(100)
                return@withContext true
            }
            
            val url = URL(WHISPER_MODELS_BASE_URL + model.filename)
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 15000
            connection.readTimeout = 15000
            connection.connect()
            
            if (connection.responseCode != HttpURLConnection.HTTP_OK) {
                Log.e(TAG, "Server returned HTTP ${connection.responseCode} for $url")
                return@withContext false
            }
            
            val contentLength = connection.contentLength
            var downloadedBytes = 0L
            var lastProgressUpdate = 0
            
            connection.inputStream.use { input ->
                FileOutputStream(outputFile).use { output ->
                    val buffer = ByteArray(8192)
                    var bytesRead: Int
                    
                    while (input.read(buffer).also { bytesRead = it } != -1) {
                        output.write(buffer, 0, bytesRead)
                        downloadedBytes += bytesRead
                        
                        // Update progress
                        if (contentLength > 0) {
                            val progress = (downloadedBytes * 100 / contentLength).toInt()
                            if (progress > lastProgressUpdate) {
                                lastProgressUpdate = progress
                                progressCallback(progress)
                            }
                        }
                    }
                }
            }
            
            Log.i(TAG, "Downloaded ${model.filename} successfully")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Error downloading model: ${e.message}")
            e.printStackTrace()
            false
        }
    }
    
    /**
     * Delete a downloaded model
     */
    fun deleteModel(model: WhisperModel): Boolean {
        val file = File(modelsDir, model.filename)
        return if (file.exists()) {
            val result = file.delete()
            if (result) {
                Log.i(TAG, "Deleted model ${model.filename}")
            } else {
                Log.e(TAG, "Failed to delete model ${model.filename}")
            }
            result
        } else {
            true // Model doesn't exist, so consider it deleted
        }
    }
}

/**
 * Data class representing a Whisper model
 */
data class WhisperModel(
    val filename: String,
    val displayName: String,
    val sizeInMb: Int
)
