import datetime
from urllib import parse

from django.db.models import Max
from django.urls.resolvers import RegexURLPattern  # 用于获取项目内的所有url
from rest_framework import serializers

from blog import models
from user.models import Attention, UserProfile
from config import urls
from config.settings import DATETIME_FORMAT  # 自定义网页中显示的时间格式
from config.settings import MEDIA_URL  # Media URL
from config.settings import FORBID_BLOG_PATH  #用户主页地址规则


class ArticleListSerializer(serializers.ModelSerializer):
    """文档列表序列化类"""

    # 标题
    title = serializers.SerializerMethodField(read_only=True)
    def get_title(self, obj):
        title = parse.unquote(obj.title)
        return title if len(title.encode()) <= 80 else f'{title[:27]}...'  # 避免展示的名称过长

    # 总体分类
    channel = serializers.SerializerMethodField(read_only=True)
    def get_channel(self, obj):
        return obj.get_channel_display()  # 这个是选择字段，使用此方法来返回value

    # 类型
    type = serializers.SerializerMethodField(read_only=True)
    def get_type(self, obj):
        return obj.get_type_display()  #

    # 评论量
    comment = serializers.SerializerMethodField(read_only=True)
    def get_comment(self, obj):
        return obj.comment.count()

    # 是否存在访问密码
    access_pwd = serializers.SerializerMethodField(read_only=True)
    def get_access_pwd(self, obj):
        return True if obj.access_password else False

    # 文档发布日期
    release_date = serializers.SerializerMethodField(read_only=True)
    def get_release_date(self, obj):
        return datetime.datetime.strftime(obj.release_date, DATETIME_FORMAT)

    # 文档完整路径
    blog_path = serializers.SerializerMethodField(read_only=True)
    def get_blog_path(self, obj):
        return f'/{obj.user.blog_path}/{obj.id}'

    class Meta:
        model = models.BlogInfo
        fields = ['id', 'title', 'type', 'channel', 'visit', 'praise', 'comment', 'release_date', 'access_pwd', 'blog_path']


class CommentListSerializer(serializers.ModelSerializer):
    """评论序列化类"""

    # 文档完整路径
    blog_path = serializers.SerializerMethodField(read_only=True)
    def get_blog_path(self, obj):
        return f'/{obj.user.blog_path}/{obj.blog.id}'

    # 被评文档标题
    article_title = serializers.SerializerMethodField(read_only=True)
    def get_article_title(self, obj):
        title = parse.unquote(obj.blog.title)
        return title if len(title.encode()) <= 80 else f'{title[:27]}...'

    # 评论者昵称
    user_nickname = serializers.SerializerMethodField(read_only=True)
    def get_user_nickname(self, obj):
        return obj.user.nickname

    # 评论者主页
    user_home = serializers.SerializerMethodField(read_only=True)
    def get_user_home(self, obj):
        return f'/{obj.user.blog_path}'

    # 评论者头像
    user_avatar = serializers.SerializerMethodField(read_only=True)
    def get_user_avatar(self, obj):
        return f'/{MEDIA_URL}{obj.user.avatar}'

    # 评论内容（解码）
    content = serializers.SerializerMethodField(read_only=True)
    def get_content(self, obj):
        content = parse.unquote(obj.content)
        return content if len(content.encode()) <= 150 else f'{content[:37]}...'  # 避免展示的评论内容过长

    # 评论日期
    comment_date = serializers.SerializerMethodField(read_only=True)
    def get_comment_date(self, obj):
        return datetime.datetime.strftime(obj.comment_date, DATETIME_FORMAT)

    class Meta:
        model = models.Comment
        fields = ['id', 'blog', 'user', 'content', 'comment_date', 'article_title', 'user_nickname', 'user_home', 'user_avatar', 'blog_path']


class AttentionListSerializer(serializers.ModelSerializer):
    """关注徐序列化类"""

    # 关注者昵称
    from_user_nickname = serializers.SerializerMethodField(read_only=True)
    def get_from_user_nickname(self, obj):
        return obj.from_user.nickname

    # 关注者头像
    from_user_avatar = serializers.SerializerMethodField(read_only=True)
    def get_from_user_avatar(self, obj):
        return f'/{MEDIA_URL}{obj.from_user.avatar}'

    # 关注者主页地址
    from_user_home = serializers.SerializerMethodField(read_only=True)
    def get_from_user_home(self, obj):
        return f'/{obj.from_user.blog_path}'

    # 被关注者昵称
    to_user_nickname = serializers.SerializerMethodField(read_only=True)
    def get_to_user_nickname(self, obj):
        return obj.to_user.nickname

    # 被关注者头像
    to_user_avatar = serializers.SerializerMethodField(read_only=True)
    def get_to_user_avatar(self, obj):
        return f'/{MEDIA_URL}{obj.to_user.avatar}'

    # 被关注者主页
    to_user_home = serializers.SerializerMethodField(read_only=True)
    def get_to_user_home(self, obj):
        return f'/{obj.to_user.blog_path}'

    # 被关注者id
    to_user_id = serializers.SerializerMethodField(read_only=True)
    def get_to_user_id(self, obj):
        return obj.to_user.id

    # 关注日期
    attention_date = serializers.SerializerMethodField(read_only=True)
    def get_attention_date(self, obj):
        return datetime.datetime.strftime(obj.attention_date, DATETIME_FORMAT)

    class Meta:
        model = Attention
        fields = ['to_user_id', 'from_user_nickname', 'to_user_nickname', 'from_user_avatar', 'from_user_home', 'to_user_avatar', 'to_user_home', 'attention_date']


