#!/usr/bin/env python3
"""
Splunk App Icon Generator
Generates the required icon set for Splunk app submissions.
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont

def generate_splunk_icons(text, bg_color, fg_color, use_border, border_width, output_dir="."):
    """
    Generate Splunk app icons in all required sizes.
    
    Args:
        text: 1-2 character string to display on icon
        bg_color: Background hex color (e.g., "#001E36")
        fg_color: Foreground/text hex color (e.g., "#31A8FF")
        use_border: Whether to draw a border
        border_width: Border thickness (0-100 scale)
        output_dir: Directory where icons will be saved (default: current directory)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Splunk required output sizes
    output_configs = [
        ("appIcon.png", 36),
        ("appIcon_2x.png", 72),
        ("appIconAlt.png", 36),
        ("appIconAlt_2x.png", 72)
    ]

    # We draw at a high resolution and downscale for high-quality anti-aliasing
    canvas_size = 512
    # Scale the border width from a 100-unit scale to our 512-unit canvas
    scaled_border = int(border_width * (canvas_size / 100))
    
    # Create a transparent canvas
    img = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 1. Draw Main Background (Rounded Rectangle)
    # Radius is 15% of canvas size
    radius = int(canvas_size * 0.15)
    draw.rounded_rectangle(
        [0, 0, canvas_size, canvas_size],
        radius=radius,
        fill=bg_color
    )

    # 2. Draw Border (Optional)
    if use_border:
        # Inset the border so it stays inside the background
        inset = scaled_border / 2
        draw.rounded_rectangle(
            [inset, inset, canvas_size - inset, canvas_size - inset],
            radius=int(radius * 0.8),
            outline=fg_color,
            width=scaled_border
        )

    # 3. Draw Text
    # Attempt to load Helvetica (Standard on macOS)
    try:
        # Font size is roughly 45% of canvas
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(canvas_size * 0.42))
    except:
        try:
            # Fallback for other systems
            font = ImageFont.truetype("Arial.ttf", int(canvas_size * 0.42))
        except:
            font = ImageFont.load_default()

    # Center the text using 'mm' (Middle-Middle) anchor
    draw.text(
        (canvas_size / 2, canvas_size / 2 + (canvas_size * 0.02)), # Slight y-offset for visual balance
        text,
        fill=fg_color,
        font=font,
        anchor="mm"
    )

    print(f"🚀 Generating Splunk app icons for: '{text}'")
    print(f"   Colors: BG={bg_color}, FG={fg_color} | Border: {use_border}")

    # 4. Resize and Save
    for filename, size in output_configs:
        # Use LANCZOS for the best downscaling quality
        resized_img = img.resize((size, size), resample=Image.Resampling.LANCZOS)
        output_path = os.path.join(output_dir, filename)
        resized_img.save(output_path)
        print(f"  ✅ Created {output_path} ({size}x{size})")
    
    print(f"\n✨ Successfully generated {len(output_configs)} icon files!")

def main():
    parser = argparse.ArgumentParser(
        description="Generate Splunk app icon set with custom text and styling."
    )
    
    parser.add_argument(
        "--text", 
        type=str, 
        required=True, 
        help="The 1-2 character text to display on the icon (e.g., 'CI', 'ML', 'DB')"
    )
    parser.add_argument(
        "--bg", 
        type=str, 
        default="#001E36", 
        help="Background hex color (default: #001E36 - Splunk dark blue)"
    )
    parser.add_argument(
        "--fg", 
        type=str, 
        default="#31A8FF", 
        help="Foreground/text hex color (default: #31A8FF - Splunk light blue)"
    )
    parser.add_argument(
        "--border-width", 
        type=int, 
        default=8, 
        help="Border thickness on 0-100 scale (default: 8)"
    )
    parser.add_argument(
        "--no-border", 
        action="store_false", 
        dest="use_border",
        help="Disable the rounded border"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default=".",
        help="Output directory for generated icons (default: current directory)"
    )
    parser.set_defaults(use_border=True)

    args = parser.parse_args()
    
    # Validate text length
    if len(args.text) > 2:
        print("⚠️  Warning: Text is longer than 2 characters. Icon may look crowded.")
    
    generate_splunk_icons(
        text=args.text,
        bg_color=args.bg,
        fg_color=args.fg,
        use_border=args.use_border,
        border_width=args.border_width,
        output_dir=args.output_dir
    )

if __name__ == "__main__":
    main()
