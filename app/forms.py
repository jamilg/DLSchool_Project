from flask_wtf import Form, FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

class UploadForm(FlaskForm):
    file = FileField(id='inputFile1', validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, 'Только файлы jpg, jpeg and png!')])