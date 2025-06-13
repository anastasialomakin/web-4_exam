from app import db, login 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import date

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

equipment_responsible_persons = db.Table('equipment_responsible_persons',
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True),
    db.Column('responsible_person_id', db.Integer, db.ForeignKey('responsible_person.id'), primary_key=True)
)

# пользователь
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(50), nullable=False, default='Пользователь')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'Администратор'
    
    def is_tech(self):
        return self.role == 'Технический специалист'

    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    equipment = db.relationship('Equipment', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

class ResponsiblePerson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200))

    def __repr__(self):
        return f'<ResponsiblePerson {self.full_name}>'

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    md5_hash = db.Column(db.String(32), unique=True, nullable=False)

    def __repr__(self):
        return f'<Image {self.filename}>'

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inventory_number = db.Column(db.String(100), unique=True, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('В эксплуатации', 'На ремонте', 'Списано', name='equipment_status_enum'), nullable=False, default='В эксплуатации')
    notes = db.Column(db.Text)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=True)

    photo = db.relationship('Image', backref='equipment', uselist=False, lazy=True) 
    responsible_persons = db.relationship('ResponsiblePerson', secondary=equipment_responsible_persons, lazy='subquery',
        backref=db.backref('equipments', lazy=True))

    service_history = db.relationship('ServiceHistory', backref='equipment', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Equipment {self.name} ({self.inventory_number})>'

class ServiceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_date = db.Column(db.Date, nullable=False, default=date.today)
    service_type = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=False)
    
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<ServiceHistory for Equipment {self.equipment_id} on {self.service_date}>'