url='http://admin:59Intelligence59@192.168.1.22/Streaming/Channels/102/picture?snapShotImageType=JPEG'

import cv2
import numpy as np
import requests

resp = requests.get(url, stream=True).raw
image = np.asarray(bytearray(resp.read()), dtype="uint8")
image = cv2.imdecode(image, cv2.IMREAD_COLOR)

# for testing
cv2.imshow('image',image)
cv2.waitKey(0)
cv2.destroyAllWindows()