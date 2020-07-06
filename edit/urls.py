from django.conf.urls import url
from edit import views


urlpatterns = [
    url(r'^$', views.edit, name='edit'),  # 返回管理页面

    # ---------------------------------------- 文档管理 ----------------------------------------
    url(r'^getArticleList$', views.ArticleListView.as_view(), name='get_article_list'),  # 获取文档数据
    url(r'^setArticlePwd$', views.SetArticlePwdView.as_view(), name='set_article_pwd'),  # 设置文档密码
    url(r'^deleteArticlePwd$', views.DeleteArticlePwdView.as_view(), name='delete_article_pwd'),  # 删除文档密码
    url(r'^deleteArticle$', views.DeleteArticleView.as_view(), name='delete_article'),  # 删除文档
    url(r'^recoverArticle$', views.RecoverArticleView.as_view(), name='recover_article'),  # 撤销删除的文档

    # ---------------------------------------- 评论管理 ----------------------------------------
    url(r'^getCommentList$', views.CommentListView.as_view(), name='get_comment_list'),  # 获取评论数据
    url(r'^deleteComment$', views.DeleteCommentView.as_view(), name='delete_comment'),  # 删除评论

    # ---------------------------------------- 关注管理 ----------------------------------------
    url(r'^getAttentionList$', views.AttentionListView.as_view(), name='get_attention_list'),  # 获取关注数据

    # ---------------------------------------- 分类管理 ----------------------------------------
    url(r'^getClassifyList$', views.GetClassifyListView.as_view(), name='get_classify_list'),  # 获取个人分类数据
    url(r'^showOrConcealClassify$', views.ShowOrConcealClassifyView.as_view(), name='show_or_conceal_classify'),  # 主页显示/隐藏分类
    url(r'^setClassifyName$', views.alterClassifyNameView.as_view(), name='alter_classify_name'),  # 修改分类名称
    url(r'^deleteClassify$', views.DeleteClassifyView.as_view(), name='delete_classify'),  # 删除分类
    url(r'^setClassifySort$', views.SetClassifySortView.as_view(), name='set_classify_sort'),  # 设置分类排序
    url(r'^addClassify$', views.AddClassifyView.as_view(), name='add_classify'),  # 添加分类

    # ---------------------------------------- 个人信息 ----------------------------------------
    url(r'^getUserInfo$', views.GetUserInfoView.as_view(), name='get_user_info'),  # 获取用户信息
    url(r'^uploadAvatar$', views.UploadAvatarView.as_view(), name='upload_avatar'),  # 上传头像
    url('^setNickname$', views.SetNicknameView.as_view(), name='set_nickname'),  # 修改昵称
    url('^setBlogPath$', views.SetBlogPathView.as_view(), name='set_blog_path'),  # 修改主页地址
    url(r'^setUserName$', views.SetUserNameView.as_view(), name='set_username'),  # 修改用户名
    url(r'^setEmail$', views.SetEmailView.as_view(), name='set_email'),  # 修改邮箱
    url(r'^setUserPwd$', views.SetUserPwdView.as_view(), name='set_user_pwd'),  # 修改密码
]
