# Resize and compress high quality renders to be able to send it around
import os, sys, code
from PIL import Image

print("Optimizing size of files")

path = os.environ['RENDER_PATH']

res_x = int(sys.argv[1])
res_y = int(sys.argv[2])
files = sys.argv[3:]

for img in files:
  print("file being optimized -> " + img)
  image = Image.open(img)
  image = image.resize((res_x, res_y), Image.ANTIALIAS)
  image.save(img, optimize=True, quality=65)