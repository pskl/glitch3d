# Use Pillow fork with Python3
from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance
import numpy as np
import random

import sys, os, cv2

print("Averaging")
path = os.environ['RENDER_PATH']
files = [path + f for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and os.path.join(path, f).endswith(".png"))]
average_image = ''

for file in files:
    image = np.asarray((Image.open(file)))
    # Extract the frame and convert to image
    average_image = cv2.cvtColor(image,cv2.COLOR_BGR2RGBA)
    average_image = Image.fromarray(average_image)
    old_image = average_image

    # Extract the frame and convert to image
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGBA)
    image = Image.fromarray(image)

    # Calculate the difference between this frame and the last
    diff = ImageChops.difference(image, old_image)

    # Store the image for use in the next itteration
    old_image = image

    # Convert to greyscale and use that as the alpha channel
    gray_image = diff.convert('L')
    diff.putalpha(gray_image)

    #average_image = Image.blend(average_image,image,0.1)
    #average_image = Image.alpha_composite(average_image,diff)
    average_image = ImageChops.lighter(average_image,diff)

    # Darken the image slightly to prevent it getting washed out
    average_image = average_image.point(lambda p: p * 0.9)

    font = random.choice(range(0, 7))
    for i in range(0, 10):
      image = Image.fromarray(cv2.putText(np.asarray(average_image), "PSKL", (random.choice(range(10,200)), random.choice(range(10, 200))), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA))
    image.save(file + "_average.png")

average_image.save(path + "average.png")
