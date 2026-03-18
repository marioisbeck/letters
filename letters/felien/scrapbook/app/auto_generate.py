import json
import os

DATA_FILE = "parsed_chat.json"
OUTPUT_DIR = "../website/src/content/timeline"

def main():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    months = sorted(data.keys())
    
    for month in months:
        messages = data[month]
        
        # Collect all media for this month
        all_media = []
        raw_text = []
        
        for msg in messages:
            if msg['text']:
                raw_text.append(f"**{msg['date']} {msg['time']} - {msg['sender']}**: {msg['text']}")
            all_media.extend(msg.get('attachments', []))
            
        # Skip months with no media and no text (shouldn't happen, but just in case)
        if not all_media and not raw_text:
            continue

        # Format media for YAML frontmatter
        media_yaml = "\n".join([f"  - {m}" for m in all_media]) if all_media else "  []"
        if all_media and not media_yaml.startswith("  -"):
            media_yaml = "  - " + "\n  - ".join(all_media)

        # Create the markdown content
        # For now, we just dump the raw messages so you can see everything.
        content = f"### Memories from {month}\n\n"
        content += "\n\n".join(raw_text)

        # Use the first day of the month for sorting
        date_str = f"{month}-01"
        title = f"Scrapbook {month}"
        
        yaml_frontmatter = f"""---
date: {date_str}
title: "{title}"
media:
{media_yaml}
---
"""
        filepath = os.path.join(OUTPUT_DIR, f"{date_str}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(yaml_frontmatter + content)
            
        print(f"Generated {filepath} with {len(all_media)} media items.")

if __name__ == "__main__":
    main()
