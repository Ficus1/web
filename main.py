import os

from flask import Flask, render_template, url_for, request
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
import requests
from data import db_session, advert_api
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.users import User
from data.towns import Towns
from data.adverts import Adverts
from data.category import Categories
from forms.user import RegisterForm
from cities import cities
from forms.login import LoginForm
from forms.addadverts import AddAdverts
from data.likest import Like
from geoc import get_ll_span

from web_pr.data.db_session import check_password

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def check_phone_number(number):
    number = ''.join(number.split())
    try:
        if number.find('+7') != 0 and number.find('8') != 0:
            raise ValueError

        if number.startswith('8'):
            number = '+7' + number[1:]

        a = number.find('(')
        if a > -1:
            b = number.index(')', a + 2)
            number = list(number)
            number.pop(a)
            number.pop(b - 1)
            number = ''.join(number)

        number = "+" + ''.join(str(int(i)) for i in number[1:].split('-'))
        if len(number[1:]) != 11:
            raise ValueError

    except Exception:
        return False

    return True


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/personal_cabinet/<int:user_id>')
@login_required
def open_pc(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    adverts = []
    for i in db_sess.query(Adverts).filter(Adverts.member == user_id).all():
        adverts.append([i.name, i.price, i.photo, i.town, i.id, i.member])
    return render_template('personal_cabinet.html', title='Личный кабинет', user=user, adverts=adverts)


@app.route('/open/<int:ad_id>')
@login_required
def open_ad(ad_id):
    db_sess = db_session.create_session()
    ad = db_sess.query(Adverts).get(ad_id)
    map_params = {
        "ll": get_ll_span(ad.address)[0],
        "spn": get_ll_span(ad.address)[1],
        "l": 'sat,skl'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    try:
        response = requests.get(map_api_server, params=map_params)
    except Exception:
        return render_template('open.html', title='Окно тоавара', ad=ad, map='')
    return render_template('open.html', title='Окно тоавара', ad=ad, map=response.url)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    adverts = []
    sort = ['Электроприборы', 'Авто', 'Недвижимость', 'Работа', 'Другое']
    for i in db_sess.query(Adverts).all():
        adverts.append([i.name, i.price, i.photo, i.town, i.id, i.member])
    return render_template('main.html', adverts=adverts, title='Объявления', sort=sort)


@app.route('/<cat>')
@login_required
def index_filt(cat):
    db_sess = db_session.create_session()
    category_ = db_sess.query(Categories).filter(Categories.name == cat).first()
    ad = db_sess.query(Adverts).filter(Adverts.category == category_.id).all()
    sort = ['Электроприборы', 'Авто', 'Недвижимость', 'Работа', 'Другое']
    adverts = []
    for i in ad:
        adverts.append([i.name, i.price, i.photo, i.town, i.id, i.member])
    return render_template('main.html', adverts=adverts, title='Объявления', sort=sort)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if not check_phone_number(form.phone_number.data):
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Неверный формат номера телефона")
        if db_sess.query(User).filter(User.phone_number == form.phone_number.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой номер телефона уже зарегестрирован")
        with open(f"static/img/{request.files['file'].filename}", "wb") as file:
            f = request.files.get('file').read()
            file.write(f)
            file.close()

        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            age=form.age.data,
            phone_number=form.phone_number.data,
            town=form.town.data,
            photo=request.files['file'].filename
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form, cities=cities)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    form = RegisterForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            form.name.data = user.name
            form.surname.data = user.surname
            form.age.data = user.age
            form.email.data = user.email
            form.phone_number.data = user.phone_number
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            if request.files['file'].filename:
                with open(f"static/img/{request.files['file'].filename}", "wb") as file:
                    f = request.files.get('file').read()
                    file.write(f)
                    file.close()
                    current_user.photo = request.files['file'].filename
            user.name = form.name.data
            user.surname = form.surname.data
            user.age = form.age.data
            user.email = form.email.data
            user.phone_number = form.phone_number.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('register.html', title='Регистрация', form=form, cities=cities)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/add_advert', methods=['GET', 'POST'])
def add_advert():
    form = AddAdverts()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        with open(f"static/img/{request.files['file'].filename}", "wb") as file:
            f = request.files.get('file').read()
            file.write(f)
            file.close()
        advert = Adverts(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            about=form.about.data,
            category=form.category.data,
            address=form.address.data,
            photo=request.files['file'].filename,
            member=current_user.id,
            town=current_user.town
        )
        db_sess.add(advert)
        db_sess.commit()
        return redirect('/')
    return render_template('addadvert.html', title='Добавление объявления', form=form)


@app.route('/edit/<int:id>',  methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = AddAdverts()
    if request.method == "GET":
        db_sess = db_session.create_session()
        ad = db_sess.query(Adverts).filter(Adverts.id == id, ((Adverts.member == current_user.id) | (current_user.id == 1))).first()
        if ad:
            form.name.data = ad.name
            form.price.data = ad.price
            form.description.data = ad.description
            form.about.data = ad.about
            form.address.data = ad.address
            form.category.data = ad.category
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        ad = db_sess.query(Adverts).filter(Adverts.id == id, ((Adverts.member == current_user.id) | (current_user.id == 1))).first()

        if ad:
            if request.files['file'].filename:
                with open(f"static/img/{request.files['file'].filename}", "wb") as file:
                    f = request.files.get('file').read()
                    file.write(f)
                    file.close()
                    ad.photo = request.files['file'].filename
            ad.name = form.name.data
            ad.price = form.price.data
            ad.description = form.description.data
            ad.about = form.about.data
            ad.address = form.address.data
            ad.category = form.category.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('addadvert.html',
                           title='Редактирование работы',
                           form=form
                           )


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    db_sess = db_session.create_session()
    ad = db_sess.query(Adverts).filter(Adverts.id == id, ((Adverts.member == current_user.id) | (current_user.id == 1))).first()
    if ad:
        db_sess.delete(ad)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/likest')
@login_required
def likest():
    db_sess = db_session.create_session()
    adverts = []
    sort = ['Электроприборы', 'Авто', 'Недвижимость', 'Работа', 'Другое']
    for j in db_sess.query(Like).filter(Like.member == current_user.id).all():
        for i in db_sess.query(Adverts).filter(Adverts.id == j.advert).all():
            adverts.append([i.name, i.price, i.photo, i.town, i.id, i.member])
    return render_template('like.html', adverts=adverts, title='Понравившиеся', sort=sort)


@app.route('/like/<int:id>')
@login_required
def like(id):
    db_sess = db_session.create_session()
    likee = Like(
        member=current_user.id,
        advert=id
    )
    if not db_sess.query(Like).filter(Like.member == current_user.id, Like.advert == id).first():
        db_sess.add(likee)
        db_sess.commit()
    return redirect('/')


@app.route('/delete_like/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_like(id):
    db_sess = db_session.create_session()
    lk = db_sess.query(Like).filter(Like.member == current_user.id, Like.advert == id).first()
    if lk:
        db_sess.delete(lk)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/likest')


@app.route('/edit_1/<int:id>',  methods=['GET', 'POST'])
@login_required
def del_1(id):
    form = AddAdverts()
    if request.method == "GET":
        db_sess = db_session.create_session()
        ad = db_sess.query(Adverts).filter(Adverts.id == id, ((Adverts.member == current_user.id) | (current_user.id == 1))).first()
        if ad:
            form.name.data = ad.name
            form.price.data = ad.price
            form.description.data = ad.description
            form.about.data = ad.about
            form.address.data = ad.address
            form.category.data = ad.category
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        ad = db_sess.query(Adverts).filter(Adverts.id == id, ((Adverts.member == current_user.id) | (current_user.id == 1))).first()

        if ad:
            if request.files['file'].filename:
                with open(f"static/img/{request.files['file'].filename}", "wb") as file:
                    f = request.files.get('file').read()
                    file.write(f)
                    file.close()
                    ad.photo = request.files['file'].filename
            ad.name = form.name.data
            ad.price = form.price.data
            ad.description = form.description.data
            ad.about = form.about.data
            ad.address = form.address.data
            ad.category = form.category.data
            db_sess.commit()
            return redirect(f'/open/{id}')
        else:
            abort(404)
    return render_template('addadvert.html',
                           title='Редактирование работы',
                           form=form
                           )


def main():
    db_session.global_init("db/site.db")


if __name__ == '__main__':
    app.register_blueprint(advert_api.blueprint)
    main()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
