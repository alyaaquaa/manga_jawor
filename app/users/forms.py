from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email

class UpdateProfileForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image = FileField('Zdjęcie profilowe', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Zapisz zmiany')

