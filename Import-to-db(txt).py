import face_recognition
import os
import numpy as np

dir = "C:/Users/moust/Desktop/proj-test-dep/imgs"
file = open("img-encoded.txt", 'w')

for img in os.listdir(dir):
    img = os.path.join("imgs", img)
    loaded = face_recognition.load_image_file(img)
    encoded = face_recognition.face_encodings(loaded)
    np.savetxt(file, encoded)

file.close()
