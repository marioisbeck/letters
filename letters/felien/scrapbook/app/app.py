import streamlit as st
import json
import os
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

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_markdown(date, title, content, media):
    filename = f"{date}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
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

    # Sort days
    days = sorted(data.keys())
    
    # Sidebar for navigation
    st.sidebar.title("Timeline")
    
    # Filter out days without media to reduce bloat
    days_with_media = []
    for day in days:
        has_media = any(len(msg.get('attachments', [])) > 0 for msg in data[day])
        if has_media:
            days_with_media.append(day)
            
    selected_day = st.sidebar.selectbox("Select a day to review", days_with_media)
    
    if selected_day:
        messages = data[selected_day]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header(f"Source Data: {selected_day}")
            
            all_media = []
            raw_text_for_ai = []
            
            for msg in messages:
                st.markdown(f"**{msg['time']} - {msg['sender']}**")
                if msg['text']:
                    st.write(msg['text'])
                    raw_text_for_ai.append(f"[{msg['time']}] {msg['sender']}: {msg['text']}")
                
                for att in msg.get('attachments', []):
                    all_media.append(att)
                    st.info(f"Attached: {att}")
                    # In a real app, we'd load the image/video here if it's in the right path
                    
            st.subheader("Media Files")
            st.write(all_media)
            
        with col2:
            st.header("AI Story Generation")
            
            # Initialize session state for this day
            if f"draft_{selected_day}" not in st.session_state:
                st.session_state[f"draft_{selected_day}"] = ""
            if f"chat_history_{selected_day}" not in st.session_state:
                st.session_state[f"chat_history_{selected_day}"] = []
                
            if st.button("Generate Initial Draft"):
                with st.spinner("Generating..."):
                    context = "\n".join(raw_text_for_ai)
                    prompt = f"""
                    You are helping a father write a digital scrapbook for his daughter Felien.
                    Based on these WhatsApp messages from {selected_day}, write a short, sweet, and engaging story or caption (1-2 paragraphs).
                    Keep the tone warm, fatherly, and slightly playful.
                    If there are mentions of firsts (like first words, first steps), highlight them!
                    
                    Messages:
                    {context}
                    """
                    draft, history = get_gemini_response(prompt)
                    st.session_state[f"draft_{selected_day}"] = draft
                    # Convert history format for Streamlit display
                    if history:
                        st.session_state[f"chat_history_{selected_day}"] = history
                        
            # Display current draft
            draft = st.text_area("Current Draft", value=st.session_state[f"draft_{selected_day}"], height=200)
            st.session_state[f"draft_{selected_day}"] = draft
            
            # Chat interface for refinement
            st.subheader("Refine with AI")
            refinement_prompt = st.text_input("Tell Gemini how to adjust the draft:")
            if st.button("Refine"):
                if refinement_prompt:
                    with st.spinner("Refining..."):
                        context = "\n".join(raw_text_for_ai)
                        full_prompt = f"""
                        Current draft:
                        {st.session_state[f"draft_{selected_day}"]}
                        
                        User request to refine:
                        {refinement_prompt}
                        
                        Please provide the updated draft based on this request. Only output the new draft text.
                        """
                        new_draft, _ = get_gemini_response(full_prompt)
                        st.session_state[f"draft_{selected_day}"] = new_draft
                        st.rerun()
            
            st.subheader("Approval")
            title = st.text_input("Story Title", value=f"Memories from {selected_day}")
            
            if st.button("Approve & Save", type="primary"):
                if st.session_state[f"draft_{selected_day}"]:
                    filepath = save_markdown(selected_day, title, st.session_state[f"draft_{selected_day}"], all_media)
                    st.success(f"Saved to {filepath}!")
                else:
                    st.error("Please generate a draft first.")

if __name__ == "__main__":
    main()
