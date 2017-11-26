# Resize and compress high quality renders to be able to send it around
import os, sys
from PIL import Image

print("Optimizing size of files")

path = os.environ['RENDER_PATH']
files = [path + f for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and os.path.join(path, f).endswith(".png"))]

for img in files:
  print("file being optimized -> " + img)
  image = Image.open(img)
  image = image.resize((2000,2000),Image.ANTIALIAS)
  image.save(img, quality=95)
  image.save(img, optimize=True, quality=65)