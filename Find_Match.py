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
import os
import msvcrt


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}

app = Flask(__name__)
app.config["IMAGE_UPLOADS_LOST"] = "C:\\Users\\moust\\Desktop\\proj-test-dep\\static\\imgs\\lost"
app.config["IMAGE_UPLOADS_FOUND"] = "C:\\Users\\moust\\Desktop\\proj-test-dep\\static\\imgs\\found"


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
        if 'findMatch' in request.form and request.form['findMatch'] == "Find Match":

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
            lastseendate = request.form['lastseendate']

            if allowed_file(file1.filename):
                # The image file seems valid! Detect faces and return the result.
                return detect_faces_in_image(file1, name1, country, phone, email, lastseen, lastseendate)

        elif 'makepost' in request.form and request.form['makepost'] == "post":

            if 'file2' not in request.files:
                return redirect(request.url)
            if 'name2' not in request.form:
                return redirect(request.url)
            if 'phone2' not in request.form:
                return redirect(request.url)
            if 'email2' not in request.form:
                return redirect(request.url)
            if 'country2' not in request.form:
                return redirect(request.url)
            if 'lastseen2' not in request.form:
                return redirect(request.url)
            if 'lastseendate2' not in request.form:
                return redirect(request.url)
            if 'description' not in request.form:
                return redirect(request.url)
            if 'age' not in request.form:
                return redirect(request.url)

            file = request.files['file2']
            description = request.form['description']
            age = request.form['age']
            name = request.form['name2']
            phone = request.form['phone2']
            email = request.form['email2']
            country = request.form['country2']
            lastseen = request.form['lastseen2']
            lastseendate = request.form['lastseendate2']

            if allowed_file(file.filename):
                # The image file seems valid! Detect faces and return the result.
                return make_post(file, name, country, phone, email, lastseen, lastseendate, description, age)

    # If no valid image file was uploaded, show the file upload form:
    return render_template("upload.html")


