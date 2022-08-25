import cv2
import numpy as np
import os
from deepface import DeepFace
from PIL import Image
from django.conf import settings


def get_image():
    cam = cv2.VideoCapture(0)

    result, image = cam.read()

    if result:
        # cv2.imshow("Press any key to close", image)
        try:
            cv2.imwrite('user.jpg', image)
        except:
            print('didn\'t go')
        # cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        return None


def create_image(photo):
    with open('user.png', 'wb+') as destination:
        for chunk in photo.chunks():
            destination.write(chunk)
    return 'user.png'

def detectFace(photo):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    img = cv2.imread(photo)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    if len(face) == 1:
        return True
    else:
        return False


def get_verification(photo):
    get_image()
    try:
        res = detectFace('./user.jpg')
        if res:
            compare = DeepFace.verify('./user.jpg', photo, model_name="VGG-Face")['verified']
            return compare
        else:
            return False
    except:
        return False


