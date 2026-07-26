import fs from 'fs'

const pngPath = 'public/TK-VIBES_LOGO.png'
const png = fs.readFileSync(pngPath)
const b64 = png.toString('base64')
const w = 572
const h = 436

const full = [
  `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${w} ${h}" role="img" aria-label="TK Vibes Digital Agency">`,
  '  <title>TK Vibes Digital Agency</title>',
  `  <image width="${w}" height="${h}" href="data:image/png;base64,${b64}"/>`,
  '</svg>',
].join('\n')

fs.writeFileSync('public/tk-vibes-logo.svg', full)

const mx = 70
const my = 8
const mw = 432
const mh = 210

const mark = [
  `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="${mx} ${my} ${mw} ${mh}" role="img" aria-label="TK Vibes">`,
  '  <title>TK Vibes</title>',
  `  <image x="0" y="0" width="${w}" height="${h}" href="data:image/png;base64,${b64}"/>`,
  '</svg>',
].join('\n')

fs.writeFileSync('public/tk-vibes-mark.svg', mark)

console.log('Created public/tk-vibes-logo.svg and public/tk-vibes-mark.svg')
