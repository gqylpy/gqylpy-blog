import datetime
from urllib.parse import unquote
from rest_framework import serializers
from blog import models

from config.wlmj import WLMJ_CONTENT
from config.settings import WLMJ
from config.settings import MEDIA_URL  # Media URL
from config.settings import DATETIME_FORMAT  # 自定义网页中显示的时间格式
from config.settings import WLMJ_VISIT_LINK
from config.settings import WLMJ_USER
from config.settings import WLMJ_PAYMENT_LINK

_wlmj = WLMJ_CONTENT % ({
    'wlmj_visit_link': WLMJ_VISIT_LINK,
    'wlmj_payment_link': WLMJ_PAYMENT_LINK
})


class ArticleInfoSerializer(serializers.ModelSerializer):
    """文档信息序列化类"""

    def __init__(self, is_show_article, is_index=None, from_page='', *args, **kwargs):
        """
        :param is_show_article: 是否序列化文档内容，描述(取反)，评论
        :param is_index: 当前序列化视图是否为首页
        """
        super().__init__(*args, **kwargs)
        self.is_show_article = is_show_article
        self.is_index = is_index
        self.from_page = from_page

    # 文档对应的用户信息（头像）
    user_avatar = serializers.SerializerMethodField(read_only=True)

    def get_user_avatar(self, obj):
        return self.is_index and f'/{MEDIA_URL}{str(obj.user.avatar)}'

    # 文档对应的用户信息（昵称）
    user_nickname = serializers.SerializerMethodField(read_only=True)

    def get_user_nickname(self, obj):
        return self.is_index and obj.user.nickname

    # 文档对应的用户信息（主页）
    user_home = serializers.SerializerMethodField(read_only=True)

    def get_user_home(self, obj):
        return self.is_index and f'/{obj.user.blog_path}'

    # 文档完整路径
    blog_path = serializers.SerializerMethodField(read_only=True)

    def get_blog_path(self, obj):
        return f'/{obj.user.blog_path}/{obj.id}'

    # 文档类型
    type = serializers.SerializerMethodField(read_only=True)

    def get_type(self, obj):
        return obj.get_type_display()  # 这个是选择字段，使用此方法来返回value

    # 文档评论数量
    comment_number = serializers.SerializerMethodField(read_only=True)

    def get_comment_number(self, obj):  # obj就相当于 models.表名.object 中的object
        return len(obj.comment.filter(is_delete=False))  # 返回评论的总数

    # 是否有访问密码
    restrict_access = serializers.SerializerMethodField(read_only=True)

    def get_restrict_access(self, obj):
        return True if obj.access_password else False

    # 文档标题（解码）
    title = serializers.SerializerMethodField(read_only=True)

    def get_title(self, obj):
        return unquote(obj.title)

    # 文档描述（解码）
    description = serializers.SerializerMethodField(read_only=True)

    def get_description(self, obj):
        return not self.is_show_article and not obj.access_password and unquote(obj.description)

    # 文档发布日期
    release_date = serializers.SerializerMethodField(read_only=True)

    def get_release_date(self, obj):
        return datetime.datetime.strftime(obj.release_date, DATETIME_FORMAT)

    # 文档内容
    content = serializers.SerializerMethodField(read_only=True)

    def get_content(self, obj):
        if not self.is_show_article:
            return None

        content = unquote(obj.content.content)

        # 开启WLMJ
        # if WLMJ and obj.user_id in WLMJ_USER:  # and self.from_page not in ['index', 'home', 'self']:
        #     content = _wlmj + content

        return '该文有密码' if obj.access_password else content

    # 文档评论
    comment = serializers.SerializerMethodField(read_only=True)

    def get_comment(self, obj):
        if not self.is_show_article:
            return []
        comment_lst = []
        for com_obj in obj.comment.filter(is_delete=False).order_by('-comment_date'):
            dct = {'id': com_obj.id, 'content': unquote(com_obj.content), 'com_user': com_obj.user.nickname,
                   'reply_user': None,
                   'com_user_id': com_obj.user.id, 'com_user_av': f'/{MEDIA_URL}{str(com_obj.user.avatar)}',
                   'com_user_path': f'/{com_obj.user.blog_path}',
                   'com_date': datetime.datetime.strftime(com_obj.comment_date, DATETIME_FORMAT)}
            if com_obj.reply:
                dct.update({'com_user': com_obj.reply.user.nickname, 'reply_user': com_obj.user.nickname,
                            'reply_user_path': f'/{com_obj.reply.user.blog_path}',
                            'reply_user_id': com_obj.user.id,
                            'reply_user_av': f'/{MEDIA_URL}{str(com_obj.reply.user.avatar)}'})
            comment_lst.append(dct)
        return comment_lst

    class Meta:
        model = models.BlogInfo
        fields = ['id', 'title', 'description', 'praise', 'visit', 'tags', 'type', 'user_avatar', 'user_nickname',
                  'release_date', 'restrict_access', 'comment_number', 'content', 'comment', 'blog_path', 'user_home']


class ClassifySerializer(serializers.ModelSerializer):
    """个人分类序列化类"""

    # 当前分类中的文档数量
    article_count = serializers.SerializerMethodField(read_only=True)

    def get_article_count(self, obj):
        return obj.blog.filter(is_draft=False, is_delete=False, is_private=False).count()

    # 分类名称（解码）
    name = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        name = unquote(obj.name)
        return name if len(name.encode()) <= 45 else f'{name[:16]}..'  # 避免分类名称过长

    class Meta:
        model = models.Classify
        fields = ['id', 'name', 'article_count']
