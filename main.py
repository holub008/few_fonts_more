import cv2
import numpy as np


#################
# manually rotate images that aren't 90 degree aligned
#################

rotations = [
    (10, -10),
    (12, 15)
]
completed_rotations = {}
for credit_id, degrees in rotations:
    image = cv2.imread("./images/%d.png" % (credit_id,))
    rows, cols, _ = image.shape

    transform = cv2.getRotationMatrix2D((cols / 2, rows / 2), degrees, 1)
    completed_rotations[credit_id] = cv2.warpAffine(image, transform, (cols, rows))


#################
# detect regions of interest (single characters) using simple binarization & contouring, since the white text is easy to
# threshold on a relatively dark background.
# also perform some preprocessing (borders + erosion) for tesseract
#################

n_images = 19
for credit_id in range(1, n_images + 1):
    if not credit_id in completed_rotations:
        filename = "./images/%d.png" % (credit_id,)
        image = cv2.imread(filename)
    else:
        image = completed_rotations[credit_id]

    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(grey_image, 127, 255, cv2.THRESH_BINARY)

    ctrs, hier = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

    for i, ctr in enumerate(sorted_ctrs):
        # getting the ROI
        x, y, w, h = cv2.boundingRect(ctr)
        binary_roi = thresh[y:y + h, x:x + w]

        border_size = 100
        bordered_character = border = cv2.copyMakeBorder(
            binary_roi,
            top=border_size,
            bottom=border_size,
            left=border_size,
            right=border_size,
            borderType=cv2.BORDER_CONSTANT,
            value=[0, 0, 0]
        )

        # since the font letters are so thick, erode to something the model likely understands better
        kernel = np.ones((10, 10), np.uint8)
        # tesseract is also extremely sensitive to background color, it seems, so we flip colors
        preprocessed_image = cv2.bitwise_not(cv2.erode(bordered_character, kernel, iterations=1))

        cv2.imwrite("./images/extracted_characters/tesseract_%d_%d.jpg" % (credit_id, i), preprocessed_image)
        # write the original image mask so that we can recover the font after OCR
        cv2.imwrite("./images/extracted_characters/mask_%d_%d.jpg" % (credit_id, i), binary_roi)
