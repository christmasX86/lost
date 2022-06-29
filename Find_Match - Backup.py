import face_recognition
from flask import Flask, jsonify, request, redirect, render_template
from flask import redirect, url_for, send_from_directory
import numpy as np
from numpy import asarray, save, load
# import os, requests
from werkzeug.utils import secure_filename
import json
from npy_append_array import NpyAppendArray

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
        if 'name' not in request.form:
            return redirect(request.url)
        if 'phone' not in request.form:
            return redirect(request.url)
        if 'email' not in request.form:
            return redirect(request.url)
        if 'country' not in request.form:
            return redirect(request.url)
        if 'lastseen' not in request.form:
            return redirect(request.url)

        file1 = request.files['file1']
        name1 = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        country = request.form['country']
        lastseen = request.form['lastseen']

        if allowed_file(file1.filename):
            # The image file seems valid! Detect faces and return the result.
            # return ''' Hello world'''
            return detect_faces_in_image(file1, name1, country, phone, email, lastseen)

    # If no valid image file was uploaded, show the file upload form:
    return render_template("upload.html")


def detect_faces_in_image(file1, name1, country, phone, email, lastseen):

    # Load the uploaded image file
    img1 = face_recognition.load_image_file(file1)
    unknown_face_encodings1 = face_recognition.face_encodings(img1)

    # Save data to npy file
    save('data.npy', [unknown_face_encodings1[0],
         1, unknown_face_encodings1[0], 2])

    # Load data from npy file
    data = load('data.npy', allow_pickle=True)
    print(data)

    known_face_encodings = data[:: 2]
    ids = data[1:: 2]

    print(ids)
    print(known_face_encodings)
    # append person names to array
    # known_face_names = []
    # known_face_names.append(name1)

    # create database of known faces and their encodings for comparison
    # with unknown faces in the image uploaded by the user
    # known_face_encodings = []
    # known_face_encodings.append(unknown_face_encodings1[0])
    # db = open("img-encoded.txt", "a")
    # for face in known_face_encodings:
    #     db.write(str(face) + "\n")
    # db.close()

    # create database of known faces and their encodings for comparison
    # with unknown faces in the image uploaded by the user
    # db = open("img-encoded.txt", "r")
    # known_face_encodings = []
    # for face in np.loadtxt(db):
    #     known_face_encodings.append(face)
    # db.close()

    # create database for face names
    # db = open("img-names.txt", "a")
    # for name in known_face_names:
    #     db.write(str(name) + "\n")
    # db.close()

    # # create database for reading face names
    # db = open("img-names.txt", "r")
    # known_face_names = []
    # for name in db:
    #     known_face_names.append(name)
    # db.close()

    ###### Copilot Code ######

    # face_found = False
    # is_same = False

    # if len(unknown_face_encodings1) > 0:
    #     face_found = True
    #     # See if the first face in the uploaded image matches the known face of person 1
    #     match_results = face_recognition.compare_faces(
    #         known_face_encodings, unknown_face_encodings1[0])
    #     if match_results[0]:
    #         is_same = True
    #     else:
    #         is_same = False

    # # Return the result as json
    # return jsonify({
    #     'face_found': face_found,
    #     'is_same': is_same
    # })
    ###############

    face_found = False
    is_same = False

    # Compare the faces in the uploaded image to the faces in the database
    # face_distances = face_recognition.face_distance(
    #     known_face_encodings, unknown_face_encodings2[0])
    # If the closest face has a distance less than 0.6, it is a match
    # if face_distances[0] < 0.6:
    #     face_found = True
    #     is_same = True
    # else:
    #     face_found = True
    #     is_same = False

    # # Return the result as json
    # return jsonify({
    #     'face_found': face_found,
    #     'is_same': is_same
    # })

    # Create arrays of known face encodings and their names
    # known_face_encodings = [
    #     unknown_face_encodings1[0],
    #     unknown_face_encodings2[0]
    # ]

    ####### Old comparison 1 on 1  #######
    if len(unknown_face_encodings1) > 0:
        face_found = True
        # See if the first face in the uploaded image matches the known face of person 1
        print("type-----", known_face_encodings[0].shape)
        match_results = face_recognition.compare_faces(
            known_face_encodings[0], unknown_face_encodings1)
        if match_results[0]:
            is_same = True
        else:
            is_same = False
        print("is same:", is_same)
        if not is_same:
            new_id = ids[-1] + 1
            data.append([unknown_face_encodings1, new_id])
            save('data.npy', data)

            # user file
            user_dict = {"id": new_id,
                         "name": name1,
                         "country": country,
                         "phone": phone,
                         "email": email,
                         "lastseen": lastseen}

            with open('users.txt', 'w') as json_file:
                json.dump(user_dict, json_file)
        # elif face_found and is_same:
            # return render_template("notifications.html")

    # Return the result as json
    return jsonify({
        'face_found': face_found,
        'is_same': is_same
    })
    ###### End of Old comparison 1 on 1 ######


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
