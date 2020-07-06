# 自定义filters

from django import template
from config.settings import MEDIA_URL

register = template.Library()


@register.filter(name='user_avatar')
def query_user_avatar(request):
    """
    设置用户头像路径
    :param request: 响应对象
    :return: 用户头像完整路径
    """
    return f'/{MEDIA_URL}{request.user.avatar}'


@register.filter(name='next_url')
def set_next_url(request):
    """
    设置返回URL
    :param request: 响应对象
    :return: 完整的返回URL
    """
    return f'?next={request.get_full_path()}'


@register.filter(name='add_space')
def add_space(string: str):
    """让字符串中的每个字符以空格分割"""
    new_str = ''
    for i in string:
        new_str += f' {i}'
    return new_str
