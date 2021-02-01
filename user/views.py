from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View  # CBV继承类
from django.contrib import auth  # 认证模块
from django.urls import reverse  # 反转路由
from django.views.decorators.csrf import csrf_protect  # 装饰器，指定视图必须经过csrf校验
from django.utils.decorators import method_decorator  # CBV装饰器，用法：@method_decorator(wrapper)，装饰到类方法上

from user import models
from user import forms  # 自定义的Form组件
from tools.img_code import AuthCode  # 自定义图片验证码
from config.settings import FONT_FILE_PATH  # 字体文件路径
from config.settings import SITE_NAME, LAYOUT_TITLE  # 站点名称配置



class RegLogin(View):
    """用户登录/注册"""

    local_title = None

    def get(self, request):
        # 判断当前访问的页面是否为注册页面
        reg = True if request.GET.get('page') else False
        return render(request, 'reg_login.html',
                      {'reg_form': forms.RegForm(), 'login_form': forms.LoginForm(), 'captcha': self.set_code(), 'reg': reg,
                       'site_name': SITE_NAME, 'layout_title': self.local_title or LAYOUT_TITLE})


    @method_decorator(csrf_protect)
    def post(self, request):
        self.reg_form, self.login_form = forms.RegForm(), forms.LoginForm()  # 先准备好Form对象
        page = request.POST.get('page')
        if hasattr(self, page):  # 用户注册 或 用户登录
            return getattr(self, page)()
        return redirect('auth:logout')


    # 用户注册的逻辑
    def reg(self):
        # 先校验验证码是否正确
        return HttpResponse("暂时开放，联系管理员：zhuyk4@lenovo.com")
        captcha = self.request.POST.get('captcha', False)
        if captcha != self.request.session.get('reg_captcha', None):
            return render(self.request, 'reg_login.html',
                          {'reg_form': self.reg_form, 'login_form': self.login_form,
                           'captcha_err': '验证码错误', 'captcha': self.set_code(), 'reg': True})

        # 验证码校验通过后删除该session键值对
        del self.request.session['reg_captcha']

        # 校验数据
        reg_form = forms.RegForm(self.request.POST)
        if reg_form.is_valid():  # 校验，成功校验数据后，才可执行reg_form.cleaned_data
            obj = reg_form.save(commit=False)  # Form组件自带的方法，commit=False表示稍后通过obj.save()方法保存数据
            obj.set_password(obj.password)  # 设置用户密码
            obj.nickname = obj.username  # 设置字段信息
            obj.save()  # 保存
            return render(self.request, 'reg_login.html',
                          {'reg_form': reg_form, 'login_form': self.login_form, 'captcha': self.set_code(),
                           'reg_by': reg_form.cleaned_data.get('username')})

        # 数据校验未通过：
        return render(self.request, 'reg_login.html',
                      {'reg_form': reg_form, 'login_form': self.login_form, 'captcha': self.set_code(), 'reg': True})


    # 用户登陆的逻辑
    def login(self):
        next_url = self.request.GET.get('next')
        login_form = forms.LoginForm(self.request.POST)
        if login_form.is_valid():
            user = auth.authenticate(self.request, **login_form.cleaned_data)  # 认证用户
            if user:
                login_form.cleaned_data.get('freeze_mode') == 'False' and self.request.session.set_expiry(0)  # 取消下次自动登录
                auth.login(self.request, user)  # 生成session数据
                if next_url:
                    return redirect(next_url)
                return redirect(reverse('home', kwargs={'blog_path': self.request.user.blog_path}))
            return render(self.request, 'reg_login.html',
                          {'reg_form': self.reg_form, 'login_form': login_form,
                           'login_err': '用户名或密码错误', 'captcha': self.set_code()})

        # 数据校验未通过：
        return render(self.request, 'reg_login.html',
                      {'reg_form': self.reg_form, 'login_form': login_form, 'captcha': self.set_code()})


    # 用于生成并记录图片验证码
    def set_code(self):
        obj = AuthCode(font_path=FONT_FILE_PATH)  # 生成图片验证码
        self.request.session['reg_captcha'] = ''.join(obj.get_code())  # 将验证码内容存入session
        return obj.get_memory_img_data()  # 返回验证码数据（base64）



def logout(request):
    """注销"""
    auth.logout(request)
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(reverse('auth:reg_login'))



def is_user_exists(request):
    """# 注册/登录时验证用户是否存在"""
    if request.is_ajax():
        username = request.POST.get('username')
        if models.UserProfile.objects.filter(username=username):  # 如果用户存在
            return JsonResponse(True, safe=False)
    return JsonResponse(False, safe=False)



def freebsd_root(request):
    return HttpResponse('遗忘密码，联系管理员：zhuyk4@lenovo.com')
