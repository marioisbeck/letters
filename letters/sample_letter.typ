#import "template.typ": letter

#show: letter.with(
  sender: [
    *Mario*\
    123 Main Street\
    City, Country 12345\
    mario@example.com
  ],
  recipient: [
    *John Doe*\
    456 Elm Street\
    Other City, Country 67890
  ],
  subject: "A Letter with Line Art"
)

Dear John,

I am writing to you today to share this beautiful line art illustration that I recently created.

#align(center)[
  // Ensure you have an image in line_art_images before uncommenting
  // #image("line_art_images/sample.png", width: 60%)
]

I hope you enjoy it as much as I do.

Sincerely,

Mario
