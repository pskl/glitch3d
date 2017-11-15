# Make a mosaic with images
import sys
import os
from PIL import Image

print("Mosaicing")

RES_X = 5000
RES_Y = 5000
path = './renders/'
files = [path + f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
images = map(Image.open, files)
widths, heights = zip(*(i.size for i in images))

total_width = images[0].size[0] * 4
total_height = total_width

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

res.save('./mosaic.png')