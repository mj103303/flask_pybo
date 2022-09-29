from flask import Blueprint, render_template, url_for, redirect, request, g, flash

from datetime import datetime

from pybo.views.auth_views import login_required

from .. import db
from ..models import Question, Answer, User
from ..forms import QuestionForm, AnswerForm

bp = Blueprint("question", __name__, url_prefix="/question")

@bp.route('/list/')
def _list():
    page = request.args.get("page", default=1, type=int)    # page
    kw = request.args.get('kw', default='', type=str)    
    
    question_list = Question.query.order_by(Question.create_date.desc())
    if kw:
        search = "%%{}%%".format(kw);
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |    # 질문제목
                    Question.content.ilike(search) |    # 질문내용
                    User.username.ilike(search) |       # 질문작성자
                    sub_query.c.content.ilike(search) | # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    )\
            .distinct()

    question_list = question_list.paginate(page, per_page=10)
    return render_template("question/question_list.html", question_list=question_list, page=page, kw=kw)

@bp.route("/detail/<int:question_id>")
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    return render_template("question/question_detail.html", question=question, form=form)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = QuestionForm()
    
    if request.method == "POST" and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data, create_date=datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
        
    return render_template("question/question_form.html", form=form)

@bp.route('/modify/<int:question_id>', methods=("GET", "POST"))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == "POST":
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)     # populate_obj : form 변수의있는 데이터를 question 객체에 업데이트
            question.modify_date = datetime.now()
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:   # get request
        form = QuestionForm(obj=question)
        return render_template('question/question_form.html', form=form)        

# 질문삭제
@bp.route("/delete/<int:question_id>")
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제 권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    # 위에 if문이 작동안했다는건, g.user == question.user 의미지
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))
        
        
# 질문추천
@bp.route("/vote/<int:question_id>")
@login_required
def vote(question_id):
    _question = Question.query.get_or_404(question_id)
    if g.user == _question.user:
        flash('본인이 작성한 글은 추천할 수 없습니다')
    else:
        _question.voter.append(g.user)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))