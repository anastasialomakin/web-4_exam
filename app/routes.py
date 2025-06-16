from app.models import Equipment, User, ServiceHistory, Category, Image
from flask import render_template, Blueprint, redirect, url_for, flash, request, abort, current_app, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, EquipmentForm
from functools import wraps
from app import db 
from werkzeug.utils import secure_filename
import os
import hashlib

bp = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@bp.route('/index')
def index():
    all_equipment = Equipment.query.order_by(Equipment.purchase_date.desc()).all()
    return render_template('index.html', title='Главная', equipment_list=all_equipment)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
            return redirect(url_for('main.login'))

        login_user(user, remember=form.remember_me.data)
        
        flash('Вход выполнен успешно!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('login.html', title='Вход', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно вышли из системы.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/equipment/<int:id>')
@login_required 
def equipment_detail(id):
    equipment_item = Equipment.query.get_or_404(id)

    service_history = equipment_item.service_history.order_by(ServiceHistory.service_date.desc()).all()

    return render_template(
        'equipment_detail.html', 
        title=f'Детали: {equipment_item.name}', 
        equipment=equipment_item,
        history=service_history 
    )

def save_picture(form_picture):
    md5 = hashlib.md5(form_picture.read()).hexdigest()
    form_picture.seek(0)
    image = Image.query.filter_by(md5_hash=md5).first()
    if image:
        return image
    file_ext = os.path.splitext(form_picture.filename)[1]
    filename = md5 + file_ext

    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    form_picture.save(picture_path)
    
    new_image = Image(
        filename=filename,
        mime_type=form_picture.mimetype,
        md5_hash=md5
    )
    db.session.add(new_image)
    db.session.commit() 
    
    return new_image

@bp.route('/equipment/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_equipment():
    form = EquipmentForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    
    if form.validate_on_submit():
        image_id = None
        if form.photo.data:
            try:
                image_obj = save_picture(form.photo.data)
                image_id = image_obj.id
            except Exception as e:
                flash(f'При сохранении файла возникла ошибка: {e}', 'danger')
                db.session.rollback()
                return render_template('equipment_form.html', title='Добавление оборудования', form=form)
        
        new_equipment = Equipment(
            name=form.name.data,
            inventory_number=form.inventory_number.data,
            category_id=form.category.data,
            purchase_date=form.purchase_date.data,
            cost=form.cost.data,
            status=form.status.data,
            notes=form.notes.data,
            responsible_persons=form.responsible_persons.data,
            image_id=image_id 
        )
        db.session.add(new_equipment)
        db.session.commit()
        
        flash('Новое оборудование успешно добавлено!', 'success')
        return redirect(url_for('main.equipment_detail', id=new_equipment.id))
        
    return render_template('equipment_form.html', title='Добавление оборудования', form=form)

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required 
def edit_equipment(id):
    equipment_item = Equipment.query.get_or_404(id)
    form = EquipmentForm(original_inventory_number=equipment_item.inventory_number)
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]

    if form.validate_on_submit():
        equipment_item.name = form.name.data
        equipment_item.inventory_number = form.inventory_number.data
        equipment_item.category_id = form.category.data
        equipment_item.purchase_date = form.purchase_date.data
        equipment_item.cost = form.cost.data
        equipment_item.status = form.status.data
        equipment_item.notes = form.notes.data
        equipment_item.responsible_persons = form.responsible_persons.data

        if form.photo.data:
            try:
                image_obj = save_picture(form.photo.data)
                equipment_item.image_id = image_obj.id
            except Exception as e:
                flash(f'При сохранении файла возникла ошибка: {e}', 'danger')
                db.session.rollback()
                return render_template('equipment_form.html', title='Редактирование оборудования', form=form, equipment=equipment_item)

        db.session.commit()
        flash('Данные об оборудовании успешно обновлены!', 'success')
        return redirect(url_for('main.equipment_detail', id=equipment_item.id))

    elif request.method == 'GET':
        form.name.data = equipment_item.name
        form.inventory_number.data = equipment_item.inventory_number
        form.category.data = equipment_item.category_id
        form.purchase_date.data = equipment_item.purchase_date
        form.cost.data = equipment_item.cost
        form.status.data = equipment_item.status
        form.notes.data = equipment_item.notes
        form.responsible_persons.data = equipment_item.responsible_persons

    return render_template('equipment_form.html', title='Редактирование оборудования', form=form, equipment=equipment_item)

@bp.route('/equipment/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_equipment(id):
    equipment_to_delete = Equipment.query.get_or_404(id)
    image_to_check = equipment_to_delete.photo
    db.session.delete(equipment_to_delete)
    
    if image_to_check:
        other_equipment_with_same_image = Equipment.query.filter_by(image_id=image_to_check.id).first()
        if not other_equipment_with_same_image:
            try:
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_to_check.filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                db.session.delete(image_to_check)
            except Exception as e:
                flash(f'Ошибка при удалении файла изображения: {e}', 'danger')
                db.session.rollback()
                return redirect(url_for('main.index'))

    db.session.commit()
    flash('Оборудование успешно удалено.', 'success')
    return redirect(url_for('main.index'))