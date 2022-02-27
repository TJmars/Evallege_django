import os

#settings.pyからそのままコピー
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qg8wj%&+enffck-xsjq*mfcm9uvm)bng!n@5s6vg_d^rj(zs38'

#settings.pyからそのままコピー
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'evallege', #　作成したデータベース名
        'USER': 'root', # ログインユーザー名
        'HOST': '',
        'PORT': '',
    }
}

DEBUG = True #ローカルでDebugできるようになります
