from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField, DateField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed 
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

from app.models import Equipment, ResponsiblePerson

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message="Пожалуйста, введите логин.")])
    password = PasswordField('Пароль', validators=[DataRequired(message="Пожалуйста, введите пароль.")])

    remember_me = BooleanField('Запомнить меня')

    submit = SubmitField('Войти')

def get_responsible_person_label(person):
    return person.full_name

class EquipmentForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(min=3, max=200)])
    inventory_number = StringField('Инвентарный номер', validators=[DataRequired(), Length(min=1, max=100)])
    category = SelectField('Категория', coerce=int, validators=[DataRequired()])
    purchase_date = DateField('Дата покупки', format='%Y-%m-%d', validators=[DataRequired()])
    cost = DecimalField('Стоимость', validators=[DataRequired()])
    status = RadioField('Статус', choices=[
        ('В эксплуатации', 'В эксплуатации'),
        ('На ремонте', 'На ремонте'),
        ('Списано', 'Списано')
    ], validators=[DataRequired()])
    notes = TextAreaField('Примечание')
    responsible_persons = QuerySelectMultipleField(
        'Ответственные лица',
        query_factory=lambda: ResponsiblePerson.query.order_by('full_name'),
        get_label=get_responsible_person_label,
        allow_blank=True,
    )
    
    photo = FileField('Фотография', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Разрешены только изображения!')
    ])
    submit = SubmitField('Сохранить')

    def __init__(self, original_inventory_number=None, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)
        self.original_inventory_number = original_inventory_number

    def validate_inventory_number(self, inventory_number):
        if inventory_number.data == self.original_inventory_number:
            return
        
        equipment = Equipment.query.filter_by(inventory_number=inventory_number.data).first()
        if equipment:
            raise ValidationError('Оборудование с таким инвентарным номером уже существует.')