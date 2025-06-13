from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message="Пожалуйста, введите логин.")])
    password = PasswordField('Пароль', validators=[DataRequired(message="Пожалуйста, введите пароль.")])

    remember_me = BooleanField('Запомнить меня')

    submit = SubmitField('Войти')