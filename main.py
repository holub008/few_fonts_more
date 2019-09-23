import cv2
import numpy as np
# heavily borrowed from http://cvisiondemy.com/extract-roi-from-image-with-python-and-opencv/

import pytesseract

#################
# detect regions of interest (single characters) using simple binarization & contouring, since the white text is easy to
# threshold on a relatively dark background.
#################

credit_id = 1
filename = "./images/%d.png" % (credit_id,)
image = cv2.imread(filename)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
# TODO, even a cv2.waitKey results in cruddy behavior in pycharm
# cv2.imshow('binarized_image', thresh)

kernel = np.ones((10, 1), np.uint8)
img_dilation = cv2.dilate(thresh, kernel, iterations=1)

ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

for i, ctr in enumerate(sorted_ctrs):
    # Get bounding box
    x, y, w, h = cv2.boundingRect(ctr)

    # Getting ROI
    roi = image[y:y + h, x:x + w]
    binary_roi = img_dilation[y:y + h, x:x + w]
    cv2.imwrite("./images/raw_characters/%d_%d.jpg" % (credit_id, i), roi)

    content = pytesseract.image_to_string(binary_roi, config="-l eng --psm 10")
    print(content)

    # this can provide a nice visual, when displaying all ROIs
    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# cv2.imshow('all_rois', image)
cv2.waitKey()


##################
# OCR the text in each character image
##################

# psm = page segmentation mode = 10 implies single character
