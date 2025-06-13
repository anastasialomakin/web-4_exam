from app.models import Equipment, User, ServiceHistory
from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm

bp = Blueprint('main', __name__)

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