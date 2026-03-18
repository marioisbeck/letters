import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables from the root .env
load_dotenv(".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)

DATA_FILE = "parsed_chat.json"
OUTPUT_DIR = "../website/src/content/timeline"

def get_gemini_story(month, context, letters_context):
    try:
        # Using gemini-2.5-flash as it is the current standard model in the new API
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        with open("monthly_prompt.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        prompt = prompt_template.replace("{month_name}", month).replace("{letters_context}", letters_context).replace("{messages_text}", context)
        
        # Add safety settings to prevent blocking
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
        
        response = model.generate_content(prompt, safety_settings=safety_settings)
        return response.text
    except Exception as e:
        print(f"Error generating for {month}: {e}")
        # Try fallback model if 1.5-pro fails
        try:
            print(f"Trying fallback model for {month}...")
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            # Try one more fallback to the oldest standard model just in case
            try:
                print(f"Trying gemini-1.5-flash for {month}...")
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                return response.text
            except Exception as e3:
                print(f"Final fallback failed: {e3}")
                return f"Ein wunderschöner Monat voller kleiner und großer Momente. (Auto-generated fallback due to error)"

def read_letters():
    letters_text = ""
    try:
        with open("../../20241105_1.typ", "r", encoding="utf-8") as f:
            letters_text += "--- Letter Year 1 ---\n" + f.read() + "\n\n"
        with open("../../20251105_2.typ", "r", encoding="utf-8") as f:
            letters_text += "--- Letter Year 2 ---\n" + f.read() + "\n\n"
    except Exception as e:
        print(f"Warning: Could not read letters: {e}")
    return letters_text

def main():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    months = sorted(data.keys())
    
    letters_context = read_letters()
    
    print(f"Generating stories for {len(months)} months. This might take a minute...")
    
    for month in months:
        messages = data[month]
        
        all_media = []
        raw_text = []
        
        for msg in messages:
            if msg['text']:
                raw_text.append(f"[{msg['date']} {msg['time']}] {msg['sender']}: {msg['text']}")
            all_media.extend(msg.get('attachments', []))
            
        if not all_media and not raw_text:
            continue

        # Curation: Select up to 10 media items to allow for a nice carousel
        curated_media = []
        if len(all_media) > 10:
            # Take evenly spaced samples
            step = len(all_media) / 10
            curated_media = [all_media[int(i * step)] for i in range(10)]
        else:
            curated_media = all_media

        context = "\n".join(raw_text)
        
        print(f"Generating story for {month}...")
        story = get_gemini_story(month, context, letters_context)
        
        # Format media for YAML
        media_yaml = "\n".join([f"  - {m}" for m in curated_media]) if curated_media else "  []"
        if curated_media and not media_yaml.startswith("  -"):
            media_yaml = "  - " + "\n  - ".join(curated_media)

        date_str = f"{month}-01"
        
        # Try to extract a title if Gemini provided one (e.g., ### Title)
        title = f"Erinnerungen aus {month}"
        lines = story.split('\n')
        if lines and lines[0].startswith('### '):
            title = lines[0].replace('### ', '').strip()
            story = '\n'.join(lines[1:]).strip()
        elif lines and lines[0].startswith('# '):
            title = lines[0].replace('# ', '').strip()
            story = '\n'.join(lines[1:]).strip()
        elif lines and lines[0].startswith('**') and lines[0].endswith('**'):
            title = lines[0].replace('**', '').strip()
            story = '\n'.join(lines[1:]).strip()
            
        yaml_frontmatter = f"""---
date: {date_str}
title: "{title.replace('"', "'")}"
media:
{media_yaml}
---
"""
        filepath = os.path.join(OUTPUT_DIR, f"{date_str}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(yaml_frontmatter + story)
            
        # Sleep slightly to avoid rate limits
        time.sleep(2)

if __name__ == "__main__":
    main()
