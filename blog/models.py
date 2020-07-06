from urllib import parse
from django.db import models
from user.models import UserProfile
from config.settings import BLOG_TYPE  # 对数据表中所有文档的分类


__all__ = ['BlogInfo', 'Article', 'Classify', 'Comment', 'ArticleImg']


# 文档类型
article_type_choices = (
    ('original', '原'),
    ('repost', '转'),
    ('translated', '译'),
)


class BlogInfo(models.Model):
    """文档信息表"""
    title = models.CharField('标题', max_length=1000)  # max_length=65535
    content = models.OneToOneField('Article', verbose_name='文档内容', unique=True, related_name='blog')  # related_name='blog'：反向查询时使用的字段名
    description = models.CharField('描述', max_length=2048)
    praise = models.BigIntegerField('赞', default=0)
    visit = models.BigIntegerField('访问量', default=0)
    classify = models.ManyToManyField('Classify', verbose_name='个人分类', related_name='blog', help_text='用户自己的分类')  # null没有影响
    user = models.ForeignKey(UserProfile, verbose_name='所属用户', related_name='blog')
    tags = models.TextField('标签', max_length=1500, null=True, blank=True, help_text='多个标签用 "," 逗号分隔')  # max_length=65534：varchar最大长度
    channel = models.IntegerField('文档分类', choices=BLOG_TYPE, null=True, blank=True, help_text='对数据表中所有博客的分类')
    type = models.CharField('文档类型', choices=article_type_choices, max_length=16, default='original')
    # stick_date = models.DateTimeField('置顶时间', null=True, blank=True, help_text='为空，即不置顶')
    is_private = models.BooleanField('是否私密', default=False)
    is_draft = models.BooleanField('是否草稿', default=True)
    is_delete = models.BooleanField('是否删除', default=False)
    access_password = models.CharField('访问密码', max_length=32, null=True, blank=True, help_text='为空，即无密码')
    release_date = models.DateTimeField('发布日期', auto_now_add=True)
    # 一对多评论表，反向查询字段名：comment

    def __str__(self):
        return parse.unquote(self.title)

    class Meta:
        db_table = 'blog'
        verbose_name_plural = '文档信息'


class Article(models.Model):
    """文档内容表"""
    content = models.TextField('内容', max_length=1073741823)  # 1G，TextField为LONGTEXT类型，最大长度4GB（4294967295Byte）
    markdown_content = models.TextField('Markdown内容', max_length=1073741823, help_text='使用Markdown编辑器编写的内容')
    # 一对一博客信息表，反向查询字段名：blog

    def __str__(self):
        return f'对应文档：{self.blog.title}'

    class Meta:
        db_table = 'article'
        verbose_name_plural = '文档内容'


class Classify(models.Model):
    """文档分类表"""
    user = models.ForeignKey(UserProfile, verbose_name='所属用户', related_name='classify')
    name = models.CharField('分类名称', max_length=200)
    sort = models.IntegerField('排序', null=True, blank=True)
    is_show = models.BooleanField('是否显示', default=True)
    data_created = models.DateTimeField('创建日期', auto_now_add=True)
    # 多对多博客信息表，反向查询字段名：blog

    def __str__(self):
        return parse.unquote(self.name)

    class Meta:
        db_table = 'classify'
        verbose_name_plural = '文档分类'
        unique_together = ('user', 'name')


class Comment(models.Model):
    """文档评论表"""
    blog = models.ForeignKey('BlogInfo', verbose_name='被评文档', related_name='comment')
    user = models.ForeignKey(UserProfile, verbose_name='评论者', related_name='comment')
    reply = models.ForeignKey('self', verbose_name='回复', null=True, blank=True, help_text='自关联，为空即无回复')
    content = models.TextField('评论内容', max_length=1073741823)
    is_delete = models.BooleanField('是否删除', default=False)
    comment_date = models.DateTimeField('评论日期', auto_now_add=True)

    def __str__(self):
        return parse.unquote(self.content)

    class Meta:
        db_table = 'comment'
        verbose_name_plural = '评论'


class ArticleImg(models.Model):
    """用于存储文档内容中的图片"""
    user = models.ForeignKey(UserProfile, verbose_name='所属用户', related_name='article_img')
    image = models.ImageField(upload_to='ai/%Y-%m')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image

    class Meta:
        db_table = 'article_img'
        verbose_name_plural = '文档图片'


"""
数据迁移：
python manage.py makemigrations
python manage.py migrate


删库重建：
drop database hlwd;
create database hlwd charset utf8;
"""