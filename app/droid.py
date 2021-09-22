import urllib.request
import cv2
import numpy as np

url='http://192.168.1.105:8080/shot.jpg'

    # I'm guessing this would output the html source code ?
    # print(s)
# https://thecodacus.com/blog/2017/07/31/ip-webcam-opencv-wireless-camera/
while True:
    with urllib.request.urlopen(url) as imgResp:
        # s = url.read()
    # imgResp=urllib.urlopen(url)
        imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgNp,-1)

    # all the opencv processing is done here
        cv2.imshow('test',img)
        if ord('q')==cv2.waitKey(10):
            exit(0)