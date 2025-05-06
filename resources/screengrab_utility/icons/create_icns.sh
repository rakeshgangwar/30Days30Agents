#!/bin/bash

# Script to convert PNG to ICNS file for macOS app

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Check if the PNG file exists
if [ ! -f "icon.png" ]; then
    echo "Error: icon.png not found in the current directory."
    exit 1
 fi

# Create temporary iconset directory
mkdir -p icon.iconset

# Generate different icon sizes
sips -z 16 16 icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32 icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32 icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64 icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128 icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256 icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256 icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512 icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# Convert iconset to icns file
iconutil --convert icns --output ../icon.icns icon.iconset

# Clean up
rm -rf icon.iconset

echo "Icon created successfully at: $(dirname "$(pwd)")/icon.icns"
