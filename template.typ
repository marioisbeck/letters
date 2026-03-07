#let letter(
  sender: none,
  recipient: none,
  date: datetime.today().display("[month repr:long] [day], [year]"),
  subject: none,
  body
) = {
  set document(title: subject)
  set page(paper: "a4", margin: (x: 3cm, y: 3cm))
  set text(font: "Linux Libertine", size: 11pt)

  // Sender
  if sender != none {
    align(right)[
      #block(width: 50%)[
        #sender
      ]
    ]
  }

  v(1cm)

  // Recipient
  if recipient != none {
    block[
      #recipient
    ]
  }

  v(1cm)

  // Date
  align(right)[
    #date
  ]

  v(1cm)

  // Subject
  if subject != none {
    strong[Subject: #subject]
    v(0.5cm)
  }

  // Body
  body
}
