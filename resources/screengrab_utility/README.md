# Gradient Screenshot & Video Tool

A Python tool that adds beautiful gradient backgrounds to screenshots and screen recordings on macOS.

## Features

- Add gradient backgrounds to screenshots and QuickTime screen recordings
- Choose from random, custom, or previously used gradient settings
- **Extract colors and style from existing gradient files** to maintain consistency
- Maintain original format: images stay as images, videos stay as videos
- Simple and intuitive PyQt5 interface
- Rounded corners for a polished look
- Command-line options for automation
- **Standalone macOS application** with custom icon

## Installation

### Option 1: Install as a macOS Application

1. Build the standalone application:
   ```bash
   ./build_app.sh
   ```

2. Copy the application to your Applications folder:
   ```bash
   cp -r "dist/Gradient Screenshot.app" /Applications/
   ```

3. Launch the app from your Applications folder or Spotlight

### Option 2: Run from Source

```bash
# Clone the repository or download the script
git clone https://github.com/yourusername/gradient-screenshot.git
cd gradient-screenshot

# Install dependencies
pip install -r requirements.txt

# Run the script
python gradient_screenshot.py
```

## Usage

### Basic Usage

```bash
python gradient_screenshot.py
```

Or simply double-click the application if you installed it as a macOS app.

This will prompt you to select a screenshot or screen recording file and then present options for gradient settings.

### Interactive Mode

When you run the script without specifying colors or direction, it will display an interactive dialog with the following options:

1. **Random background** - Generate new random colors and direction
2. **Reuse last settings** - Use the same colors and direction from your previous run
3. **Custom settings** - Specify your own hex colors and direction
4. **Extract from reference file** - Pick colors and direction from an existing gradient file

For videos, you'll also have the option to select which part of the video to use for the frame (beginning, middle, or end).

### Command Line Options

```bash
python gradient_screenshot.py [media_file] [options]
```

#### Options:

- `-o, --output`: Specify output file path
- `-d, --direction`: Choose gradient direction (`vertical`, `horizontal`, `diagonal`)
- `-c1, --color1`: Starting color in hex format (e.g., `#FF0000FF`)
- `-c2, --color2`: Ending color in hex format (e.g., `#0000FFFF`)
- `-r, --random`: Use random colors
- `-p, --padding`: Padding around the image/video (default: 100 pixels)
- `-b, --border-radius`: Radius for rounded corners (default: 15 pixels)
- `-f, --frame-position`: Position in video to extract frame (0.0 to 1.0, default: 0.5)
- `-n, --noninteractive`: Run in non-interactive mode (no prompts)
- `--reuse`: Reuse last used colors and direction

### Examples

#### Process a screenshot with random colors:

```bash
python gradient_screenshot.py screenshot.png -r
```

#### Process a screen recording with custom colors:

```bash
python gradient_screenshot.py screenrecording.mov -c1 "#FF5733" -c2 "#33FF57" -d diagonal
```

#### Reuse last settings:

```bash
python gradient_screenshot.py screenshot.png --reuse
```

## How It Works

### For Images

1. The script takes a screenshot as input
2. Adds a gradient background with padding
3. Applies rounded corners
4. Saves the result as a PNG file

### For Videos

1. The script takes a QuickTime screen recording as input
2. Processes each frame by adding the same gradient background
3. Applies rounded corners to each frame
4. Combines the frames back into a video with the same properties as the original
5. Saves the result as an MP4 file

## Building the macOS Application

The repository includes scripts to build a standalone macOS application:

1. `app.py` - Entry point for the application
2. `build_app.sh` - Build script that packages everything into a `.app` file
3. `icons/generate_icon.py` - Creates a custom gradient icon for the app

The application is built using PyInstaller and includes all necessary dependencies.

## Configuration

Your last used gradient settings are saved to `~/.gradient_screenshot_config.json` and can be reused with the `--reuse` flag.

## Requirements

### For Running from Source
- Python 3.6+
- Pillow (PIL Fork)
- PyQt5
- OpenCV (for video processing)

### For Building the macOS App
- PyInstaller
- py2app

## License

MIT
