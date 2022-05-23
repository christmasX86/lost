from attr import field
from pytest import skip
import face_recognition
from flask import Flask, jsonify, request, redirect
import numpy as np

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file1' not in request.files:
            return redirect(request.url)

        file1 = request.files['file1']

        if file1.filename == '':
            return redirect(request.url)

        if file1 and allowed_file(file1.filename):
            return detect_faces_in_image(file1)

    return '''
    <!doctype html>
    <title>Face matching</title>
    <h1>Face Matching POC</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file1">
      <!-- <input type="file" name="file2"> -->
      <input type="submit" value="Upload">
    </form>
    '''


def detect_faces_in_image(file1):

    img1 = face_recognition.load_image_file(file1)
    unknown_face_encodings1 = face_recognition.face_encodings(img1)

    face_found = False
    is_same = False

    db = open("img-encoded.txt", "r")

    if len(unknown_face_encodings1) > 0:
        face_found = True
        for face in np.loadtxt(db):
            match_results = face_recognition.compare_faces(
                [unknown_face_encodings1[0]], face)
            if match_results[0]:
                is_same = True
                break

    # Return the result as json
    result = {
        "face_found_in_image": face_found,
        "is pictures is the same": is_same
    }
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
