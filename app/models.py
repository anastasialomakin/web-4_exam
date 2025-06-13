from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

equipment_responsible_persons = db.Table('equipment_responsible_persons',
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True),
    db.Column('responsible_person_id', db.Integer, db.ForeignKey('responsible_person.id'), primary_key=True)
)

# пользователь
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='Пользователь')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'Администратор'

    def is_tech(self):
        return self.role == 'Технический специалист'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    equipment = db.relationship('Equipment', backref='category', lazy=True)

class ResponsiblePerson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200), nullable=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    md5_hash = db.Column(db.String(32), unique=True, nullable=False)
    equipment = db.relationship('Equipment', backref='photo', uselist=False, lazy=True)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inventory_number = db.Column(db.String(100), unique=True, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('В эксплуатации', 'На ремонте', 'Списано', name='equipment_status'), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=True)
    
    responsible_persons = db.relationship('ResponsiblePerson', secondary=equipment_responsible_persons, lazy='subquery',
        backref=db.backref('equipment', lazy=True))
    
    service_history = db.relationship('ServiceHistory', backref='equipment', lazy=True, cascade="all, delete-orphan")

class ServiceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False)