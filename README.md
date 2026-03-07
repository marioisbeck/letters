# Typst Letters with Line Art Generation

This repository is set up for writing `.typ` letters and converting images into elegant line art illustrations that you can embed in your letters.

## Directory Structure

- `letters/`: Store your `.typ` letter files here.
- `raw_images/`: Place your original photos here.
- `line_art_images/`: The generated line art illustrations will be saved here.
- `template.typ`: A base Typst template for formatting your letters.

## How to use the Image Conversion

This project includes a custom AI skill for Cursor.

1. Drop your photos into the `raw_images` folder.
2. In the Cursor chat, simply type `/convert-line-art` (or ask the AI to "convert my images").
3. The AI will process the images using the specific fashion illustration style prompt and save the results in `line_art_images` with the same name.

## Writing Letters

You can use the provided `template.typ` to write your letters. To compile a letter to PDF, you need [Typst](https://typst.app/) installed on your system:

```bash
typst compile letters/sample_letter.typ
```
