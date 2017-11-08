import cv2

for f in os.listdir("./renders/"):
    img = cv2.imread("./renders/%s" %f);
    dst = cv2.fastNlMeansDenoisingColored(img)
    cv2.imwrite('res/%s' %f, dst);