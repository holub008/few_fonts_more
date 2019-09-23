import cv2
import numpy as np

#################
# detect regions of interest (single characters) using simple binarization & contouring, since the white text is easy to
# threshold on a relatively dark background.
# also perform some preprocessing (borders + erosion) for tesseract
#################

n_images = 19
for credit_id in range(1, n_images + 1):
    filename = "./images/%d.png" % (credit_id,)
    image = cv2.imread(filename)
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
        eroded_image = cv2.bitwise_not(cv2.erode(bordered_character, kernel, iterations=1))

        cv2.imwrite("./images/extracted_characters/eroded_%d_%d.jpg" % (credit_id, i), eroded_image)
        cv2.imwrite("./images/extracted_characters/binary_%d_%d.jpg" % (credit_id, i), binary_roi)
