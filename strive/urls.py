from django.conf.urls import url
from strive import views


urlpatterns = [
    # ---------- Markdown编辑器 ----------
    url(r'^$', views.Strive.as_view(), name='strive'),  # 写文章页面
    url(r'^(?P<id>\d*)$', views.Strive.as_view(), name='strive_id'),  # 编辑文章页面，id为UserInfo表的id
    url(r'^saveArticle$', views.SaveArticle.as_view(), name='save_article'),  # 发布/保存文章的路径
    url(r'^getArticle$', views.GetArticle.as_view(), name='get_article'),  # 获取文章内容
    url(r'^UploadImage$', views.UploadImage.as_view(), name='upload_image'),  # 上传图片
]
