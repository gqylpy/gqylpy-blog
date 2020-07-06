from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.views.static import serve
from django.views import static
from django.views.generic.base import RedirectView

from blog import views
from config.settings import MEDIA_URL  # Media 路径
from config.settings import MEDIA_ROOT  # Media 目录
from config.settings import STATIC_URL  # 静态资源路径
from config.settings import STATIC_ROOT  # 静态资源路径

urlpatterns = [
    # 网站首页
    url(r'^$', views.index, name='index'),

    # 用户主页相关
    url(r'^home/', include('blog.urls', namespace='home')),

    # 管理页面相关
    url(r'^edit-X/', include('edit.urls', namespace='edit')),

    # 用户认证相关
    url(r'^auth/', include('user.urls', namespace='auth')),

    # 处理写文档相关
    url(r'^strive/', include('strive.urls', namespace='strive')),

    # 管理站点
    url(r'^xx-xx', admin.site.urls),

    # # Favicon.ico
    # url(r'^favicon\.ico$', RedirectView.as_view(url=f'{STATIC_URL}favicon.ico'), name='favicon.ico'),
    #
    # # Robots.txt
    # url(r'^robots\.txt$', RedirectView.as_view(url=f'{STATIC_URL}robots.txt'), name='robots.txt'),
    #
    # # Sitemap.txt
    # url(r'^sitemap\.txt$', RedirectView.as_view(url=f'{STATIC_URL}sitemap.txt'), name='sitemap.txt'),

    # Media url（静态资源交由代理处理）
    # url(rf'^{MEDIA_URL}(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),

    # # Static url（静态资源交由代理处理）
    # url(r'^static/(?P<path>.*)', static.serve, {'document_root': STATIC_ROOT}, name='static'),

    # 返回文档页面
    url(r'^(?P<blog_path>.+)/(?P<article_id>\d+)/$', views.ArticleInfo.as_view(), name='article'),

    # 返回用户主页 (勿改url，user.forms.117有用到)
    url(r'^(?P<blog_path>.+)/$', views.home, name='home'),
]

# 不要试图改变最后两条路由的位置及顺序
