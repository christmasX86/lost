import face_recognition
from flask import Flask, jsonify, request, redirect, render_template
from flask import redirect, url_for, send_from_directory
import numpy as np
from numpy import asarray, save, load
# import os, requests
from werkzeug.utils import secure_filename
import json
from npy_append_array import NpyAppendArray
import io
import sqlite3


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}

app = Flask(__name__)


def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


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
            return detect_faces_in_image(file1, name1, country, phone, email, lastseen)

    # If no valid image file was uploaded, show the file upload form:
    return render_template("upload.html")


def detect_faces_in_image(file1, name1, country, phone, email, lastseen):

    # Load the uploaded image file
    img1 = face_recognition.load_image_file(file1)
    unknown_face_encodings1 = face_recognition.face_encodings(img1)

    # Converts np.array to TEXT when inserting
    sqlite3.register_adapter(np.ndarray, adapt_array)
    # Converts TEXT to np.array when selecting
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect("test2.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    # cur.execute('''create table lost (name varchar(255), country varchar(255), phone varchar(255),
    #             email varchar(255), lastseen varchar(255), encoding array)''')
    # cur.execute("delete from test")
    # print(cur.fetchall())

    if len(unknown_face_encodings1) > 0:
        face_found = True
        is_same = False
        i = 0
        for row in cur.execute("select encoding from lost"):
            match_results = face_recognition.compare_faces(
                row, unknown_face_encodings1[0])
            i += 1
            if match_results[0]:
                is_same = True
                break
        if is_same == False:  # Face not found
            cur.execute("insert into lost values (?, ?, ? , ? , ? ,?)", (name1, country,
                        phone, email, lastseen, unknown_face_encodings1[0],))
            con.commit()
            file1.save("/images" + name1 + ".jpg")
            i = 0
            # con.close()
        else:  # Face Found
            pass
            # con.close()
            # return render_template("upload.html", message="Face already exists")

    # Return the result as json
    if i != 0:  # Face Found
        data = cur.execute(
            "select name, country, phone, email, lastseen from lost where rowid = (?)", (i,))
        return jsonify(data.fetchall())
    else:  # Face not found
        return jsonify({
            'face_found': face_found,
            'is_same': is_same
        })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
