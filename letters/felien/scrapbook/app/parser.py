import re
import os
import json
from datetime import datetime

def parse_whatsapp_chat(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    messages = []
    
    # Regex to match the WhatsApp chat format
    # Example: [07.11.23, 10:17:31] Mieke van der Laan-Beck: ‎<attached: 00000005-PHOTO-2023-11-07-10-17-31.jpg>
    # Note: WhatsApp sometimes adds LRM (Left-to-Right Mark) \u200e characters, so we handle them.
    pattern = re.compile(r'^[\u200e]*\[(\d{2}\.\d{2}\.\d{2}), (\d{2}:\d{2}:\d{2})\] ([^:]+): (.*)$')
    attachment_pattern = re.compile(r'[\u200e]*<attached: ([^>]+)>')

    current_message = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = pattern.match(line)
        if match:
            date_str, time_str, sender, content = match.groups()
            
            # Parse datetime
            # Format: DD.MM.YY, HH:MM:SS
            dt_obj = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%y %H:%M:%S")
            
            # Check for attachment
            attachments = []
            att_match = attachment_pattern.search(content)
            if att_match:
                attachments.append(att_match.group(1))
                # Remove attachment string from content
                content = attachment_pattern.sub('', content).strip()
            
            current_message = {
                'timestamp': dt_obj.isoformat(),
                'date': dt_obj.strftime("%Y-%m-%d"),
                'time': time_str,
                'sender': sender.strip(),
                'text': content,
                'attachments': attachments
            }
            messages.append(current_message)
        else:
            # Continuation of previous message
            if current_message:
                # Check if the continuation line has an attachment
                att_match = attachment_pattern.search(line)
                if att_match:
                    current_message['attachments'].append(att_match.group(1))
                    line = attachment_pattern.sub('', line).strip()
                
                if line:
                    current_message['text'] += '\n' + line

    # Group messages by day
    events_by_day = {}
    for msg in messages:
        # Skip system messages
        if msg['sender'] == 'Felien Fan Club' or "Messages and calls are end-to-end encrypted" in msg['text']:
            continue
            
        day = msg['date']
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(msg)

    return events_by_day

if __name__ == "__main__":
    chat_file = "../../whatsapp_export/20260318_export/_chat.txt"
    events = parse_whatsapp_chat(chat_file)
    
    # Save to JSON for inspection
    with open("parsed_chat.json", "w", encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    
    print(f"Parsed {sum(len(msgs) for msgs in events.values())} messages across {len(events)} days.")
