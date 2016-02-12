import os
from Lodel import app
from flask import render_template, request, redirect, url_for
from werkzeug import secure_filename

@app.route("/")
def index():
    return render_template('dashboard/index.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_UPLOAD_FILE_EXTENSIONS']


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['myfile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))

    return render_template('files/upload.html')