class ClassifyListSerializer(serializers.ModelSerializer):
    """文档分类序列化类"""

    # 分类名称（解码）
    name = serializers.SerializerMethodField()
    def get_name(self, obj):
        name = parse.unquote(obj.name)
        return parse.unquote(name if name.encode() else f'{name[:27]}...')

    # 文档数量
    article_count = serializers.SerializerMethodField()
    def get_article_count(self, obj):
        return obj.blog.filter(is_draft=False, is_delete=False).count()

    class Meta:
        model = models.Classify
        fields = ['id', 'name', 'article_count', 'is_show']
        read_only_fields = ['id', 'article_count', 'is_show']  # 只读字段（即反序列化时不校验的字段）



class ClassifySer(serializers.Serializer):
    """文档分类反序列化类"""

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # 当前用户对象

    name = serializers.CharField(
        max_length=200,
        write_only=True,
        error_messages={
            'max_length': '分类名称过长',
        }
    )


    def validate_name(self, value):
        """校验分类名称"""

        # 提取该用户已存在的分类名称
        name_list = [dct.get('name') for dct in models.Classify.objects.filter(user=self.user).values('name')]

        # 判断分类名称是否重复
        if parse.quote(value) in name_list:
            raise serializers.ValidationError('分类名称不可重复')

        return value.strip()


    def update(self, instance, validated_data):
        """更新数据"""

        # 获取分类新名称
        name = validated_data.get('name', '')

        if name:
            instance.name = parse.quote(name)  # 修改内存中的原始数据
            instance.save()  # 保存到数据库

        return instance


    def create(self, validated_data):
        """添加数据"""

        # 准备添加的分类
        name = parse.quote(validated_data.get('name'))

        # 获取该用户分类最大的排序值，如果该用户没有分类，则排序值为0
        sort_value = models.Classify.objects.filter(user=self.user).values('sort').aggregate(max=Max('sort')).get('max') or 0

        # 添加分类
        models.Classify.objects.create(user=self.user, name=name, sort=sort_value + 1)

        return validated_data



class UserInfoSerializer(serializers.ModelSerializer):
    """用户信息序列化类"""

    # 用户头像完整路径
    avatar = serializers.SerializerMethodField()
    def get_avatar(self, obj):
        return f'/{MEDIA_URL}{obj.avatar}'

    class Meta:
        model = UserProfile
        fields = ['nickname', 'blog_path', 'username', 'email', 'avatar']



class UserInfoSer(serializers.Serializer):
    """用户信息反序列化类"""

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # 当前用户对象

    nickname = serializers.CharField(
        write_only=True,
        max_length=32,
        error_messages={
            'max_length': '昵称过长',
        }
    )

    blog_path = serializers.CharField(
        write_only=True,
        max_length=32,
        error_messages={
            'max_length': '主页地址过长',
        }
    )

    username = serializers.CharField(
        write_only=True,
        max_length=32,
        error_messages={
            'max_length': '用户名过长',
        }
    )

    email = serializers.EmailField(
        write_only=True,
        error_messages={
            'invalid': '邮箱格式错误',
        }
    )

    # 旧密码 新密码
    old_pwd = serializers.CharField(write_only=True)
    new_pwd = serializers.CharField(write_only=True)


    def get_all_urls(self, urlpatterns, prev, is_first=False, result=[]):
        """获取项目所有的URL"""
        if is_first:
            result.clear()
        for item in urlpatterns:
            v = item._regex.strip('^$')
            if isinstance(item, RegexURLPattern):
                result.append(prev + v)
            else:
                self.get_all_urls(item.url_patterns, prev + v)
        return result


    def validate_username(self, value):
        """校验用户名"""

        # 用户名唯一
        if UserProfile.objects.filter(username=value):
            raise serializers.ValidationError('用户名已被使用')

        return value


    def validate_blog_path(self, value):
        """校验主页地址"""

        # 主页地址不可为空
        if value.isspace():
            raise serializers.ValidationError('主页地址不可包含空格')

        # 主页地址不可包含的字符
        for i in FORBID_BLOG_PATH:
            if i in value:
                raise serializers.ValidationError(f'主页地址不可包含的字符：{[i for i in FORBID_BLOG_PATH]}')

        # 获取项目内所有url，并对所有url进行分析过滤去重
        url_list = self.get_all_urls(urls.urlpatterns, prev='/')
        url_set = set([url.split('/')[1] for url in url_list if '(?P<blog_path>.+)' not in url])

        # 主页地址不可为站点内使用的地址
        if value in self.get_all_urls(urls.urlpatterns, prev='/'):
            raise serializers.ValidationError('不可用的地址')

        # 主页地址唯一
        if UserProfile.objects.filter(blog_path=value):
            raise serializers.ValidationError('改地址已被使用')

        return value


    def validate_old_pwd(self, value):
        """校验旧密码"""

        # 校验格式
        if len(value) is not 32:
            raise serializers.ValidationError('密码格式错误')

        # 校验旧密码是否正确
        if not self.user.check_password(value):
            raise serializers.ValidationError('旧密码错误')

        return value


    def validate_new_pwd(self, value):
        """校验新密码"""

        # 校验格式
        if len(value) is not 32:
            raise serializers.ValidationError('密码格式错误')

        # 校验新旧密码是否一致
        if self.user.check_password(value):
            raise serializers.ValidationError('新密码与旧密码不可一致')

        return value


    def update(self, instance, validated_data):
        """更新数据"""
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.blog_path = validated_data.get('blog_path', instance.blog_path)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        # 更新密码
        old_pwd, new_pwd = validated_data.get('old_pwd'), validated_data.get('new_pwd')
        if old_pwd and new_pwd:
            instance.set_password(new_pwd)  # 校验通过则修改密码

        instance.save()
        return instance
