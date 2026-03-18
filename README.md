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

You can use the provided `template.typ` to write your letters. To compile a letter to PDF, you need [Typst](https://typst.app/) installed on your system. 

*Note: It is recommended to compile from the project root so that absolute paths to templates and images work correctly.*

```bash
typst compile letters/your_letter.typ --root .
```

## Adding Line Art to Letters

You can easily add generated line art images to the bottom right corner of your letters. The system will automatically:
1. Increase the image size to 150% (12cm x 12cm).
2. Extract the contour of the people in the line art using an ASCII art representation.
3. Make the text flow elegantly *around* the contour of the image.
4. Keep the image slightly transparent so it blends beautifully with the page.

If your letter has multiple pages, you can provide multiple images, and it will cycle through them (one per page).

Use the included Python script to automatically process the images and update your letter file:

```bash
# Add one image to a letter
./add_line_art.py letters/your_letter.typ line_art_images/sample1.png

# Add multiple images (one for each page)
./add_line_art.py letters/your_letter.typ line_art_images/sample1.png line_art_images/sample2.png

# Customize the watermark opacity (default is 15%)
./add_line_art.py letters/your_letter.typ line_art_images/sample1.png --opacity 20%

# Customize the image size (default is 12cm)
./add_line_art.py letters/your_letter.typ line_art_images/sample1.png --size 14cm
```

After running the script, compile your letter as usual:
```bash
typst compile letters/your_letter.typ --root .
```
