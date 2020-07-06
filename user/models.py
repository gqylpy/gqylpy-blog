from django.db import models
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        username = self.normalize_email(username)
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, password, **extra_fields)


# A few helper functions for common logic between User and AnonymousUser.
def _user_get_all_permissions(user, obj):
    permissions = set()
    for backend in auth.get_backends():
        if hasattr(backend, "get_all_permissions"):
            permissions.update(backend.get_all_permissions(user, obj))
    return permissions


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False


# ========================================================================================================================
# =====================================其它代码可以不管，更改下面的字段等信息就可以了=====================================
# ========================================================================================================================

class Attention(models.Model):
    """用户关注表"""
    from_user = models.ForeignKey('UserProfile', verbose_name="关注者", related_name='idol')
    to_user = models.ForeignKey('UserProfile', verbose_name="被关注者", related_name='bean_vermicelli')
    attention_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}'

    class Meta:
        db_table = 'attention'
        verbose_name_plural = '用户关注表'
        unique_together = ('from_user', 'to_user')


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """用户认证表"""
    username = models.CharField("用户名", max_length=32, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_("是否可以登录到管理站点"))
    is_active = models.BooleanField(default=True, help_text=("是否激活"))
    nickname = models.CharField("昵称", max_length=32)
    # descriptor = models.TextField("描述",max_length=2000, null=True, blank=True)  # LONGTEXT类型，最大支持4GB
    avatar = models.ImageField("头像", upload_to="ua", default='ua/default.jpg')  # 切勿更改，在 edit.views.UploadAvatarView类中有手动指定ua操作
    blog_path = models.CharField("主页地址", max_length=255, unique=True, help_text="用户主页地址，例如：http://106.13.73.98/博客地址名")
    # gender = models.CharField("性别", choices=(("male", "男"), ("female", "女")), max_length=8, null=True, blank=True)
    # birthday = models.DateField("生日", null=True, blank=True, help_text="日期格式：YYYY-MM-DD，相当于Python中的datetime.date()实例")
    email = models.EmailField("邮箱", max_length=255)  # EmailField:字符串类型，Django Admin以及ModelForm中提供验证机制
    date_joined = models.DateTimeField("加入日期", auto_now_add=True)

    USERNAME_FIELD = 'username'  # 你必须指定用户名字段
    # REQUIRED_FIELDS = []  # 还可以指定必填字段

    class Meta:
        db_table = 'user'  # 指定数据库中的表名称
        verbose_name_plural = '用户信息'  # 管理站点中显示的表名称


# 迁移数据后，你会发现数据库表字段中的前3个字段为：password、last_login、is_superuser
# 不必惊慌，这是Django做的，认证系统中会用到这3个字段

# 最后，在settings.py文件中指定此类：
    # AUTH_USER_MODEL = 'App名称.UserProfile'

# ========================================================================================================================
# ========================================================================================================================


    def __str__(self):  # __unicode__ on Python 2
        return self.username  # 该返回值会作为认证方法 authenticate 以及 request.user 的返回值

    def get_full_name(self):
        # The user is identified by their email address
        return self.nickname

    def get_short_name(self):
        # The user is identified by their email address
        return self.username

    def has_perm(self, perm, obj=None):
        #     "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always

        if self.is_active and self.is_superuser:
            return True
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        #     "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        #     "Does the user have permissions to view the app `app_label`?"
        #     Simplest possible answer: Yes, always
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)

    objects = UserManager()


# 数据迁移：
# python manage.py makemigrations  记录更改
# python manage.py migrate  开始迁移
