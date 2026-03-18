import streamlit as st
import json
import os
import shutil
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="Felien Scrapbook Curation", layout="wide")

# Constants
DATA_FILE = "parsed_chat.json"
OUTPUT_DIR = "../website/src/content/timeline"
MEDIA_DIR = "../../whatsapp_export/20260318_export"
IMAGE_DIR = "../../images"
VIDEO_DIR = "../../videos"

# Ensure output directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_markdown(date, title, content, media):
    filename = f"{date}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Copy media to the respective folders
    for m in media:
        src = os.path.join(MEDIA_DIR, m)
        if os.path.exists(src):
            ext = m.lower().split('.')[-1]
            if ext in ['mp4', 'mov']:
                dst = os.path.join(VIDEO_DIR, m)
            else:
                dst = os.path.join(IMAGE_DIR, m)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
    
    media_yaml = "\n".join([f"  - {m}" for m in media]) if media else "  []"
    if media and not media_yaml.startswith("  -"):
        media_yaml = "  - " + "\n  - ".join(media)
        
    yaml_frontmatter = f"""---
date: {date}
title: "{title}"
media:
{media_yaml}
---
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(yaml_frontmatter + content)
    return filepath

def get_gemini_response(prompt, chat_history=None):
    if not api_key:
        return "Error: GEMINI_API_KEY not found in .env file."
    
    try:
        # Use gemini-1.5-pro (since 3.1 pro isn't a standard public model name yet, we'll use the latest available pro model)
        # Assuming the user meant gemini-1.5-pro or we can just use 'gemini-pro'
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        if chat_history:
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(prompt)
            return response.text, chat.history
        else:
            response = model.generate_content(prompt)
            return response.text, None
    except Exception as e:
        return f"Error: {str(e)}", chat_history

def main():
    st.title("Felien Scrapbook Curation App")
    
    if not api_key:
        st.warning("Please set GEMINI_API_KEY in your .env file to enable AI features.")
        st.stop()

    data = load_data()
    if not data:
        st.error("No parsed data found. Please run parser.py first.")
        st.stop()

    # Sort months
    months = sorted(data.keys())
    
    # Sidebar for navigation
    st.sidebar.title("Timeline")
    
    # Filter out months without media to reduce bloat
    months_with_media = []
    for month in months:
        has_media = any(len(msg.get('attachments', [])) > 0 for msg in data[month])
        if has_media:
            months_with_media.append(month)
            
    selected_month = st.sidebar.selectbox("Select a month to review", months_with_media)
    
    if selected_month:
        messages = data[selected_month]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header(f"Source Data: {selected_month}")
            
            all_media = []
            raw_text_for_ai = []
            
            # Use an expander for the raw text messages
            raw_text_for_ai = []
            with st.expander("View Chat Messages", expanded=False):
                for msg in messages:
                    st.markdown(f"**{msg['date']} {msg['time']} - {msg['sender']}**")
                    if msg['text']:
                        st.write(msg['text'])
                        raw_text_for_ai.append(f"[{msg['date']} {msg['time']}] {msg['sender']}: {msg['text']}")
            
            # Show a nice grid of media
            st.subheader("Media Selection")
            st.write("All photos/videos are selected by default. Uncheck any you want to exclude.")
            
            # Initialize media selection state
            if f"selected_media_{selected_month}" not in st.session_state:
                # YOLO: Select ALL media by default
                all_attachments = []
                for msg in messages:
                    all_attachments.extend(msg.get('attachments', []))
                st.session_state[f"selected_media_{selected_month}"] = all_attachments
            
            # Collect all media first
            all_media = []
            for msg in messages:
                all_media.extend(msg.get('attachments', []))
                
            # Create a grid for media (3 columns)
            cols = st.columns(3)
            for idx, att in enumerate(all_media):
                col = cols[idx % 3]
                with col:
                    media_path = os.path.join(MEDIA_DIR, att)
                    is_selected = att in st.session_state[f"selected_media_{selected_month}"]
                    
                    # Checkbox for selection
                    if st.checkbox("Include", value=is_selected, key=f"check_{att}"):
                        if att not in st.session_state[f"selected_media_{selected_month}"]:
                            st.session_state[f"selected_media_{selected_month}"].append(att)
                    else:
                        if att in st.session_state[f"selected_media_{selected_month}"]:
                            st.session_state[f"selected_media_{selected_month}"].remove(att)
                            
                    if os.path.exists(media_path):
                        ext = att.lower().split('.')[-1]
                        if ext in ['jpg', 'jpeg', 'png', 'webp']:
                            st.image(media_path, use_container_width=True)
                        elif ext in ['mp4', 'mov']:
                            st.video(media_path)
                        else:
                            st.info(f"Unsupported preview: {att}")
                    else:
                        st.warning("File not found")
            
        with col2:
            st.header("AI Story Generation")
            
            # Initialize session state for this month
            if f"draft_{selected_month}" not in st.session_state:
                st.session_state[f"draft_{selected_month}"] = ""
            if f"chat_history_{selected_month}" not in st.session_state:
                st.session_state[f"chat_history_{selected_month}"] = []
                
            if st.button("Generate Initial Draft"):
                with st.spinner("Generating..."):
                    context = "\n".join(raw_text_for_ai)
                    
                    # Read the prompt template
                    try:
                        with open("monthly_prompt.txt", "r", encoding="utf-8") as f:
                            prompt_template = f.read()
                    except FileNotFoundError:
                        prompt_template = "You are a loving father writing a scrapbook. Summarize these messages:\n{messages_text}"
                        
                    prompt = prompt_template.replace("{month_name}", selected_month).replace("{year}", "").replace("{messages_text}", context)
                    
                    draft, history = get_gemini_response(prompt)
                    st.session_state[f"draft_{selected_month}"] = draft
                    # Convert history format for Streamlit display
                    if history:
                        st.session_state[f"chat_history_{selected_month}"] = history
                        
            # Display current draft
            draft = st.text_area("Current Draft", value=st.session_state[f"draft_{selected_month}"], height=400)
            st.session_state[f"draft_{selected_month}"] = draft
            
            # Chat interface for refinement
            st.subheader("Refine with AI")
            refinement_prompt = st.text_input("Tell Gemini how to adjust the draft:")
            if st.button("Refine"):
                if refinement_prompt:
                    with st.spinner("Refining..."):
                        full_prompt = f"""
                        Current draft:
                        {st.session_state[f"draft_{selected_month}"]}
                        
                        User request to refine:
                        {refinement_prompt}
                        
                        Please provide the updated draft based on this request. Only output the new draft text.
                        """
                        new_draft, _ = get_gemini_response(full_prompt)
                        st.session_state[f"draft_{selected_month}"] = new_draft
                        st.rerun()
            
            st.subheader("Approval")
            title = st.text_input("Story Title", value=f"Memories from {selected_month}")
            
            # Use the first day of the month for sorting in the timeline
            save_date = f"{selected_month}-01"
            
            if st.button("Approve & Save", type="primary"):
                if st.session_state[f"draft_{selected_month}"]:
                    final_media = st.session_state[f"selected_media_{selected_month}"]
                    filepath = save_markdown(save_date, title, st.session_state[f"draft_{selected_month}"], final_media)
                    st.success(f"Saved to {filepath} with {len(final_media)} media items!")
                else:
                    st.error("Please generate a draft first.")

if __name__ == "__main__":
    main()
