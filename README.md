# Voice to ASL Converter

A Python-based application that converts spoken language into American Sign Language (ASL) videos using speech recognition and the WLASL dataset.

## Features

- **Multi-language Speech Recognition**: Supports English, French, and Arabic using Vosk models
- **ASL Video Generation**: Converts English speech to ASL video sequences
- **Live Transcription**: Real-time speech-to-text with Whisper model
- **Automatic Silence Detection**: Stops recording after detecting silence
- **English-to-ASL Glossing**: Intelligent text normalization and ASL grammar rules

## Requirements

See requirements.txt for Python dependencies.

## Setup

1. Install Python dependencies:
   `ash
   pip install -r requirements.txt
   `

2. Download required Vosk models:
   - [English model](https://alphacephei.com/vosk/models)
   - [French model](https://alphacephei.com/vosk/models)
   - [Arabic model](https://alphacephei.com/vosk/models)

3. Download WLASL dataset:
   - Place videos in WLASL/videos/
   - Include required JSON and text files

## Usage

### Live Recording with Auto-stop
`ash
python vosk_demo.py
`

### Continuous Pipeline
`ash
python vosk_pipeline.py
`

### Live Captioning (Whisper)
`ash
python start.py
`

## Project Structure

- vosk_demo.py - Main demo with silence detection and multi-language support
- vosk_pipeline.py - Continuous speech-to-ASL pipeline
- translate_sentence.py - Core English-to-ASL glossing and video generation
- start.py - Whisper-based live transcription
- test.py - Testing utilities

## Notes

- ASL video generation is only available for English input
- French and Arabic recognition provide text transcription only
- Models and video datasets are not included in the repository (downloadable separately)
