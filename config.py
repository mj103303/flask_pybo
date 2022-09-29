import os

BASE_DIR =os.path.dirname(__file__)
# __file__ : 파일명까지
# config.py 파일 위치 (폴더까지만)


SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))
    # sqlite가 사용되고
    # 파일은 pybo.db 파일로 저장된다.
SQLALCHEMY_TRACK_MODIFICATIONS = False      # sqlalchemy의 이벤트를 처리하옵션
    # 파이보에 불필요
    # 

SECRET_KEY = "dev"
