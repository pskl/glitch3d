# Use Pillow fork with Python3
from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance
import numpy as np
import random
import sys, os, cv2, code, uuid

print("Averaging and signing 💁🏻‍♀️")
path = os.environ['RENDER_PATH']
files = sys.argv[1:]
print("Will average the following files: " + str(files))
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

    # possibly invert colors
    if random.randint(0,1) == 1:
      image = Image.fromarray(cv2.bitwise_not(np.asarray(current_image)))

# add signature
font = random.choice(range(0, 7))
average_image = Image.fromarray(cv2.putText(np.asarray(average_image), random.choice(["PSKL"]), (random.choice(range(0, average_image.size[0])), random.choice(range(0, average_image.size[1]))), font, random.uniform(0.8, 3), random.choice([(255, 255, 255), (0,0,0)]), random.choice(range(1, 3)), random.choice(range(1,8))))

average_image.save(path + "average_" + str(uuid.uuid1()) + ".png")