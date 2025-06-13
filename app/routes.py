from app.models import Equipment, User
from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
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
    
    # validate_on_submit() вернет True, если форма была отправлена (метод POST)
    # и все валидаторы прошли успешно
    if form.validate_on_submit():
        # Ищем пользователя в базе данных по имени, которое ввели в форме
        user = User.query.filter_by(username=form.username.data).first()
        
        # Проверяем, найден ли пользователь и правильный ли у него пароль
        if user is None or not user.check_password(form.password.data):
            # Если нет - показываем сообщение об ошибке
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
            # и снова рендерим страницу входа
            return redirect(url_for('main.login'))
        
        # Если все хорошо, "запоминаем" пользователя в сессии
        # form.remember_me.data будет True или False в зависимости от чекбокса
        login_user(user, remember=form.remember_me.data)
        
        # Перенаправляем пользователя на главную страницу
        flash('Вход выполнен успешно!', 'success')
        return redirect(url_for('main.index'))
    
    # Если форма не была отправлена (метод GET) или не прошла валидацию,
    # просто отображаем страницу с формой
    return render_template('login.html', title='Вход', form=form)

# Функция logout у нас уже есть и работает правильно
@bp.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно вышли из системы.', 'info')
    return redirect(url_for('main.index'))