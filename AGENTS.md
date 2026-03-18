# Agent Instructions

## Personal Voice and Style Guidelines
When writing personal letters, vows, or similar texts for the user, adhere to the following voice, tone, and style extracted from the author's wedding vows.

### Core Tone
- **Deeply Affectionate & Vulnerable:** Express emotions openly, showing deep appreciation and unconditional love.
- **Adventurous & Reflective:** Frame life and relationships as a shared journey, an exploration, and an adventure. Use metaphors related to nature, navigation (e.g., "true north", "safe harbour"), and discovery.
- **Playful & Intimate:** Balance profound sincerity with lighthearted, intimate humor. Don't shy away from mentioning endearing quirks, inside jokes, or slightly silly moments (e.g., "small cute fart", "guilty pleasure", "pun intended").
- **Honest & Grounded:** Acknowledge hardships, personal battles, and the reality of life's end, but always pivot back to support, resilience, and gratitude.

### Language and Grammar
The author speaks and writes in English, Dutch, and German. Texts often blend these languages or use them for emphasis.

#### 1. English
- **Spelling:** Use British/International English spelling (e.g., *organise*, *harbour*).
- **Style:** Poetic yet accessible. Use strong, emotive vocabulary ("fateful", "immensely grateful", "co-evolving").
- **Phrasing:** Conversational but structured. NEVER use em dashes (`---` or `—`) or en dashes (`--` or `–`). For pauses or side thoughts, strictly use a simple hyphen with spaces on both sides (` - `).

#### 2. Dutch (Nederlands)
- **Style:** Warm, enthusiastic, and conversational.
- **Vocabulary:** Use endearing and expressive terms (e.g., *lekker*, *heerlijk*, *oprecht*, *puur*).
- **Phrasing:** Natural, spoken-style Dutch that conveys excitement and coziness (gezelligheid). Example: "Thuis komen doe ik het liefst vol enthousiasme..."

#### 3. German (Deutsch)
- **Style:** Deep, romantic, and slightly elevated but natural.
- **Vocabulary:** Use expressive, heartfelt nouns and verbs (e.g., *in vollen Zügen genießen*, *bedingungslose Liebe*, *Entdeckungsreise*).
- **Phrasing:** Well-structured sentences that carry emotional weight without being overly formal.

### Multilingual Usage
- **Seamless Transitions:** It is natural to switch between languages between paragraphs or thoughts to capture the exact right feeling.
- **Tri-lingual Emphasis:** For highly important statements (like promises or declarations of love), state them in all three languages for maximum impact.
  - Example: 
    - *I vow to speak the truth to you!*
    - *Ik beloof je dat ik de waarheid zal spreken!*
    - *Ich verspreche, stets die Wahrheit zu sagen!*
  - Example: *I love you, ik hou van je, ich liebe dich*

### Formatting
- Use bullet points for lists of promises or key takeaways.
- Use exclamation marks to convey genuine enthusiasm, but don't overdo it.
- Emoticons like `:-)` or emojis like `😘` can be used sparingly to convey warmth at the end of a thought or the letter.

## Learned User Preferences
- **Letter Format:** Always create letters in `.typ` format using the `template.typ` style (e.g., `#import "/templates/template.typ": letter` and `#show: letter.with(...)`). Do not use Markdown (`.md`) for letters.
- **Line Art Conversion:** When converting images from `raw_images` to `line_art_images`, strictly focus on the people in the image and completely disregard/remove the background and any other objects.
- **Line Art Integration:** When the user wants to add line art to a letter, use the `scripts/add_line_art.py` script. This script automatically processes the image to make its background transparent, and updates the `.typ` file so the text elegantly flows around a rectangular block containing the image. The default image size is structurally set to 150% (12cm x 12cm) in the bottom right corner, but can be adjusted using the `--size` parameter.
