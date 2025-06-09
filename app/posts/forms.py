from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import InputRequired, DataRequired
from wtforms.widgets import ListWidget, CheckboxInput
from flask_wtf.file import FileField, FileAllowed
from wtforms import ValidationError
from wtforms.validators import URL



class PostForm(FlaskForm):
    title = StringField('Tytuł', validators=[InputRequired()])
    content = TextAreaField('Treść', validators=[InputRequired()])

    genres = SelectMultipleField(
        'Wybierz gatunek',
        choices=[
            ('akcja', 'akcja'),
            ('biografia', 'biografia'),
            ('biznes', 'biznes'),
            ('dojinshi', 'dojinshi'),
            ('dramat', 'dramat'),
            ('fantasy', 'fantasy'),
            ('horror', 'horror'),
            ('historia', 'historia'),
            ('josei', 'josei'),
            ('kodomo', 'kodomo'),
            ('komedia', 'komedia'),
            ('magical girls', 'magical girls'),
            ('mecha', 'mecha'),
            ('musical', 'musical'),
            ('nadprzyrodzone', 'nadprzyrodzone'),
            ('parodia', 'parodia'),
            ('psychologia', 'psychologia'),
            ('przygoda', 'przygoda'),
            ('romans', 'romans'),
            ('seinen', 'seinen'),
            ('shōnen', 'shōnen'),
            ('shōjo', 'shōjo'),
            ('sport', 'sport'),
            ('science fiction', 'science fiction'),
            ('tajemnica', 'tajemnica'),
            ('thriller', 'thriller'),
            ('tragedia', 'tragedia'),
            ('wojna', 'wojna'),
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False),
        coerce=str
    )

    image = FileField('Dodaj zdjęcie (opcjonalnie)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Tylko pliki obrazów!')
    ])

    image_url = StringField('Link do źródła obrazka (obowiązkowy przy dodaniu obrazka)', validators=[
        URL(message='Podaj poprawny URL.')  # Dodany walidator formatu URL
    ])

    tags = StringField('Stwórz tagi (oddzielone przecinkami)')
    submit = SubmitField('Zapisz')

    def validate_genres(self, field):
        if not field.data:
            raise ValidationError('Wybierz przynajmniej jeden gatunek.')
        if len(field.data) > 5:
            raise ValidationError('Możesz wybrać maksymalnie 5 gatunków.')


def validate(self, extra_validators=None):
    if not super().validate(extra_validators=extra_validators):
        return False

    if self.image.data and not self.image_url.data:
        self.image_url.errors.append('Podanie linku do źródła obrazka jest obowiązkowe.')
        return False

    return True



class CommentForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Dodaj komentarz')

