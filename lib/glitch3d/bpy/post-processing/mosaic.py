# Make a mosaic with images
import os, sys
from PIL import Image

print("Mosaicing")
path = os.environ['RENDER_PATH']
files = [path + f for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and os.path.join(path, f).endswith(".png"))]
images = map(Image.open, files)
widths, heights = zip(*(i.size for i in images))

total_width = images[0].size[0] * 4
total_height = images[0].size[1] * 4

res = Image.new('RGB', (total_height,total_width))
print('stitching ' + str(len(files)) + ' images')

x_offset = 0
y_offset = 0
for file in files:
    print(file)
    image = Image.open(file)
    print(image.size)
    res.paste(image, (x_offset, y_offset))
    x_offset += image.size[0]
    if x_offset > total_width:
      print('reset')
      y_offset += image.size[1]
      x_offset = 0

res.save(path + 'mosaic.png')