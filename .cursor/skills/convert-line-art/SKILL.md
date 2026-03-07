---
description: Convert images from raw_images to line art in line_art_images
tags: [image, convert, line-art, typst]
---

# Convert to Line Art Skill

This skill converts images placed in the `raw_images` folder into expressive ink fashion illustrations and saves them in the `line_art_images` folder.

## When to use this skill

Use this skill when the user asks to "convert images", "generate line art", or uses a slash command like `/convert` to process images for their Typst letters.

## Instructions

1. Check the `raw_images` directory for any images.
2. For each image found, use the `gemini-imagegen` skill (or your image generation capabilities) to generate an edited/stylized version of the image using the following exact style prompt:

### STYLE PROMPT
Convert the provided photo into an expressive ink fashion illustration.

Anchor:
Modern expressive fashion ink illustration similar to editorial fashion sketches

Style:
- elegant black ink line drawing
- loose flowing sketch lines
- expressive brush strokes
- high contrast black ink
- selective dark ink shading
- minimal but confident lines
- fashion illustration aesthetic

Face and proportions:
- realistic facial proportions
- simplified but recognizable facial features
- soft elegant expression

Hair and lines:
- hair drawn with bold flowing brush strokes
- a few expressive stray lines around the subject

Shading:
- limited ink wash shading
- strong contrast areas in hair and shadows
- no heavy crosshatching

Composition:
- portrait style
- subject centered
- large white negative space
- minimal or no background

Rendering:
- looks like hand drawn ink on paper
- artistic fashion illustration style
- slightly sketchy but elegant

3. Save the resulting image into the `line_art_images` directory with the exact same base name as the original image (e.g., if the input is `raw_images/portrait.jpg`, the output should be `line_art_images/portrait.png`).
4. Inform the user that the conversion is complete and the images are ready to be included in their `.typ` letters.
