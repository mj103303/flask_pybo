from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown
from sqlalchemy import MetaData

import config
from pybo.filter import format_datetime   # 이렇게 임포트를 하네

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))   # 전역변수
migrate = Migrate() # 전역변수



def create_app():
    app = Flask(__name__, )   # 플라스크 애플리케이션을 생성하는 코드야
    app.config.from_object(config)
      

    # ORM
    db.init_app(app)
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db) 
    migrate.init_app(app, db)
    from . import models  
    
    # blueprint    
    from .views import main_views, question_views, answer_views, auth_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)
    app.register_blueprint(auth_views.bp)
    
    # filter
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime
    
    # markdown
    Markdown(app, extensions=["nl2br", "fenced_code"])
        # nl2br : 줄바꿈 자동 , 원래는 스페이스 2개 해야함
        # fenced_code : 코드(코딩) 표시 기능
    
    return app

#! create_app 함수가 : 애플리케이션팩토리
# 함수명 바꾸면 실행안됨 , create_app은 플라스크 내부에서 정의된 함수

