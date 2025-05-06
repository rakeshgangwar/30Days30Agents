#!/usr/bin/env python3

import argparse
from PIL import Image, ImageDraw
import os
import random
import glob
import json
import sys
import cv2
import numpy as np
import tempfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QRadioButton, QButtonGroup, QLineEdit, QPushButton, 
                             QFileDialog, QMessageBox, QGroupBox, QGridLayout, QSpacerItem, QSizePolicy,
                             QComboBox, QCheckBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette

# Config file to store last used settings
CONFIG_FILE = os.path.expanduser("~/.gradient_screenshot_config.json")

# Video file extensions supported
VIDEO_EXTENSIONS = [".mov", ".mp4", ".m4v"]

# Output formats
IMAGE_OUTPUT_FORMAT = ".png"  # For image outputs
VIDEO_OUTPUT_FORMAT = ".mp4"  # For video outputs

# Suffix for gradient files
GRADIENT_SUFFIX = "_gradient"

def save_config(colors, direction):
    """
    Save the current configuration to a config file.
    
    Args:
        colors (list): List of two colors in hex format
        direction (str): Gradient direction
    """
    config = {
        "colors": colors,
        "direction": direction
    }
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Warning: Could not save configuration: {e}")

def load_config():
    """
    Load the last used configuration from the config file.
    
    Returns:
        dict: Configuration with colors and direction, or None if not found
    """
    if not os.path.exists(CONFIG_FILE):
        return None
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load configuration: {e}")
        return None

def generate_random_colors():
    """
    Generate a pair of random colors for gradient.
    Returns two colors in hex format with alpha.
    """
    # Generate vibrant colors for better visual appeal
    hue1 = random.random()
    hue2 = (hue1 + 0.3 + random.random() * 0.4) % 1.0
    
    # Convert HSV to RGB (simplified conversion)
    def hsv_to_rgb(h, s=0.8, v=0.9):
        h_i = int(h * 6)
        f = h * 6 - h_i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if h_i == 0:
            r, g, b = v, t, p
        elif h_i == 1:
            r, g, b = q, v, p
        elif h_i == 2:
            r, g, b = p, v, t
        elif h_i == 3:
            r, g, b = p, q, v
        elif h_i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        return (int(r * 255), int(g * 255), int(b * 255))
    
    rgb1 = hsv_to_rgb(hue1)
    rgb2 = hsv_to_rgb(hue2)
    
    # Create hex colors with alpha
    color1 = f"#{rgb1[0]:02x}{rgb1[1]:02x}{rgb1[2]:02x}FF"  # Fully opaque
    color2 = f"#{rgb2[0]:02x}{rgb2[1]:02x}{rgb2[2]:02x}FF"  # Fully opaque
    
    return [color1, color2]

def generate_random_direction():
    """
    Generate a random gradient direction.
    Returns one of: 'vertical', 'horizontal', or 'diagonal'
    """
    directions = ['vertical', 'horizontal', 'diagonal']
    return random.choice(directions)

def is_video_file(file_path):
    """
    Check if the file is a video based on its extension.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if it's a video file, False otherwise
    """
    _, ext = os.path.splitext(file_path.lower())
    return ext in VIDEO_EXTENSIONS

def extract_video_frame(video_path, frame_position=0.5):
    """
    Extract a frame from a video file.
    
    Args:
        video_path (str): Path to the video file
        frame_position (float): Position in the video to extract frame (0.0 to 1.0)
        
    Returns:
        PIL.Image: Extracted frame as PIL Image
        dict: Video properties (fps, width, height, total_frames)
    """
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        
        # Check if video opened successfully
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return None, None
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            print(f"Error: Could not determine frame count for {video_path}")
            cap.release()
            return None, None
        
        # Calculate frame number to extract
        frame_to_extract = int(total_frames * frame_position)
        
        # Set position to the desired frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_to_extract)
        
        # Read the frame
        ret, frame = cap.read()
        
        # Release the video capture object
        cap.release()
        
        if not ret:
            print(f"Error: Could not read frame from {video_path}")
            return None, None
        
        # Convert BGR to RGB (OpenCV uses BGR, PIL uses RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(frame_rgb)
        
        # Return the image and video properties
        video_props = {
            "fps": fps,
            "width": width,
            "height": height,
            "total_frames": total_frames
        }
        
        return pil_image, video_props
    
    except Exception as e:
        print(f"Error extracting frame from video: {e}")
        return None, None

