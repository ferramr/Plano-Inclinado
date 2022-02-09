# Se deben instalar los modulos
# $ pip install Flask-WTF
# $ pip install email-validator
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ExperimentForm(FlaskForm):
    angulo = IntegerField('Angulo', validators=[DataRequired(), NumberRange(min=5, max=45, message='Angulo fuera de rango: [5 45]')])
    submit = SubmitField('Inicio')