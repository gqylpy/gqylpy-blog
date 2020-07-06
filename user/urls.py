from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.RegLogin.as_view(), name='reg_login'),  # 注册/登录页面
    url(r'^logout$', views.logout, name='logout'),  # 用户注销
    url(r'^is_user_exists$', views.is_user_exists, name='is_user_exists'),  # 注册/登录时验证用户名是否存在
    url(r'^freebsd_root$', views.freebsd_root, name='is_freebds_root'),  # 遗忘密码
]
