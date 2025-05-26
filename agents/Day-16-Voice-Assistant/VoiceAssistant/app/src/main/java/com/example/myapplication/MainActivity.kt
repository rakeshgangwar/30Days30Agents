package com.example.myapplication

import android.Manifest
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.lifecycleScope
import com.example.myapplication.ui.theme.MyApplicationTheme
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.isGranted
import com.google.accompanist.permissions.rememberMultiplePermissionsState
import com.google.accompanist.permissions.rememberPermissionState
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private lateinit var audioRecorder: AudioRecorder
    private lateinit var whisperManager: WhisperManager
    private lateinit var modelDownloader: ModelDownloader
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        // Initialize audio recorder, whisper manager, and model downloader
        audioRecorder = AudioRecorder(this)
        whisperManager = WhisperManager(this)
        modelDownloader = ModelDownloader(this)
        
        setContent {
            MyApplicationTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen(audioRecorder, whisperManager, modelDownloader, lifecycleScope)
                }
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        audioRecorder.release()
        whisperManager.release()
    }
}

@Composable
fun MainScreen(
    audioRecorder: AudioRecorder,
    whisperManager: WhisperManager,
    modelDownloader: ModelDownloader,
    coroutineScope: kotlinx.coroutines.CoroutineScope
) {
    var currentScreen by remember { mutableStateOf(Screen.VoiceAssistant) }
    var selectedModel by remember { mutableStateOf<WhisperModel?>(null) }
    
    // Check if any models are downloaded and select the first one
    LaunchedEffect(Unit) {
        val downloadedModels = modelDownloader.getDownloadedModels()
        if (downloadedModels.isNotEmpty()) {
            selectedModel = downloadedModels.first()
        }
    }
    
    when (currentScreen) {
        Screen.VoiceAssistant -> {
            VoiceAssistantScreen(
                audioRecorder = audioRecorder,
                whisperManager = whisperManager,
                modelDownloader = modelDownloader,
                selectedModel = selectedModel,
                coroutineScope = coroutineScope,
                onSelectModelClick = { currentScreen = Screen.ModelSelection }
            )
        }
        Screen.ModelSelection -> {
            ModelSelectionScreen(
                onBackClick = { currentScreen = Screen.VoiceAssistant },
                onModelSelected = { model ->
                    selectedModel = model
                    currentScreen = Screen.VoiceAssistant
                }
            )
        }
    }
}

enum class Screen {
    VoiceAssistant, ModelSelection
}

@OptIn(ExperimentalPermissionsApi::class, ExperimentalMaterial3Api::class)
@Composable
fun VoiceAssistantScreen(
    audioRecorder: AudioRecorder,
    whisperManager: WhisperManager,
    modelDownloader: ModelDownloader,
    selectedModel: WhisperModel?,
    coroutineScope: kotlinx.coroutines.CoroutineScope,
    onSelectModelClick: () -> Unit
) {
    val context = LocalContext.current
    var transcribedText by remember { mutableStateOf("") }
    var isRecording by remember { mutableStateOf(false) }
    var isTranscribing by remember { mutableStateOf(false) }
    var isModelInitialized by remember { mutableStateOf(false) }
    var isInitializingModel by remember { mutableStateOf(false) }
    
    // Request appropriate permissions based on Android version
    val permissions = remember {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // Android 13+ uses the new media permissions
            listOf(Manifest.permission.RECORD_AUDIO, Manifest.permission.READ_MEDIA_AUDIO)
        } else {
            // Android 12 and below use the old storage permissions
            listOf(
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            )
        }
    }
    
    val permissionsState = rememberMultiplePermissionsState(permissions = permissions)
    
    // Initialize the model when selected model changes
    LaunchedEffect(selectedModel) {
        if (selectedModel != null && !isModelInitialized && !isInitializingModel) {
            isInitializingModel = true
            coroutineScope.launch {
                val modelPath = modelDownloader.getModelPath(selectedModel)
                if (modelPath != null) {
                    Toast.makeText(context, "Initializing Whisper model...", Toast.LENGTH_SHORT).show()
                    
                    // Initialize the model with the downloaded file
                    isModelInitialized = whisperManager.initModel(modelPath)
                    
                    if (isModelInitialized) {
                        Toast.makeText(context, "Model initialized successfully", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(context, "Failed to initialize model", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(context, "Model file not found", Toast.LENGTH_SHORT).show()
                }
                isInitializingModel = false
            }
        } else if (selectedModel == null) {
            isModelInitialized = false
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Voice Assistant") },
                actions = {
                    IconButton(onClick = onSelectModelClick) {
                        Icon(Icons.Default.Settings, contentDescription = "Select Model")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Model info
            if (selectedModel != null) {
                Text(
                    text = "Using model: ${selectedModel.displayName}",
                    style = MaterialTheme.typography.bodyMedium
                )
            } else {
                ElevatedButton(
                    onClick = onSelectModelClick,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Download a Whisper Model to Start")
                }
            }
            
            // Transcribed text area
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    if (isTranscribing) {
                        CircularProgressIndicator()
                    } else if (transcribedText.isEmpty()) {
                        Text(
                            text = if (selectedModel == null) {
                                "Please select a model first"
                            } else {
                                "Tap the button to start recording"
                            },
                            textAlign = TextAlign.Center,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    } else {
                        Text(
                            text = transcribedText,
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                }
            }
            
            // Recording button
            Button(
                onClick = {
                    if (!permissionsState.allPermissionsGranted) {
                        permissionsState.launchMultiplePermissionRequest()
                        return@Button
                    }
                    
                    if (selectedModel == null) {
                        Toast.makeText(context, "Please select a model first", Toast.LENGTH_SHORT).show()
                        onSelectModelClick()
                        return@Button
                    }
                    
                    if (!isModelInitialized) {
                        Toast.makeText(context, "Model not initialized yet", Toast.LENGTH_SHORT).show()
                        return@Button
                    }
                    
                    if (isRecording) {
                        // Stop recording and transcribe
                        val recordedFile = audioRecorder.stopRecording()
                        isRecording = false
                        
                        if (recordedFile != null) {
                            isTranscribing = true
                            coroutineScope.launch {
                                val result = whisperManager.transcribeAudio(recordedFile)
                                transcribedText = result
                                isTranscribing = false
                            }
                        } else {
                            Toast.makeText(context, "Failed to record audio", Toast.LENGTH_SHORT).show()
                        }
                    } else {
                        // Start recording
                        val file = audioRecorder.startRecording()
                        if (file != null) {
                            isRecording = true
                            Toast.makeText(context, "Recording started", Toast.LENGTH_SHORT).show()
                        } else {
                            Toast.makeText(context, "Failed to start recording", Toast.LENGTH_SHORT).show()
                        }
                    }
                },
                modifier = Modifier.size(64.dp),
                shape = MaterialTheme.shapes.extraLarge,
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isRecording) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                ),
                enabled = selectedModel != null && isModelInitialized && !isTranscribing
            ) {
                Icon(
                    imageVector = if (isRecording) {
                        Icons.Default.Close
                    } else {
                        Icons.Default.Call
                    },
                    contentDescription = if (isRecording) "Stop Recording" else "Start Recording"
                )
            }
            
            // Status text
            Text(
                text = when {
                    selectedModel == null -> "No model selected"
                    isInitializingModel -> "Initializing model..."
                    !isModelInitialized -> "Model not initialized"
                    isTranscribing -> "Transcribing..."
                    isRecording -> "Recording..."
                    else -> "Ready"
                },
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}