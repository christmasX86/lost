import face_recognition
import os
import numpy as np

dir = "C:/Users/moust/Desktop/proj-test-dep/imgs-add"
file = open("img-encoded-add.txt", 'a')

for img in os.listdir(dir):
    img = os.path.join("imgs-add", img)
    loaded = face_recognition.load_image_file(img)
    encoded = face_recognition.face_encodings(loaded)
    # if face found
    if len(encoded) > 0:
        np.savetxt(file, encoded)

file.close()
