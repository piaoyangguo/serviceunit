import os
import raven
import logging
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'nj(vhl79)l*deqlvart7uy3sy#j&0f6z56f&l5ytyw5jdo7+qj')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', True)

#ALLOWED_HOSTS = ['127.0.0.1', 'test.teamin.cc', 'litepc.teamin.cc']
#ALLOWED_HOSTS = ['127.0.0.1', '10.94.0.11']
ALLOWED_HOSTS = ['127.0.0.1', '*']

ENV = {
    'prod': {
        'db': 'mysql://taskrecog:chainton_01@rds181qo19304o768zgt.mysql.rds.aliyuncs.com/taskrecog',
        'teamin_base': 'https://lite.teamin.cc',
        'h5_base': 'https://litepc.teamin.cc/assistant',
        'name_base': 'http://127.0.0.1:18416',
        'unit_apikey': 'lxz6Li7yG9M3P0gb2Dk4UdPn',
        'unit_secretkey': 'RI7YCcKwHsn58Mf5S3PoBPl9zs1ILiYT',
        #'unit_scene': 21784,
        'unit_scene': 22110,
    },
    'test': {
        'db': 'mysql://teamin_test:vWLKfnvNvQsM6RNu@rds181qo19304o768zgt.mysql.rds.aliyuncs.com:3306/serviceunit_test',
        'teamin_base': 'https://evn-test.teamin.cc',
        'h5_base': 'https://litepc.teamin.cc/assistant3',
        'name_base': 'http://evn-test.teamin.cc:28416',
        'unit_apikey': 'lxz6Li7yG9M3P0gb2Dk4UdPn',
        'unit_secretkey': 'RI7YCcKwHsn58Mf5S3PoBPl9zs1ILiYT',
        #'unit_scene': 21784,
        'unit_scene': 22110,
    },
    'dev': {
        'db': 'mysql://teamin_test:vWLKfnvNvQsM6RNu@rds181qo19304o768zgt.mysql.rds.aliyuncs.com:3306/serviceunit_dev',
        'teamin_base': 'https://evn-develop.teamin.cc',
        'h5_base': 'https://litepc.teamin.cc/assistant3',
        'name_base': 'http://evn-develop.teamin.cc:18416',
        'unit_apikey': 'lxz6Li7yG9M3P0gb2Dk4UdPn',
        'unit_secretkey': 'RI7YCcKwHsn58Mf5S3PoBPl9zs1ILiYT',
        #'unit_scene': 21784,
        'unit_scene': 22110,
    },
}
x = os.environ.get('UNIT_ENV', 'dev')
if x not in ENV:
    x = 'dev'
ENV = ENV[x]
print('DJANGO RUN AT ENV << {} >>'.format(x))

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=ENV['db'],
    )
}

UNIT_SCENE_ID   = ENV['unit_scene']
UNIT_API_KEY    = ENV['unit_apikey']
UNIT_SECRET_KEY = ENV['unit_secretkey']

TEAMIN_BASE = ENV['teamin_base']
H5_BASE     = ENV['h5_base']
NAME_BASE   = ENV['name_base']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ]
}

ROOT_URLCONF = 'serviceunit.urls'


#UNIT_INTRO = '''你好！我目前可以做以下事情：
#1. 创建任务
#例：创建任务，小明下午三点开会
#2. 接收文档
#直接将文档发送给我即可
#3.查询任务
#例：查询任务，我最近一周的任务
#4.查询文档
#例：查询文档，我今天上午上传的关于人事任命的文档
#现在试着参照例句让我帮你处理一些事情吧！'''

UNIT_INTRO_v2 = {
    'text': '\n'.join([
        '抱歉，我还不能理解你的意思，目前我还在学习期，请多给我一点时间，我会从错误中成长，变得越来越聪明',
        '',
        '点这里，查看我的使用说明',
    ]),
    'url': 'https://litepc.teamin.cc/assistant/h5/help/person',
    'gurl': 'https://litepc.teamin.cc/assistant/h5/help/organization',
}


#UNIT_HELP = '''您好，目前我还在学习期，请多给我一点时间，我会从错误中成长，变得越来越聪明，现在我可以做以下事情：
#1. 创建任务（字数不可以超过120字）
#例：创建任务，小明下午三点开会
#2. 接收文档
#直接将文档发送给我即可
#3.查询任务
#例：查询任务，我最近一周的任务
#4.查询文档
#例：查询文档，我今天上午上传的关于人事任命的文档
#参照例句发送给我，让我帮您处理一些事情吧！
#发送指令前请确保账号已绑定。'''

UNIT_HELP_v2 = {
    'text': '\n'.join([
        '使用中遇到问题了吗？',
        '点这里，查看使用说明',
    ]),
    'url': UNIT_INTRO_v2['url'],
    'gurl': UNIT_INTRO_v2['gurl'],
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'serviceunit.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

DATE_FORMAT = '%Y-%m-%d'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime).19s %(message)s'
        },
        'verbose': {
            'format': '%(asctime)s %(levelname)s[%(module)s][line:%(lineno)d] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'info.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        'django': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
    },
}
