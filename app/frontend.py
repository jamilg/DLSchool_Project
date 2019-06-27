from flask import Blueprint, render_template, flash, redirect, url_for, request, send_from_directory
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator

from werkzeug.utils import secure_filename

from app.forms import UploadForm
from app.nav import nav

from app.object_detection import ObjectDetector

import os

UPLOAD_FOLDER = 'app/static/uploads'

frontend = Blueprint('frontend', __name__)


nav.register_element('frontend_top', Navbar(
    View('Object detecttion Demo', '.index'),
    View('Домой', '.index'),
    View('Загрузить изображение', '.upload_file'),
    View('Посмотреть загруженные', '.gallery'),
    View('О проекте', '.about'),
    Text('Используется Flask-Bootstrap {}'.format(FLASK_BOOTSTRAP_VERSION)), ))


@frontend.route('/')
def index():
    return render_template('index.html')

@frontend.route('/about')
def about():
    return render_template('about.html')

@frontend.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()

    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save(os.path.join(UPLOAD_FOLDER, filename))

        #return redirect(url_for('frontend.uploaded_file', filename=filename))
        return redirect(url_for('frontend.detect', filename=filename))

    return render_template('upload.html', form=form)

@frontend.route('/gallery')
def gallery():
    pics = os.listdir(UPLOAD_FOLDER)
    pics = [ 'uploads/' + file for file in pics]
    return render_template('gallery.html', pics = pics)

@frontend.route('/uploads/<path:filename>')
def detect(filename):
    detector = ObjectDetector()
    imgsrc = detector.detect(filename)
    return render_template("detection.html", imgsrc=imgsrc)