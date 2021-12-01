from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'team-5.cvyy2p2s4med.ap-northeast-2.rds.amazonaws.com',
        'PORT': 3306,
        'NAME': 'everytime_backend',
        'USER': 'everytime-backend',
        'PASSWORD': 't5database',
    }
}
