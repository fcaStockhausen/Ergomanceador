#!/bin/bash
# Simple launcher for audio editor (no programming required!)

echo "=========================================="
echo "Karaokeficador - Audio Editor"
echo "=========================================="
echo ""
echo "Starting audio editor for sound designers..."
echo ""

# Activate conda environment and run
$CONDA_EXE run -n karaokeficador python tools/audio_editor_standalone.py
