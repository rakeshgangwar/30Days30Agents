# Voice Assistant Application

This Android application uses the whisper.cpp library to transcribe speech to text locally on your device. It provides a simple interface for recording audio and converting it to text using OpenAI's Whisper model.

## Features

- Record audio from the device microphone
- Transcribe speech to text using Whisper models
- Local processing (no internet required for transcription)
- Simple and intuitive UI

## Setup Instructions

### 1. Download a Whisper Model

This application requires a Whisper model file to function. You'll need to download one of the following models and place it in your app's assets folder:

- `ggml-tiny.en.bin` (39M) - English-only model, fastest but least accurate
- `ggml-base.en.bin` (74M) - English-only model, good balance of speed and accuracy
- `ggml-small.en.bin` (244M) - English-only model, more accurate but slower
- `ggml-medium.en.bin` (769M) - English-only model, even more accurate but slower

You can download these models from the [whisper.cpp releases page](https://github.com/ggerganov/whisper.cpp/releases).

### 2. Add the Model to Your Project

1. Create an `assets` folder in your app's `src/main` directory if it doesn't already exist
2. Copy the downloaded model file to the assets folder

## Building the Project

The project uses CMake to build the native whisper.cpp library. When you build the app, it will automatically download the whisper.cpp source code and build it for Android.

## How to Use

1. Launch the app
2. Grant microphone permissions when prompted
3. Wait for the model to initialize (this may take a few seconds)
4. Tap the microphone button to start recording
5. Speak clearly into the microphone
6. Tap the button again to stop recording and start transcription
7. The transcribed text will appear on the screen

## Technical Details

- The app uses whisper.cpp, a C++ implementation of OpenAI's Whisper model
- JNI (Java Native Interface) is used to bridge between Kotlin and C++
- Audio is recorded in 16kHz format for optimal speech recognition
- The app demonstrates how to use native code in an Android application

## Troubleshooting

- If you encounter build errors related to CMake, make sure you have the NDK installed in Android Studio
- If the model fails to initialize, check that the model file is correctly placed in the assets folder
- For better transcription results, record in a quiet environment and speak clearly

## License

This project uses the whisper.cpp library, which is licensed under the MIT License.
