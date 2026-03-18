#!/usr/bin/env python3
import argparse
import re
import os
import sys
from PIL import Image

def process_image(img_path):
    """
    Reads an image, converts white background to transparent,
    and saves it as *_transparent.png.
    """
    try:
        img = Image.open(img_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening {img_path}: {e}")
        sys.exit(1)
        
    width, height = img.size
    aspect_ratio = height / width
    
    # Make white pixels transparent
    # Use getdata instead of get_flattened_data for older Pillow versions
    data = img.getdata()
    new_data = []
    for item in data:
        # If pixel is close to white, make it transparent
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    
    # Save transparent version
    base, ext = os.path.splitext(img_path)
    trans_path = f"{base}_transparent.png"
    img.save(trans_path)
    
    return trans_path, aspect_ratio

def main():
    parser = argparse.ArgumentParser(description="Add line art images to a Typst letter with block wrapping.")
    parser.add_argument("letter", help="Path to the letter (.typ) file (e.g., letters/my_letter.typ)")
    parser.add_argument("images", nargs="+", help="Paths to the line art images (e.g., line_art_images/img1.png)")
    parser.add_argument("--opacity", default="15%", help="Opacity of the line art (default: 15%%)")
    parser.add_argument("--size", default="12cm", help="Size of the line art (default: 12cm)")
    args = parser.parse_args()

    if not os.path.exists(args.letter):
        print(f"Error: Letter file '{args.letter}' not found.")
        sys.exit(1)

    # Process images
    processed_images = []
    
    for i, img_path in enumerate(args.images):
        print(f"Processing {img_path}...")
        trans_path, aspect_ratio = process_image(img_path)
        
        # Ensure path starts with / so Typst treats it relative to project root
        typ_trans_path = trans_path if trans_path.startswith("/") else f"/{trans_path}"
        
        processed_images.append({
            "path": typ_trans_path,
            "aspect_ratio": aspect_ratio
        })

    # Update the letter file
    with open(args.letter, "r") as f:
        content = f.read()

    # Format the line_art_images array
    images_str = "(\n"
    for img in processed_images:
        # Calculate height based on size and aspect ratio
        size_val = float(re.sub(r'[^\d.]', '', args.size))
        size_unit = re.sub(r'[\d.]', '', args.size)
        height_val = size_val * img["aspect_ratio"]
        height_str = f"{height_val:.2f}{size_unit}"
        
        images_str += f'    (path: "{img["path"]}", height: {height_str}),\n'
    images_str += "  )"
    
    # Check if line_art_images is already in the file
    if "line_art_images:" in content:
        # Find the start of line_art_images:
        start_idx = content.find("line_art_images:")
        # Find the end of the array (matching parentheses)
        paren_count = 0
        end_idx = -1
        for i in range(start_idx, len(content)):
            if content[i] == '(':
                paren_count += 1
            elif content[i] == ')':
                paren_count -= 1
                if paren_count == 0:
                    end_idx = i + 1
                    break
        if end_idx != -1:
            content = content[:start_idx] + f'line_art_images: {images_str}' + content[end_idx:]
            
        if "line_art_opacity:" in content:
            content = re.sub(r'line_art_opacity:\s*[^,\n]+', f'line_art_opacity: {args.opacity}', content)
        if "line_art_size:" in content:
            content = re.sub(r'line_art_size:\s*[^,\n]+', f'line_art_size: {args.size}', content)
        elif args.size != "12cm":
            # Add it if not present but requested
            content = re.sub(r'(line_art_opacity:\s*[^,\n]+)', r'\1,\n  line_art_size: ' + args.size, content)
    else:
        # Insert into #show: letter.with(
        match = re.search(r'#show:\s*letter\.with\s*\(', content)
        if match:
            insert_pos = match.end()
            insertion = f'\n  line_art_images: {images_str},\n  line_art_opacity: {args.opacity},\n  line_art_size: {args.size},'
            content = content[:insert_pos] + insertion + content[insert_pos:]
        else:
            print("Error: Could not find '#show: letter.with(' in the letter file.")
            sys.exit(1)

    with open(args.letter, "w") as f:
        f.write(content)
        
    print(f"Successfully updated {args.letter} with block wrapping for {len(args.images)} image(s).")
    print(f"Compile with: typst compile {args.letter} --root .")

if __name__ == "__main__":
    main()
