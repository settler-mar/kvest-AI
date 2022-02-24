from CursorClass import HandCursor, MouseCursor

import cv2

cursor = HandCursor()
while 1:
    blank_image = cv2.imread("bg.jpg", -1)  # np.zeros((720, 1280, 3), np.uint8)
    cursor.update(blank_image, True)
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.imshow("Image", blank_image)
    cv2.waitKey(1)
