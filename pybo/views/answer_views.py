from flask import Blueprint, render_template, redirect, url_for, request, g, flash
from datetime import datetime

from pybo import db
from pybo.views.auth_views import login_required     
# migrate는 안가지고오네
from ..forms import AnswerForm
from pybo.models import Question, Answer

bp = Blueprint("answer", __name__, url_prefix="/answer")

# 삭제
@bp.route("/delete/<int:answer_id>")
@login_required
def delete(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question.id
    if g.user != answer.user:
        flash("삭제 권한이 없습니다")
    else:
        db.session.delete(answer)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))

# 수정
@bp.route("/modify/<int:answer_id>", methods=("GET", "POST"))
@login_required
def modify(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if g.user != answer.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=answer.question.id))
    if request.method == "POST":
        form = AnswerForm()     # 이걸로 검사함
        if form.validate_on_submit():
            form.populate_obj(answer)   # form에 answer를 채우는 게 맞는거 같애
                # form은 클래스 모델 객체잖아
            answer.modify_date = datetime.now() # 수정일시저장
            db.session.commit()
            return redirect("{}#answer_{}".format(url_for('question.detail', question_id=answer.question.id), answer.id))
    else:   # get 
        form = AnswerForm(obj=answer)
    return render_template('answer/answer_form.html', form=form)
            
            

@bp.route("/create/<int:question_id>", methods=["POST"])
@login_required
def create(question_id):
    form = AnswerForm()    
    question = Question.query.get_or_404(question_id)
    
    if request.method == "POST" and form.validate_on_submit():
        content = request.form.get("content")
        answer = Answer(content=content, create_date=datetime.now(), user=g.user)
            # wow: g.user는 @bp.before_app_request 애너테이션에 의해 생성
            # g.user는 로그인한 사용자야
        '''
            answer = Answer(question=question, content, create_date=datetime.now())
            db.session.add(answer)
            db.session.commit()
            이렇게 해도, 저장가능 >> 존나 불편하네
            question=릴레이션할 질문 적는겨
        '''
        question.answer_set.append(answer)
        db.session.commit()
        return redirect("{}#answer_{}".format(url_for('question.detail', question_id=question_id), answer.id))

    return render_template('question/question_detail.html', question=question, form=form)

# 추천
@bp.route("/vote/<int:answer_id>")
@login_required
def vote(answer_id):
    _answer = Answer.query.get_or_404(answer_id)
    if g.user == _answer.user:
        flash('본인이 작성한 글은 추천할수 없습니다')
    else:
        _answer.voter.append(g.user)
        db.session.commit()
    return redirect("{}#answer_{}".format(url_for('question.detail', question_id=_answer.question.id), _answer.id))