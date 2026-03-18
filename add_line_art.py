#!/usr/bin/env python3
import argparse
import re
import os
import sys
from PIL import Image

def process_image(img_path, grid_size=20):
    """
    Reads an image, converts white background to transparent,
    saves it as *_transparent.png, and generates an ascii art grid
    for Typst meander contour wrapping.
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
    
    # Generate ascii art based on alpha channel
    ascii_art = ""
    cell_w = width / grid_size
    cell_h = height / grid_size
    
    for row in range(grid_size):
        row_str = ""
        for col in range(grid_size):
            left = int(col * cell_w)
            upper = int(row * cell_h)
            right = int((col + 1) * cell_w)
            lower = int((row + 1) * cell_h)
            cell = img.crop((left, upper, right, lower))
            
            # Check if there are opaque pixels (alpha > 50)
            pixels = cell.getdata()
            has_opaque = any(p[3] > 50 for p in pixels)
            row_str += "#" if has_opaque else " "
        ascii_art += row_str + "\n"
        
    return trans_path, ascii_art, aspect_ratio

def main():
    parser = argparse.ArgumentParser(description="Add line art images to a Typst letter with contour wrapping.")
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
    grids_typ_content = ""
    
    for i, img_path in enumerate(args.images):
        print(f"Processing {img_path}...")
        trans_path, ascii_art, aspect_ratio = process_image(img_path, grid_size=20)
        
        # Ensure path starts with / so Typst treats it relative to project root
        typ_trans_path = trans_path if trans_path.startswith("/") else f"/{trans_path}"
        
        grid_var_name = f"img{i+1}_grid"
        # We write the ascii art as a raw string block in Typst
        grids_typ_content += f"#let {grid_var_name} = ```\n{ascii_art}```\n\n"
        
        processed_images.append({
            "path": typ_trans_path,
            "grid_var": grid_var_name,
            "aspect_ratio": aspect_ratio
        })

    # Write the grids to a companion .typ file
    base_letter = os.path.splitext(args.letter)[0]
    grids_file = f"{base_letter}_grids.typ"
    with open(grids_file, "w") as f:
        f.write(grids_typ_content)
        
    print(f"Generated grids in {grids_file}")

    # Update the letter file
    with open(args.letter, "r") as f:
        content = f.read()

    # Add import for grids if not present
    grids_import = f'#import "{os.path.basename(grids_file)}": *\n'
    if grids_import not in content:
        # Put it after the template import
        content = re.sub(r'(#import "[^"]+template\.typ": letter\n)', r'\1' + grids_import, content)

    # Format the line_art_images array
    images_str = "(\n"
    for img in processed_images:
        # Calculate height based on size and aspect ratio
        size_val = float(re.sub(r'[^\d.]', '', args.size))
        size_unit = re.sub(r'[\d.]', '', args.size)
        height_val = size_val * img["aspect_ratio"]
        height_str = f"{height_val:.2f}{size_unit}"
        
        images_str += f'    (path: "{img["path"]}", grid: {img["grid_var"]}, height: {height_str}),\n'
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
        
    print(f"Successfully updated {args.letter} with contour wrapping for {len(args.images)} image(s).")
    print(f"Compile with: typst compile {args.letter} --root .")

if __name__ == "__main__":
    main()
