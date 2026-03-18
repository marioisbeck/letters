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
2. For each image found, check if a corresponding converted image already exists in the `line_art_images` directory (e.g., `raw_images/portrait.jpg` -> `line_art_images/portrait.png`). If it already exists, **skip** this image.
3. For each new image that needs conversion, use the `gemini-imagegen` skill (or your image generation capabilities) to generate an edited/stylized version of the image using the following exact style prompt:

### STYLE PROMPT
Convert the provided photo into an expressive ink fashion illustration. Focus strictly on the people in the image and completely disregard the background and any other objects.

Anchor:
Modern expressive fashion ink illustration similar to editorial fashion sketches

Style:
- elegant black ink line drawing
- loose flowing sketch lines
- expressive brush strokes
- high contrast black ink
- strictly monochrome (black and white only, absolutely NO brown, sepia, or other colors)
- selective dark ink shading
- minimal but confident lines
- fashion illustration aesthetic

Face and proportions:
- realistic facial proportions
- highly accurate likeness to the original subjects (preserve the child's actual looks carefully)
- recognizable facial features
- soft elegant expression

Hair and lines:
- hair drawn with bold flowing brush strokes
- a few expressive stray lines around the subject

Shading:
- limited ink wash shading (black/grey only)
- strong contrast areas in hair and shadows
- no heavy crosshatching

Composition:
- ONLY draw the people from the original image
- completely remove/disregard all background elements, objects, and scenery
- portrait style
- subject centered
- large white negative space
- pure white background

Rendering:
- looks like hand drawn ink on paper
- artistic fashion illustration style
- slightly sketchy but elegant

4. Save the resulting image into the `line_art_images` directory with the exact same base name as the original image (e.g., if the input is `raw_images/portrait.jpg`, the output should be `line_art_images/portrait.png`).
5. Inform the user that the conversion is complete.
6. Remind the user that they can add these images to their letter using the `./add_line_art.py` script, which will automatically extract the image contour and wrap the text around the line art. For example: `./add_line_art.py letters/my_letter.typ line_art_images/portrait.png`
