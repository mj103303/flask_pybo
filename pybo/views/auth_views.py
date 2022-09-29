from flask import Blueprint, url_for, redirect, flash, request, render_template, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from pybo import db
from pybo.forms import UserCreateForm, UserLoginForm
from pybo.models import User

import functools

bp =Blueprint('auth', __name__, url_prefix="/auth")

@bp.before_app_request  # 라우팅함수보다 항상 먼저 실행됨 *모든 라우팅 함수보다 먼저 실행 모든 모든
def load_logged_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == "GET" else ''
            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)
    return wrapped_view

@bp.route("/signup", methods=('GET', 'POST'))
def signup():
    form = UserCreateForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
            # 가입한 유저가 있는지 찾아보는겨
        # user가 없어야지 가입시키지
        if not user:
            user = User(username=form.username.data, password=generate_password_hash(form.password1.data), email=form.email.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('이미 존재하는 사용자 입니다')
    return render_template('auth/signup.html', form=form)

@bp.route("/login", methods=("GET", "POST"))
def login():
    form = UserLoginForm()
    if request.method == "POST" and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = "존재하지 않는 사용자 입니다"
        if not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 일치하지 않습니다"
        if error == None:            
            session.clear()
            session['user_id'] = user.id
            _next = request.args.get('next', '')
            if _next:
                return redirect(_next)
            else:
                return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)


# logout
@bp.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for('main.index'))
