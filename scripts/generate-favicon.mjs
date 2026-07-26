import fs from 'fs'
import sharp from 'sharp'
import toIco from 'to-ico'

const source = 'public/TK-VIBES_LOGO.png'
const markCrop = { left: 70, top: 8, width: 432, height: 210 }
const bg = { r: 9, g: 16, b: 28, alpha: 1 }

async function createSquareMark(size) {
  return sharp(source)
    .extract(markCrop)
    .resize(size, size, { fit: 'contain', background: bg })
    .png()
    .toBuffer()
}

const mark512 = await createSquareMark(512)
const icon32 = await sharp(mark512).resize(32, 32).png().toBuffer()
const icon48 = await sharp(mark512).resize(48, 48).png().toBuffer()
const icon16 = await sharp(mark512).resize(16, 16).png().toBuffer()
const apple180 = await sharp(mark512).resize(180, 180).png().toBuffer()

fs.mkdirSync('src/app', { recursive: true })
fs.writeFileSync('src/app/favicon.ico', await toIco([icon16, icon32, icon48]))
fs.writeFileSync('src/app/icon.png', icon32)
fs.writeFileSync('src/app/apple-icon.png', apple180)

console.log('Generated src/app/favicon.ico, icon.png, and apple-icon.png')