def select_media_file():
    """
    Prompt user to select a screenshot or video from the desktop using PyQt5.
    Returns the path to the selected file.
    """
    # Get desktop path
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Create QApplication instance if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Open file dialog
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select a screenshot or screen recording",
        desktop_path,
        "Media Files (*.png *.jpg *.jpeg *.mov *.mp4 *.m4v);;All Files (*.*)"
    )
    
    return file_path

def extract_colors_from_image(image_path):
    """
    Extract the gradient colors and attempt to determine direction from a processed image.
    
    Args:
        image_path (str): Path to the processed image with gradient background
        
    Returns:
        tuple: (colors, direction) where colors is a list of two hex colors and direction is a string
              or None if extraction fails
    """
    try:
        # Open the image
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        
        # Define padding for sampling points (use standard padding value)
        padding = 100
        
        # Sample points for color extraction
        # We'll sample from the corners and edges where the gradient is most visible
        sample_points = [
            (padding, padding),  # Top-left corner of the padding
            (width - padding, padding),  # Top-right corner of the padding
            (padding, height - padding),  # Bottom-left corner of the padding
            (width - padding, height - padding),  # Bottom-right corner of the padding
            (width // 2, padding),  # Top middle
            (padding, height // 2),  # Left middle
            (width - padding, height // 2),  # Right middle
            (width // 2, height - padding)  # Bottom middle
        ]
        
        # Get colors from sample points
        colors = [img.getpixel(point) for point in sample_points]
        
        # Convert RGB to hex
        hex_colors = [f"#{r:02x}{g:02x}{b:02x}FF" for r, g, b in colors]
        
        # Find the most different colors (likely the gradient endpoints)
        max_diff = 0
        color_pair = None
        
        for i in range(len(hex_colors)):
            for j in range(i+1, len(hex_colors)):
                # Calculate color difference (simple Euclidean distance in RGB space)
                c1 = colors[i]
                c2 = colors[j]
                diff = sum((c1[k] - c2[k])**2 for k in range(3))**0.5
                
                if diff > max_diff:
                    max_diff = diff
                    color_pair = [hex_colors[i], hex_colors[j]]
        
        # Determine direction based on color distribution
        # This is a heuristic and may not always be accurate
        horizontal_diff = abs(colors[1][0] - colors[0][0]) + abs(colors[3][0] - colors[2][0])
        vertical_diff = abs(colors[2][0] - colors[0][0]) + abs(colors[3][0] - colors[1][0])
        diagonal_diff = abs(colors[3][0] - colors[0][0])
        
        if diagonal_diff > max(horizontal_diff, vertical_diff):
            direction = "diagonal"
        elif horizontal_diff > vertical_diff:
            direction = "horizontal"
        else:
            direction = "vertical"
        
        print(f"Extracted colors: {color_pair[0]} and {color_pair[1]}")
        print(f"Detected direction: {direction}")
        
        return color_pair, direction
        
    except Exception as e:
        print(f"Error extracting colors from image: {e}")
        return None, None

def is_gradient_file(file_path):
    """
    Check if a file is likely a processed gradient file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if it's likely a gradient file, False otherwise
    """
    # Check if the filename contains the gradient suffix
    filename = os.path.basename(file_path)
    return GRADIENT_SUFFIX in filename

def select_reference_file():
    """
    Prompt user to select a reference file with gradient to extract colors from.
    
    Returns:
        str: Path to the selected file
    """
    # Get desktop path
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Create QApplication instance if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Open file dialog
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select a reference file with gradient",
        desktop_path,
        "Gradient Files (*{0}*.png *{0}*.jpg *{0}*.jpeg *{0}*.mov *{0}*.mp4 *{0}*.m4v);;All Files (*.*)".format(GRADIENT_SUFFIX)
    )
    
    return file_path

class SimplifiedOptionsDialog(QMainWindow):
    def __init__(self, is_video=False):
        super().__init__()
        self.result_colors = None
        self.result_direction = None
        self.result_frame_position = 0.5  # Default to middle frame for videos
        self.last_config = load_config()
        self.custom_group = None  # Initialize to None first
        self.is_video = is_video
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Gradient Options")
        self.setMinimumSize(400, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title label
        title_label = QLabel("Choose Gradient Options")
        title_label.setFont(QFont("Helvetica", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Options group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)
        
        # Radio buttons for main options
        self.option_group = QButtonGroup(self)
        
        # Default options
        options = ["Random background", "Custom settings", "Extract from reference file"]
        
        # Add option to reuse last settings if available
        if self.last_config:
            options.insert(1, "Reuse last settings")
        
        # Create custom settings group first before connecting signals
        self.custom_group = QGroupBox("Custom Settings")
        custom_layout = QGridLayout()
        self.custom_group.setLayout(custom_layout)
        
        # Color inputs
        custom_layout.addWidget(QLabel("Color 1 (hex):"), 0, 0)
        self.color1_input = QLineEdit("#3498dbFF")
        custom_layout.addWidget(self.color1_input, 0, 1)
        
        custom_layout.addWidget(QLabel("Color 2 (hex):"), 1, 0)
        self.color2_input = QLineEdit("#e74c3cFF")
        custom_layout.addWidget(self.color2_input, 1, 1)
        
        # Direction dropdown
        custom_layout.addWidget(QLabel("Direction:"), 2, 0)
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Random", "Vertical", "Horizontal", "Diagonal"])
        custom_layout.addWidget(self.direction_combo, 2, 1)
        
        # Video frame position slider (only for videos)
        if self.is_video:
            video_group = QGroupBox("Video Options")
            video_layout = QGridLayout()
            video_group.setLayout(video_layout)
            
            video_layout.addWidget(QLabel("Frame Position:"), 0, 0)
            frame_options = QComboBox()
            frame_options.addItems(["Beginning", "Middle", "End"])
            frame_options.setCurrentIndex(1)  # Default to middle
            frame_options.currentIndexChanged.connect(self.update_frame_position)
            video_layout.addWidget(frame_options, 0, 1)
            
            main_layout.addWidget(video_group)
        
        # Add radio buttons
        self.radio_buttons = {}
        for i, option in enumerate(options):
            radio = QRadioButton(option)
            radio.setFont(QFont("Helvetica", 12))
            self.option_group.addButton(radio, i)
            options_layout.addWidget(radio)
            self.radio_buttons[option] = radio
            
            # Connect signal to update UI based on selection
            radio.toggled.connect(self.update_ui)
        
        # Select first option by default
        if options:
            self.radio_buttons[options[0]].setChecked(True)
        
        main_layout.addWidget(options_group)
        main_layout.addWidget(self.custom_group)
        
        # Initially hide custom settings if not selected
        self.custom_group.setVisible(False)
        
        # Add spacer
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumSize(100, 40)
        cancel_button.clicked.connect(self.on_cancel)
        button_layout.addWidget(cancel_button)
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setMinimumSize(100, 40)
        ok_button.clicked.connect(self.on_ok)
        button_layout.addWidget(ok_button)
        
        main_layout.addLayout(button_layout)
        
        # Center the window
        self.center()
        
        # Initial UI update to set correct visibility
        self.update_ui()
        
        # Show the dialog
        self.show()
    
    def update_frame_position(self, index):
        # Update frame position based on selection
        if index == 0:  # Beginning
            self.result_frame_position = 0.1
        elif index == 1:  # Middle
            self.result_frame_position = 0.5
        elif index == 2:  # End
            self.result_frame_position = 0.9
    
    def update_ui(self):
        # Show/hide custom settings based on selection
        if self.custom_group:  # Check if custom_group exists
            selected_button = self.option_group.checkedButton()
            if selected_button and selected_button.text() == "Custom settings":
                self.custom_group.setVisible(True)
            else:
                self.custom_group.setVisible(False)
            
            # Adjust window size
            self.adjustSize()
    
    def center(self):
        # Center window on screen
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.desktop().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def on_ok(self):
        # Get selected option
        selected_id = self.option_group.checkedId()
        selected_option = list(self.radio_buttons.keys())[selected_id] if selected_id >= 0 else None
        
        if selected_option == "Random background":
            self.result_colors = generate_random_colors()
            self.result_direction = generate_random_direction()
        elif selected_option == "Reuse last settings" and self.last_config:
            self.result_colors = self.last_config["colors"]
            self.result_direction = self.last_config["direction"]
        elif selected_option == "Extract from reference file":
            # Prompt user to select a reference file
            reference_file = select_reference_file()
            if not reference_file:
                QMessageBox.warning(self, "No File Selected", "No reference file was selected. Please try again.")
                return
                
            # Extract colors and direction
            colors, direction = extract_colors_from_image(reference_file)
            if colors is None or direction is None:
                QMessageBox.critical(self, "Extraction Failed", "Could not extract colors from the reference file.")
                return
                
            self.result_colors = colors
            self.result_direction = direction
        elif selected_option == "Custom settings":
            # Validate hex colors
            try:
                c1 = self.color1_input.text()
                c2 = self.color2_input.text()
                # Add FF for alpha if not specified
                if len(c1) == 7:
                    c1 += "FF"
                if len(c2) == 7:
                    c2 += "FF"
                # Quick validation
                int(c1[1:], 16)
                int(c2[1:], 16)
                self.result_colors = [c1, c2]
                
                # Get direction
                direction_text = self.direction_combo.currentText().lower()
                if direction_text == "random":
                    self.result_direction = generate_random_direction()
                else:
                    self.result_direction = direction_text
            except ValueError:
                QMessageBox.critical(self, "Invalid Color", "Please enter valid hex colors (e.g., #FF0000 or #FF0000FF)")
                return
        
        self.close()
    
    def on_cancel(self):
        self.close()

def prompt_for_color_choice(is_video=False):
    """
    Prompt the user to choose between random colors, custom colors, or last used colors using PyQt5.
    
    Args:
        is_video (bool): Whether the media file is a video
        
    Returns:
        tuple: (colors, direction, frame_position) where colors is a list of two hex colors,
               direction is a string, and frame_position is a float (0.0 to 1.0)
    """
    # Create QApplication instance if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create and show the dialog
    dialog = SimplifiedOptionsDialog(is_video)
    app.exec_()
    
    # Get results
    if dialog.result_colors is None or dialog.result_direction is None:
        print("Operation cancelled.")
        sys.exit(0)
    
    return dialog.result_colors, dialog.result_direction, dialog.result_frame_position

def create_gradient_background(width, height, colors, direction='vertical', padding=100):
    """
    Create a gradient background image.
    
    Args:
        width (int): Width of the background
        height (int): Height of the background
        colors (list): List of colors for gradient
        direction (str): Direction of gradient - 'vertical', 'horizontal', or 'diagonal'
        padding (int): Extra padding around the image
    
    Returns:
        PIL.Image: The gradient background image
    """
    # Create a new image with padding
    bg_width = width + padding * 2
    bg_height = height + padding * 2
    background = Image.new("RGBA", (bg_width, bg_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(background)
    
    # Draw the gradient based on direction
    if direction == 'vertical':
        for y in range(bg_height):
            # Calculate color for this line
            ratio = y / bg_height
            r = int(int(colors[0][1:3], 16) * (1 - ratio) + int(colors[1][1:3], 16) * ratio)
            g = int(int(colors[0][3:5], 16) * (1 - ratio) + int(colors[1][3:5], 16) * ratio)
            b = int(int(colors[0][5:7], 16) * (1 - ratio) + int(colors[1][5:7], 16) * ratio)
            draw.line([(0, y), (bg_width, y)], fill=(r, g, b, 255))
    
    elif direction == 'horizontal':
        for x in range(bg_width):
            # Calculate color for this line
            ratio = x / bg_width
            r = int(int(colors[0][1:3], 16) * (1 - ratio) + int(colors[1][1:3], 16) * ratio)
            g = int(int(colors[0][3:5], 16) * (1 - ratio) + int(colors[1][3:5], 16) * ratio)
            b = int(int(colors[0][5:7], 16) * (1 - ratio) + int(colors[1][5:7], 16) * ratio)
            draw.line([(x, 0), (x, bg_height)], fill=(r, g, b, 255))
    
    elif direction == 'diagonal':
        max_distance = (bg_width**2 + bg_height**2) ** 0.5
        for y in range(bg_height):
            for x in range(bg_width):
                # Calculate distance from top-left corner
                distance = (x**2 + y**2) ** 0.5
                ratio = distance / max_distance
                r = int(int(colors[0][1:3], 16) * (1 - ratio) + int(colors[1][1:3], 16) * ratio)
                g = int(int(colors[0][3:5], 16) * (1 - ratio) + int(colors[1][3:5], 16) * ratio)
                b = int(int(colors[0][5:7], 16) * (1 - ratio) + int(colors[1][5:7], 16) * ratio)
                draw.point((x, y), fill=(r, g, b, 255))
    
    return background

def process_video_with_gradient(video_path, output_path=None, colors=None, direction=None, padding=100, border_radius=15, frame_position=0.5):
    """
    Process a video by applying a gradient background to each frame.
    
    Args:
        video_path (str): Path to the input video file
        output_path (str, optional): Path to save the output video
        colors (list): List of colors for gradient
        direction (str): Direction of gradient
        padding (int): Padding around the video in pixels
        border_radius (int): Radius for rounded corners
        frame_position (float): Position used to extract a sample frame (0.0 to 1.0)
    
    Returns:
        str: Path to the saved output video
    """
    try:
        # Extract a sample frame to get video properties and set up the gradient
        sample_frame, video_props = extract_video_frame(video_path, frame_position)
        
        if sample_frame is None or video_props is None:
            print("Error: Could not extract sample frame from video")
            return None
            
        # Create a temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            # Open the input video
            cap = cv2.VideoCapture(video_path)
            
            # Determine output path if not provided
            if output_path is None:
                filename, _ = os.path.splitext(video_path)
                output_path = f"{filename}{GRADIENT_SUFFIX}{VIDEO_OUTPUT_FORMAT}"
            
            # Get video properties
            fps = video_props["fps"]
            width = int(video_props["width"] + padding * 2)
            height = int(video_props["height"] + padding * 2)
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Create a mask for rounded corners if border_radius > 0
            if border_radius > 0:
                mask = Image.new('L', (video_props["width"], video_props["height"]), 0)
                draw = ImageDraw.Draw(mask)
                # Draw a rectangle with rounded corners
                draw.rounded_rectangle([(0, 0), (video_props["width"], video_props["height"])], border_radius, fill=255)
            
            # Create gradient background (we'll reuse this for all frames)
            background = create_gradient_background(video_props["width"], video_props["height"], colors, direction, padding)
            
            # Calculate position to paste the frame (centered)
            paste_x = padding
            paste_y = padding
            
            # Process each frame
            frame_count = 0
            total_frames = int(video_props["total_frames"])
            
            print(f"Processing video with {total_frames} frames...")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Update progress every 10% of frames
                if frame_count % max(1, int(total_frames / 10)) == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")
                
                # Convert frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_frame = Image.fromarray(frame_rgb).convert("RGBA")
                
                # Apply rounded corners if needed
                if border_radius > 0:
                    pil_frame.putalpha(mask)
                
                # Create a copy of the background for this frame
                frame_bg = background.copy()
                
                # Paste the frame onto the background
                frame_bg.paste(pil_frame, (paste_x, paste_y), pil_frame)
                
                # Convert back to OpenCV format
                cv_frame = cv2.cvtColor(np.array(frame_bg), cv2.COLOR_RGBA2BGR)
                
                # Write the frame
                out.write(cv_frame)
                
                frame_count += 1
            
            # Release resources
            cap.release()
            out.release()
            
            print(f"Video processing complete: {frame_count} frames processed")
            print(f"Gradient video saved to: {output_path}")
            
            return output_path
            
    except Exception as e:
        print(f"Error processing video: {e}")
        return None

def add_gradient_background(media_path, output_path=None, direction=None, colors=None, padding=100, border_radius=15, frame_position=0.5):
    """
    Add a gradient background to an image or video.
    
    Args:
        media_path (str): Path to the image or video file
        output_path (str, optional): Path to save the output file. If None, will use input name with '_gradient' suffix
        direction (str, optional): Direction of gradient - 'vertical', 'horizontal', or 'diagonal'. If None, will be random
        colors (list): List of colors for gradient, default is random colors
        padding (int): Padding around the media in pixels
        border_radius (int): Radius for rounded corners
        frame_position (float): Position in the video to extract frame (0.0 to 1.0), only for videos
    
    Returns:
        str: Path to the saved output file
    """
    # Check if the file is a video
    is_video = is_video_file(media_path)
    
    # If no colors or direction specified, prompt the user
    if colors is None and direction is None and not os.environ.get('GRADIENT_SCREENSHOT_NONINTERACTIVE'):
        colors, direction, frame_position = prompt_for_color_choice(is_video)
    else:
        # Generate random colors if none provided
        if colors is None:
            colors = generate_random_colors()
            print(f"Using random colors: {colors[0]} and {colors[1]}")
        
        # Generate random direction if none provided
        if direction is None:
            direction = generate_random_direction()
            print(f"Using random direction: {direction}")
    
    # Save the configuration for future use
    save_config(colors, direction)
    
    print(f"Using colors: {colors[0]} and {colors[1]}")
    print(f"Using direction: {direction}")
    
    # Process based on file type
    if is_video:
        print(f"Processing video file: {media_path}")
        return process_video_with_gradient(
            media_path, 
            output_path, 
            colors, 
            direction, 
            padding, 
            border_radius, 
            frame_position
        )
    else:
        # Process image
        try:
            img = Image.open(media_path).convert("RGBA")
        except Exception as e:
            print(f"Error opening image file: {e}")
            return None
        
        # Create a mask for rounded corners if border_radius > 0
        if border_radius > 0:
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            # Draw a rectangle with rounded corners
            draw.rounded_rectangle([(0, 0), (img.width, img.height)], border_radius, fill=255)
            # Apply the mask to the image
            img.putalpha(mask)
        
        # Create gradient background
        background = create_gradient_background(img.width, img.height, colors, direction, padding)
        
        # Calculate position to paste the image (centered)
        paste_x = padding
        paste_y = padding
        
        # Paste the image onto the background
        background.paste(img, (paste_x, paste_y), img)
        
        # Determine output path if not provided
        if output_path is None:
            filename, ext = os.path.splitext(media_path)
            output_path = f"{filename}{GRADIENT_SUFFIX}{IMAGE_OUTPUT_FORMAT}"
        
        # Save the result
        background.save(output_path)
        print(f"Gradient image saved to: {output_path}")
        
        return output_path

def main():
    parser = argparse.ArgumentParser(description='Add a gradient background to an image or video')
    parser.add_argument('media', nargs='?', help='Path to the image or video file (optional, will prompt if not provided)')
    parser.add_argument('-o', '--output', help='Path to save the output file')
    parser.add_argument('-d', '--direction', choices=['vertical', 'horizontal', 'diagonal'],
                        help='Direction of the gradient (default: random)')
    parser.add_argument('-c1', '--color1', help='Starting color in hex format with alpha (e.g., #00000088)')
    parser.add_argument('-c2', '--color2', help='Ending color in hex format with alpha (e.g., #00000088)')
    parser.add_argument('-r', '--random', action='store_true', help='Use random colors for gradient')
    parser.add_argument('-p', '--padding', type=int, default=100, help='Padding around the media in pixels')
    parser.add_argument('-b', '--border-radius', type=int, default=15, help='Radius for rounded corners')
    parser.add_argument('-f', '--frame-position', type=float, default=0.5, help='Position in video to extract frame (0.0 to 1.0)')
    parser.add_argument('-n', '--noninteractive', action='store_true', help='Run in non-interactive mode (no prompts)')
    parser.add_argument('--reuse', action='store_true', help='Reuse the last used colors and direction')
    
    args = parser.parse_args()
    
    # Set environment variable for non-interactive mode
    if args.noninteractive:
        os.environ['GRADIENT_SCREENSHOT_NONINTERACTIVE'] = '1'
    
    # If reuse flag is set, load the last configuration
    colors = None
    direction = args.direction
    if args.reuse:
        config = load_config()
        if config:
            colors = config["colors"]
            if not direction:  # Only use saved direction if not specified in command line
                direction = config["direction"]
            print(f"Reusing last configuration: colors={colors}, direction={direction}")
        else:
            print("No saved configuration found. Using defaults.")
    elif args.color1 and args.color2:
        colors = [args.color1, args.color2]
    
    # Create QApplication instance if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # If no media path provided, prompt to select one
    media_path = args.media
    if not media_path:
        media_path = select_media_file()
        if not media_path:
            print("No file selected. Exiting.")
            return
    
    add_gradient_background(
        media_path,
        args.output,
        direction,
        colors,
        args.padding,
        args.border_radius,
        args.frame_position
    )

if __name__ == "__main__":
    main()
