import os
import re
import glob

def convert_typst_to_md(typst_content):
    # Remove Typst imports and show rules
    content = re.sub(r'#import.*?\n', '', typst_content)
    content = re.sub(r'#show.*?\)\n', '', content, flags=re.DOTALL)
    
    # Convert bold *text* to **text**
    # Typst uses *bold* and _italic_, Markdown uses **bold** and *italic*
    # We'll just do a simple replacement for bold for now
    content = re.sub(r'\*(.*?)\*', r'**\1**', content)
    
    # Remove trailing backslashes used for line breaks in Typst
    content = re.sub(r'\\\n', '\n', content)
    
    return content.strip()

def main():
    typst_files = glob.glob("../../*.typ")
    output_dir = "../website/src/content/timeline"
    os.makedirs(output_dir, exist_ok=True)
    
    for file_path in typst_files:
        filename = os.path.basename(file_path)
        if "template" in filename or "grids" in filename:
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        md_content = convert_typst_to_md(content)
        
        # Extract date from filename (e.g., 20241105_1.typ -> 2024-11-05)
        # Assuming format YYYYMMDD_X.typ
        match = re.match(r'(\d{4})(\d{2})(\d{2})_.*\.typ', filename)
        if match:
            year, month, day = match.groups()
            date_str = f"{year}-{month}-{day}"
            
            # Create Markdown file with frontmatter
            md_filename = f"{date_str}-letter.md"
            out_path = os.path.join(output_dir, md_filename)
            
            frontmatter = f"""---
date: {date_str}
title: "Birthday Letter {year}"
type: "letter"
media: []
---
"""
            with open(out_path, "w", encoding="utf-8") as out_f:
                out_f.write(frontmatter + md_content)
                
            print(f"Converted {filename} to {md_filename}")

if __name__ == "__main__":
    main()
