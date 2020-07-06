from django import forms
from user import models
from django.core.exceptions import ValidationError  # 用于返回错误信息
from django.urls.resolvers import RegexURLPattern  # 用于获取项目内的所有url

from config import urls
from config.settings import FORBID_BLOG_PATH  # 主页地址规则


class BaseForm(forms.ModelForm):
    # 重写父类的init方法来批量添加样式
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({"class": "input"})



# 注册Form
class RegForm(BaseForm):

    class Meta:

        # 指定数据表
        model = models.UserProfile

        # 指定要校验的字段，如果指定为 "__all__"，则校验所有的字段；如果指定为列表, 则只校验列表内的字段
        fields = ["username", "blog_path", "password"]

        # 提示信息
        labels = {
            "username": "用户名",
            "blog_path": "主页地址",
            "password": "密码",
        }

        # 自定义错误信息
        error_messages = {
            "username": {
                "required": "请输入用户名",
                "max_length": "用户名最大32字符"
            },
            "blog_path": {
                "required": "请输入主页路径",
                "invalid": "路径格式错误",
            },
            "password": {
                "required": "请输入密码",
            },
        }

        # 自定义插件
        widgets = {
            "username": forms.widgets.TextInput(
                attrs={
                    "id": "reg_username",
                }
            ),
            "blog_path": forms.widgets.TextInput(
                attrs={
                    "id": "reg_blog_path",
                    # "placeholder": "例如：www.hlwd.com/主页地址",
                }
            ),
            "password": forms.widgets.PasswordInput(
                attrs={
                    "id": "reg_password",
                }
            ),  # 指定input框的type类型为password，并添加id属性及值
        }

        # 帮助信息
        help_texts = {}


    # 确认密码
    re_password = forms.CharField(
        label="确认密码",
        error_messages= {
            "required": "",
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                "id": "reg_re_password",
            }
        ),
    )

    # 用于获取项目所有的URL
    def get_all_urls(self, urlpatterns, prev, is_first=False, result=[]):
        if is_first:
            result.clear()
        for item in urlpatterns:
            v = item._regex.strip('^$')
            if isinstance(item, RegexURLPattern):
                result.append(prev + v)
            else:
                self.get_all_urls(item.url_patterns, prev + v)
        return result


    # 校验主页地址格式
    def clean_blog_path(self):
        blog_path = self.cleaned_data.get('blog_path')  # type: str

        # 主页地址不可为空
        if blog_path.isspace():
            raise ValidationError('主页地址不可包含空格')

        # 判断主页地址是否包含被禁用字符
        for i in FORBID_BLOG_PATH:
            if i in blog_path:
                raise ValidationError(f"主页地址不可包含的字符：{[i for i in FORBID_BLOG_PATH]}")

        # 获取项目内所有url，并对所有url进行分析过滤去重
        url_list = self.get_all_urls(urls.urlpatterns, prev='/')
        url_set = set([url.split('/')[1] for url in url_list if '(?P<blog_path>.+)' not in url])

        # 判断主页地址是否为站点地址
        if blog_path in url_set:
            raise ValidationError(f"不可用的地址")

        # 判断主页地址是否已被使用
        if models.UserProfile.objects.filter(blog_path=blog_path):
            raise ValidationError("该地址已被使用")

        return blog_path


    # 验证用户是否存在
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if models.UserProfile.objects.filter(username=username):
            raise ValidationError("用户名已被使用")
        return username


    # 用于校验密码格式
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) is 32:  # 前端用md5加密后的固定长度
            return password
        raise ValidationError("密码格式错误")


    # 用于校验密码一致性
    def clean_re_password(self):
        """
        局部钩子：clean_字段名
        :return: 定义哪个字段的钩子，就得返回哪个字段的值
        """
        password = self.cleaned_data.get("password")
        re_password = self.cleaned_data.get("re_password")
        if not password or password == re_password:  # not password：如果clean_password函数校验失败，则password为空
            return re_password
        raise ValidationError("密码不一致")



# 登录Form
class LoginForm(forms.Form):

    username = forms.CharField(
        label="用户名",
        min_length=1,
        max_length=32,
        error_messages={
            "required": "请输入用户名",
        },
        widget=forms.widgets.TextInput(
            attrs={
                "class": "input",
                "id": "login_username",
            }
        )
    )

    password = forms.CharField(
        label="密码",
        error_messages={
            "required": "请输入密码",
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                "class": "input",
                "id": "login_password"
            }
        )
    )

    # checkbox标签（单选）
    freeze_mode = forms.fields.CharField(
        label=" 下次自动登录",
        required=False,  # 可以为空
        initial="checked",  # 默认选中
        widget=forms.widgets.CheckboxInput(
            attrs={
                'class': 'check',
                'id': 'login_check',
            }
        )
    )


    # 用于验证密码格式
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) == 32:  # 前端用md5加密后的固定长度
            return password
        raise ValidationError('密码格式错误')
