#import "@preview/meander:0.4.1"

#let letter(
  line_art_images: (),
  line_art_opacity: 80%,
  line_art_size: 12cm,
  body
) = {
  set page(
    paper: "a4", 
    margin: (x: 3cm, y: 3cm),
  )
  set text(font: "Hoefler Text", size: 11pt)

  if line_art_images != none and line_art_images.len() > 0 {
    meander.reflow({
      import meander: *
      
      // Place each image as an obstacle on consecutive pages
      for (i, img_dict) in line_art_images.enumerate() {
        if i > 0 {
          pagebreak()
        }
        
        let img_height = if "height" in img_dict { img_dict.height } else { line_art_size }
        
        placed(
          bottom + right, 
          dx: 0cm, dy: 0cm, // Keep it within the text area so it's fully printable
          
          // Size is now configurable
          block(width: line_art_size, height: img_height)[
            #place(image(img_dict.path, width: 100%, height: 100%, fit: "contain"))
            // Fade the image to make it a watermark
            #place(rect(width: 100%, height: 100%, fill: rgb(255, 255, 255, 100% - line_art_opacity), stroke: none))
          ]
        )
        container(height: 100%)
      }
      
      // The actual text of the letter
      content[
        #body
      ]
    })
  } else {
    // If no images, just render the body normally
    body
  }
}
