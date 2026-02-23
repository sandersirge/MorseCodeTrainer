# Application Icons

Briefcase requires icons in multiple formats and sizes. Place your icons here with the base name `morsetrainer`.

## Required Files

### Windows (.ico)

- `morsetrainer.ico` - Multi-resolution ICO file (16x16, 32x32, 48x48, 256x256)

### macOS (.icns)

- `morsetrainer.icns` - Apple icon format (16x16 to 1024x1024 at 1x and 2x)

### Linux/General (.png)

- `morsetrainer-16.png` - 16x16 pixels
- `morsetrainer-32.png` - 32x32 pixels
- `morsetrainer-64.png` - 64x64 pixels
- `morsetrainer-128.png` - 128x128 pixels
- `morsetrainer-256.png` - 256x256 pixels
- `morsetrainer-512.png` - 512x512 pixels

## Generating Icons

You can use tools like:

- **ImageMagick**: `convert icon.png -define icon:auto-resize=256,128,64,48,32,16 morsetrainer.ico`
- **iconutil** (macOS): Create .icns from iconset folder
- **Online converters**: ConvertICO, CloudConvert, etc.

## Placeholder

Until you have proper icons, Briefcase will use a default icon.
If builds fail due to missing icons, create placeholder PNG files:

```bash
# Create a simple placeholder (requires ImageMagick)
convert -size 256x256 xc:navy -fill white -gravity center -pointsize 72 -annotate 0 "M" morsetrainer-256.png
```
