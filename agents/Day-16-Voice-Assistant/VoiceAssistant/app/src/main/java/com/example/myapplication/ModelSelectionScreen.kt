package com.example.myapplication

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ModelSelectionScreen(
    onBackClick: () -> Unit,
    onModelSelected: (WhisperModel) -> Unit
) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val modelDownloader = remember { ModelDownloader(context) }
    val coroutineScope = rememberCoroutineScope()
    
    var downloadedModels by remember { mutableStateOf(modelDownloader.getDownloadedModels()) }
    var selectedModel by remember { mutableStateOf<WhisperModel?>(downloadedModels.firstOrNull()) }
    var currentlyDownloadingModel by remember { mutableStateOf<WhisperModel?>(null) }
    var downloadProgress by remember { mutableStateOf(0) }
    
    // Refresh downloaded models list
    fun refreshDownloadedModels() {
        downloadedModels = modelDownloader.getDownloadedModels()
        if (selectedModel != null && !downloadedModels.contains(selectedModel)) {
            selectedModel = downloadedModels.firstOrNull()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Select Whisper Model") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    if (selectedModel != null) {
                        Button(
                            onClick = { 
                                selectedModel?.let { onModelSelected(it) }
                                onBackClick()
                            },
                            enabled = selectedModel != null
                        ) {
                            Text("Use Selected Model")
                        }
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
        ) {
            Text(
                "Downloaded Models",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            
            if (downloadedModels.isEmpty()) {
                Text(
                    "No models downloaded yet. Please download a model below.",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(bottom = 16.dp)
                )
            } else {
                LazyColumn(
                    modifier = Modifier
                        .weight(0.4f)
                        .fillMaxWidth()
                ) {
                    items(downloadedModels) { model ->
                        ModelItem(
                            model = model,
                            isSelected = model == selectedModel,
                            showDownloadControls = false,
                            onSelect = { selectedModel = model },
                            onDelete = {
                                coroutineScope.launch {
                                    if (modelDownloader.deleteModel(model)) {
                                        refreshDownloadedModels()
                                    }
                                }
                            }
                        )
                    }
                }
            }
            
            Divider(modifier = Modifier.padding(vertical = 16.dp))
            
            Text(
                "Available Models",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            
            LazyColumn(
                modifier = Modifier
                    .weight(0.6f)
                    .fillMaxWidth()
            ) {
                items(ModelDownloader.AVAILABLE_MODELS) { model ->
                    val isDownloaded = downloadedModels.contains(model)
                    val isDownloading = currentlyDownloadingModel == model
                    
                    ModelItem(
                        model = model,
                        isSelected = model == selectedModel,
                        showDownloadControls = !isDownloaded,
                        isDownloading = isDownloading,
                        downloadProgress = if (isDownloading) downloadProgress else 0,
                        onSelect = { if (isDownloaded) selectedModel = model },
                        onDownload = {
                            coroutineScope.launch {
                                currentlyDownloadingModel = model
                                downloadProgress = 0
                                
                                val success = modelDownloader.downloadModel(model) { progress ->
                                    downloadProgress = progress
                                }
                                
                                currentlyDownloadingModel = null
                                if (success) {
                                    refreshDownloadedModels()
                                }
                            }
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun ModelItem(
    model: WhisperModel,
    isSelected: Boolean,
    showDownloadControls: Boolean,
    isDownloading: Boolean = false,
    downloadProgress: Int = 0,
    onSelect: () -> Unit,
    onDownload: (() -> Unit)? = null,
    onDelete: (() -> Unit)? = null
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        color = if (isSelected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface,
        shape = MaterialTheme.shapes.medium,
        onClick = onSelect
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = model.displayName,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                
                Text(
                    text = "Size: ${model.sizeInMb} MB",
                    style = MaterialTheme.typography.bodyMedium
                )
                
                if (isDownloading) {
                    LinearProgressIndicator(
                        progress = { downloadProgress / 100f },
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 8.dp)
                    )
                    Text(
                        text = "Downloading: $downloadProgress%",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
            
            if (isSelected) {
                Icon(
                    imageVector = Icons.Default.Check,
                    contentDescription = "Selected",
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(start = 8.dp)
                )
            }
            
            if (showDownloadControls && onDownload != null) {
                IconButton(
                    onClick = onDownload,
                    enabled = !isDownloading
                ) {
                    Icon(
                        imageVector = Icons.Default.ArrowDropDown,
                        contentDescription = "Download"
                    )
                }
            } else if (onDelete != null) {
                IconButton(onClick = onDelete) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Delete"
                    )
                }
            }
        }
    }
}
