# Use Pillow fork with Python3
from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance
import numpy as np
import random
import sys, os, cv2

print("Averaging 💁🏻‍♀️")
path = os.environ['RENDER_PATH']
files = [path + f for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and os.path.join(path, f).endswith(".png"))]

average_image = None
old_image = None

for file in files:
    current_image = Image.open(file)
    # calculate the difference between this frame and the last
    diff = ImageChops.difference(current_image, old_image if old_image else current_image)
    old_image = current_image
    average_image = current_image

    # convert to greyscale and use that as the alpha channel
    gray_image = diff.convert('L')
    diff.putalpha(gray_image)

    average_image = Image.blend(average_image, current_image, 0.1)
    average_image = Image.alpha_composite(average_image, diff)
    average_image = ImageChops.lighter(average_image, diff)

    # darken the image slightly to prevent it getting washed out
    average_image = average_image.point(lambda p: p * 0.9)

    # # possibly invert colors
    if random.randint(0,1) == 1:
      image = Image.fromarray(cv2.bitwise_not(np.asarray(current_image)))

font = random.choice(range(0, 7))
for i in range(0,5):
  average_image = Image.fromarray(cv2.putText(np.asarray(average_image), "PSKL", (random.choice(range(20,300)), random.choice(range(20, 300))), font, random.uniform(0.8, 3), (255, 255, 255), 1, cv2.LINE_AA))
average_image.save(path + "average.png") # save final result