def make_post(file, name, country, phone, email, lastseen, lastseendate, description, age):

    filename = secure_filename(file.filename)
    imageFilename = os.path.join("imgs\\lost", filename)
    file.save(os.path.join(app.config['IMAGE_UPLOADS_LOST'], filename))
    # Load the uploaded image file
    img = face_recognition.load_image_file(file)
    known_face_encodings1 = face_recognition.face_encodings(img)

    # Converts np.array to TEXT when inserting
    sqlite3.register_adapter(np.ndarray, adapt_array)
    # Converts TEXT to np.array when selecting
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect("test2.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute('delete from found')
    con.commit()
    # con.close()

    if len(known_face_encodings1) > 0:
        face_found = True
        is_same = False
        i = 0
        rows = cur.execute("select * from found")  # .fetchall()
        for row in rows:
            # print(row[7].shape)
            # print(known_face_encodings1[0].shape)
            match_results = face_recognition.compare_faces(
                row[7], known_face_encodings1)
            i += 1
            if match_results[0]:  # Face found
                is_same = True
                # notify user
                break
        if is_same == False:  # Face not found
            i = 0
            rows = cur.execute("select * from lost")
            for row in rows:
                match_results = face_recognition.compare_faces(
                    row[9], known_face_encodings1)
                if match_results[0]:
                    is_same = True
                    break
            if is_same == False:
                cur.execute("insert into lost values (?, ?, ? , ? , ? ,?, ?, ?, ?, ?)", (name, country,
                                                                                         phone, description, age, email, lastseen, imageFilename, lastseendate, known_face_encodings1[0],))
                con.commit()
                # con.close()

        # else:  # Face Found
            # pass
            # con.close()
            # return render_template("upload.html", message="Face already exists")

    # Return the result as json
    if i != 0:  # Face Found
        data = cur.execute(
            "select name, country, phone, email, lastseen, filename from found where rowid = (?)", (i,))
        return render_template("light_user_grid2.html", data=data.fetchall())
        # return jsonify(data.fetchall())

    else:  # Face not found
        return redirect('lost')
        # return jsonify({
        #     'face_found': face_found,
        #     'is_same': is_same
        # })
    # return jsonify({
    #     'face_found': True,
    #     'is_same': True
    # })


def detect_faces_in_image(file1, name1, country, phone, email, lastseen, lastseendate):
    filename = secure_filename(file1.filename)
    imageFilename = os.path.join("imgs\\found", filename)
    file1.save(os.path.join(app.config['IMAGE_UPLOADS_FOUND'], filename))
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
    # email varchar(255), lastseen varchar(255), filename varchar(255), encoding array)''')
    # cur.execute("delete from lost where rowid = (?)", (5,))
    # cur.execute("delete from lost where lastseen = (?)", ('gleem',))
    # cur.execute("drop table lost")
    # cur.execute("drop table found")
    # cur.execute('''create table lost (name varchar(255), country varchar(255), phone varchar(255), description varchar(255), age integer,
    # email varchar(255), lastseen varchar(255), filename varchar(255), lostDate date, encoding array)''')
    # cur.execute('''create table found (name varchar(255), country varchar(255), phone varchar(255),
    # email varchar(255), lastseen varchar(255), filename varchar(255), foundDate date, encoding array)''')
    # con.commit()
    if len(unknown_face_encodings1) > 0:
        face_found = True
        is_same = False
        i = 0
        rows = cur.execute("select * from lost")
        for row in rows:
            print(i)
            # print(row[9].shape)
            match_results = face_recognition.compare_faces(
                row[9], unknown_face_encodings1)
            i += 1
            if match_results[0]:
                is_same = True
                # notify user
                break
        if is_same == False:  # Face not found
            i = 0
            rows = cur.execute("select * from found")
            for row in rows:
                match_results = face_recognition.compare_faces(
                    row[7], unknown_face_encodings1)
                if match_results[0]:
                    is_same = True
                    # notify user
                    break
            if is_same == False:
                cur.execute("insert into found values (?, ?, ? , ? , ? ,?, ?, ?)", (name1, country,
                            phone, email, lastseen,  imageFilename, lastseendate, unknown_face_encodings1[0],))
                con.commit()

            # file1.save(secure_filename(file1.filename))
            # fn = os.path.basename(file1.filename)

            # # open read and write the file into the server
            # open(fn, 'wb').write(file1.file.read())
            # file1.save(os.path.join(app.config["IMAGE_UPLOADS"], file1.filename))
            # filename = secure_filename(file1.filename)
            # file1.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
            # file1.save(secure_filename(file1.filename))         # save el file bs mish sha8ala byde 0 fl size
            # con.close()
        # else:  # Face Found
            # pass
            # con.close()
            # return render_template("upload.html", message="Face already exists")

    # Return the result as json
    if i != 0:  # Face Found
        data = cur.execute(
            "select name, country, phone, email, lastseen, filename from lost where rowid = (?)", (i,))
        # return jsonify(data.fetchall())
        return render_template("light_user_grid.html", data=data.fetchall())
        # return redirect('found')
    else:  # Face not found
        return redirect('found')
        # return render_template("light_user_grid.html", data=data.fetchall())
        # return jsonify({
        #     'face_found': face_found,
        #     'is_same': is_same
        # })
    # return jsonify({
    #     'face_found': True,
    #     'is_same': True
    # })

# hanselect el parameter el me7tagenha mel DB 3ashan tet7at fel card


@app.route('/found', methods=['GET', 'POST'])
def postslost():
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect("test2.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    data = cur.execute(
        "select name, country, phone, email, lastseen, filename from found ")
    con.commit()
    return render_template("light_user_grid2.html", data=data.fetchall())


@app.route('/lost', methods=['GET', 'POST'])
def posts():
    sqlite3.register_converter("array", convert_array)
    con = sqlite3.connect("test2.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    data = cur.execute(
        "select name, country, phone, email, lastseen, filename from lost ")
    con.commit()

    return render_template("light_user_grid.html", data=data.fetchall())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
