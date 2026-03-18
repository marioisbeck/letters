#import "@preview/meander:0.4.1"
#set page(paper: "a4", margin: 3cm)
#meander.reflow({
  import meander: *
  placed(bottom + right, dx: 3cm, dy: 3cm, block(width: 5cm, height: 5cm)[#rect(width: 100%, height: 100%, fill: red)])
  container(height: 100%)
  content[
    #lorem(2000)
  ]
})
