from django.conf.urls import url
from blog import views


urlpatterns = [
    url(r'^getArticleList$', views.ArticleListView.as_view(), name='get_article_list'),  # 返回文档列表
    url(r'^getArticleInfo$', views.ArticleInfoView.as_view(), name='get_article_info'),  # 返回文档信息
    url(r'^getArticleContent$', views.ArticleContentView.as_view(), name='get_article_content'),  # 返回文档内容（有密码时）
    url(r'^getUserInfo$', views.UserInfoView.as_view(), name='get_userinfo'),  # 返回用户信息
    url(r'^do_follow$', views.DoFollowView.as_view(), name='do_follow'),  # 关注用户
    url(r'^comment$', views.CommentView.as_view(), name='comment'),  # 文档评论
    url(r'^praise$', views.PraiseView.as_view(), name='praise'),  # 文档点赞
    url(r'^getArticleList-X$', views.IndexArticleListView.as_view(), name='get_index_article_list'),  # 返回首页文档列表
    url(r'^sreachArticle$', views.SreachArticleView.as_view(), name='search_article'),  # 模糊查询
]
