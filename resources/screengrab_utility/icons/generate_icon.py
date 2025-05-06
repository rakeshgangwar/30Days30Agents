#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os

def create_gradient_icon(size=1024, colors=None):
    """
    Create a gradient icon for the screenshot utility
    
    Args:
        size (int): Size of the icon in pixels
        colors (list): List of two colors for gradient, default is purple to green
    """
    if colors is None:
        # Purple to green gradient (matching the app's theme)
        colors = [(147, 51, 234), (51, 234, 89)]
    
    # Create a new image with alpha channel
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw rounded rectangle background with gradient
    radius = size // 10
    
    # Create gradient background
    for y in range(size):
        # Calculate color for this line
        ratio = y / size
        r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
        g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
        b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Create mask for rounded corners
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (size, size)], radius, fill=255)
    
    # Apply mask
    icon.putalpha(mask)
    
    # Draw screenshot frame symbol
    frame_padding = size // 4
    frame_size = size - (frame_padding * 2)
    
    # White frame with transparency
    draw.rounded_rectangle(
        [(frame_padding, frame_padding), 
         (frame_padding + frame_size, frame_padding + frame_size)],
        radius // 2,
        outline=(255, 255, 255, 220),
        width=size // 30
    )
    
    # Add a small camera shutter symbol in the center
    center = size // 2
    shutter_size = size // 6
    draw.ellipse(
        [(center - shutter_size, center - shutter_size),
         (center + shutter_size, center + shutter_size)],
        outline=(255, 255, 255, 220),
        width=size // 40
    )
    
    # Add a small inner circle
    inner_size = shutter_size // 2
    draw.ellipse(
        [(center - inner_size, center - inner_size),
         (center + inner_size, center + inner_size)],
        fill=(255, 255, 255, 180)
    )
    
    return icon

def main():
    # Create icons directory if it doesn't exist
    icons_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate the icon
    icon = create_gradient_icon()
    
    # Save the icon
    icon_path = os.path.join(icons_dir, "icon.png")
    icon.save(icon_path)
    
    print(f"Icon generated and saved to: {icon_path}")
    print("Now run create_icns.sh to convert it to an .icns file for macOS")

if __name__ == "__main__":
    main()
