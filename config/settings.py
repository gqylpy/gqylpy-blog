WLMJ = True

WLMJ_VISIT_LINK = 'http://blog.gqylpy.com/gqy/401/'
WLMJ_PAYMENT_LINK = 'http://www.gqylpy.com/get_wlmj_pwd'

WLMJ_USER = [6, 3011]
# [gqy, gqy02]

"""
Django settings for hello_world project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xh97j_h_@92m^qp*2*)j985c_%#2z%39c^z$74q=u8o-g5+unc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# 关闭调试模式后，必须配置 ALLOWED_HOSTS, STATIC_ROOT 和静态路由(hello_world.urls line 22)

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'user',  # 用户认证相关
    'strive',  # 处理编写文档
    'blog',  # 用户主页、首页、查看文档相关
    'edit',  # 管理相关
]

MIDDLEWARE = [
    'config.middlewares.HoldBackThiefStrategy',  # 发爬策略
    'config.middlewares.RecordRequestTime',  # 记录请求耗时
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'hello_world.middlewares.RecordViewError',  # 记录图异常信息，以便后续分析
    # 'strive.middlewares.DisableCSRFCheck',  # 用于取消个别请求进行csrf_coken校验（！已使用装饰器取消校验）
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'hello_world',
#         'HOST': 'blog.gqylpy.com',
#         'PORT': '3380',
#         'USER': 'zyk',
#         'PASSWORD': 'Two_cic1314',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hello_world',
        'HOST': 'localhost',
        'PORT': '3380',
        'USER': 'hlwd',
        'PASSWORD': 'user@hlwd',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'


USE_I18N = True

USE_L10N = True


# 引用Django自带的auth_user表，继承使用时需要配置
AUTH_USER_MODEL = 'user.UserProfile'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/


# ============================ 静态文件配置 =============================

STATIC_URL = '/static/'
# STATIC_ROOT = r'Y:\static'
STATIC_ROOT = '/data/gqylpy-blog/static/'

STATICFILES_DIRS = [
    os.path.abspath(os.path.join(BASE_DIR, 'static'))
]

# 执行命令：python3 manage.py collectstatic
# 将STATICFILES_DIRS中的所有文件夹和文件，以及各app中static中的文件都复制到STATIC_ROOT指定的目录下


# ========================= 站点登录页面的路由 ==========================

LOGIN_URL = '/auth'


# ============================== Meida配置 ==============================

MEDIA_URL = 'media/'  # 指定url路径
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # 指定媒体目录，用于存储上传的图片
MEDIA_ROOT = '/data/gqylpy-blog/media'  # 指定媒体目录，用于存储上传的图片


# ============================= Session配置 =============================

# SESSION_COOKIE_NAME = 'e10adc3949ba59abbe56e057f20f883e'  # Session的cookie保存在浏览器上的key，默认为sessionid
SESSION_COOKIE_AGE = 60 * 60 * 24 * 60  # Session的cookie实效日期，这里设置为60天，默认为两周
# SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'  # 使用加密Cookie来存储session数据，默认使用的是数据库


# ============================ 图片验证码配置 ============================

FONT_FILE_PATH = os.path.join(BASE_DIR, 'tools/tool_rely_on/kumo.ttf')  # 字体文件路径


# =========================== 禁用CSRF校验的URL ===========================

# DISABLE_CSRF_CHECK = [
#     '/strive/saveArticle',  # 发布/保存文档
#     '/strive/UploadImage',  # 上传图片
# ]
# 已使用装饰器取消校验


# ================= 对数据库中所有文档的分类/首页展示的分类 =================

BLOG_TYPE = (
    # (6, '书籍'),
    (1, '前端'),
    (2, '后端'),
    (3, '运维'),
    # (4, '测试'),
    (4, '数据库'),
    (5, '其它'),
)


# ========================= Markdown编辑器页面样式 =========================

IS_EXPERT = True  # 是否为专家（为专家者，头像带特效）
IS_MUSER = False  # 是否为管理员（为管理员者，展示文档管理链接）
CODE_THEME = 'prism-atom-one-light'  # 代码块类型（代码块区分颜色）


# ============================== 上传文件规则 ==============================

ALLOW_UPLOAD_FILE_SUFFIX_RE = r'^.*\.(jpg|jpeg|gif|png|bmp)$'  # 仅允许的后缀，正则
MAX_UPLOAD_FILE_SIZE = 1024 * 1024 * 5  # 允许的最大size


# =========================== 年轻人，你有梦想吗 ===========================

LIST = [
    '只有经历地狱般的磨砺，才能练就创造天堂的力量！',
    '你的负担将变成你的礼物，你受的苦将照亮你的路！',
]


# ============================ 用户主页地址规则 ============================

FORBID_BLOG_PATH = ['/', '.', '\\']  # 不可包含的字符列表


# ============================== 文档描述长度 ==============================

ARTICLE_DESCRIPTION_LENGTH = 150  # 该字段最大长度为2048（存的是url编码格式）


# =========================== rest_framework配置 ===========================

REST_FRAMEWORK = {
    # -------------------- 全局分页配置 -------------------
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',  # 指定分页类
    'PAGE_SIZE': 10,  # 每页显示多少条数据
    'PAGE_QUERY_PARAM': 'page',  # 查询页码的字符串
}

EDIT_PAGE_SIZE = 20  # 管理页面显示数据的最大条数


# ============================== 日期格式配置 ==============================

TIME_ZONE = 'Asia/Shanghai'  # 默认时区
USE_TE = False  #
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'  # 自定义网页中显示的时间格式


# ============================ 全局模糊查询配置 =============================

GLOBAL_QUERY_FIELD_LIST = ['title', ]  # 定义可被查询的字段（BlogInfo表） 内容: content__content


# ============================== 站点名称配置 ===============================

SITE_NAME = ' · GQYLPY'  # 站点名称
LAYOUT_TITLE = 'GQYLPY'  # 全局标题（优先级低）
LAYOUT_TITLE_MAX_LENGTH = 27


# ============================== 通用报错响应 ===============================

ERROR_INFO = {'data': None, 'status': False, 'msg': '你好，GQYLPY'}  # 视图异常响应


# ============================ 记录视图异常的文件 ============================

VIEW_ERROR_LOG_FILE = '/var/log/django_view_error.log'


# ================================= 发爬策略 =================================

HOLD_BACK_USER_AGENT = ['py', 'ssl', ]  # 客户端标识不可包含的字符串
