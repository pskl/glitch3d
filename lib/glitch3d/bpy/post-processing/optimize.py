# Resize and compress high quality renders to be able to send it around
# for instance the size limit on twitter is 5 Mb
import os, sys, code
from PIL import Image

print("Optimizing size of files")

res_x = bpy.context.scene.render.resolution_x
res_y = bpy.context.scene.render.resolution_y
files = RENDER_OUTPUT_PATHS
for img in files:
  print("file being optimized -> " + img)
  image = Image.open(img)
  image = image.resize((res_x, res_y), Image.ANTIALIAS)
  image.save(img, optimize=True, quality=65)