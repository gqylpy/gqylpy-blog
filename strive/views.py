import re
import json
import uuid
from urllib import parse
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View  # CBV继承类
from django.urls import reverse  # 反转路由
from django.utils.safestring import mark_safe  # 安全的字符串
from django.contrib.auth.decorators import login_required  # 用于校验用户是否登录的装饰器
from django.utils.decorators import method_decorator  # CBV装饰器，用法：@method_decorator(wrapper)，装饰到类方法上
from django.views.decorators.csrf import csrf_exempt  # 装饰器，排除csrf校验
from django.db import transaction  # 事务
from django.db.models import Max  # 聚合函数

from blog import models
from blog.models import BLOG_TYPE  # 文档分类
from config.settings import MEDIA_URL  # Meida配置
from config.settings import IS_EXPERT, IS_MUSER, CODE_THEME  # Markdown编辑文档样式
from config.settings import ALLOW_UPLOAD_FILE_SUFFIX_RE, MAX_UPLOAD_FILE_SIZE  # 上传文件规则
from config.settings import ARTICLE_DESCRIPTION_LENGTH  # 文档描述长度



class Strive(View):
    """写文档"""

    @method_decorator(login_required)
    def get(self, request, id=''):
        u = self.request.user

        # 判断当前用户是否有此id的文档
        if id and not models.BlogInfo.objects.filter(id=id, user=u):
            return redirect(reverse('strive:strive'))

        # 准备传入html页面的数据
        context = {
            'userinfo': self.set_userinfo(u),
            'editor': self.set_editor(u, id)
        }

        return render(request, 'strive.html', context)


    def set_userinfo(self, u):
        """设置用户信息"""
        return mark_safe(json.dumps({
            'avatar': f'/{MEDIA_URL}{str(u.avatar)}',  # 头像
            'name': u.nickname,  # 昵称
            'blogurl': f'/{u.blog_path}',  # 用户主页
            'isexpert': IS_EXPERT,  # 是否为专家（为专家者，头像带特效）
            'ismuser': IS_MUSER,  # 是否为管理员（为管理员者，有回到文档管理链接）
            'musername': u.username,  # 用户名称
        }))


    def set_editor(self, u, id):
        """设置编者信息"""
        return mark_safe({
            'codeTheme': CODE_THEME,  # 代码类型（代码块区分颜色）
            'blogTypes': [{'value': number, 'name': name} for number, name in BLOG_TYPE],  # 对数据表中所有文档的分类
            'categoriesOpts': [parse.unquote(article.name) for article in models.Classify.objects.filter(user=u)],  # 用户的个人文档分类
            'articleId': id
        })



class SaveArticle(View):
    """发布/保存文档"""

    @method_decorator(csrf_exempt)  # 发现csrf_exempt必须挂在dispatch方法上，挂在post方法上不生效！
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():  # 如果用户未登录（在写文档页面内无法跳转，所以就这么做了）
            return self.set_response_data(request.POST.get('id'), error='未登录')
        return super().dispatch(request, *args, **kwargs)


    @method_decorator(login_required)
    def post(self, request):
        # 获取要保存到数据库的数据
        save_data = self.set_save_data()
        id, classify = save_data.pop('id'), save_data.pop('classify')  # 博客id / ''，分类
        markdown_content, content = save_data.pop('markdown_content'), save_data.pop('content')  # 文档内容
        draft, user = save_data.get('draft'), save_data.get('user')  # draft-是否为草稿，user-用户对象

        # 开始添加/查询数据
        try:
            with transaction.atomic():  # 事务
                # 先获取用户分类最大的排序值，如果该用户没有分类，则排序值为0
                sort_value = models.Classify.objects.filter(user=user).values('sort').aggregate(max=Max('sort')).get('max') or 0
                # 前端传过来的分类是以","逗号分隔的

                # 1.设置个人分类
                classify_list = []
                for name in parse.unquote(classify).split(','):
                    if name:
                        name = parse.quote(name)
                        # 如果存在则查询，否则添加并查询
                        classify_obj, is_add = models.Classify.objects.get_or_create(name=name, user=user)
                        # 如果上一步骤为添加，则再写入相应的数据
                        if is_add:
                            classify_obj.is_show = False if draft else True  # 如果当前文档为草稿，则前端不显示该分类
                            sort_value += 1
                            classify_obj.sort = sort_value  # 排序值
                        classify_obj.save()
                        classify_list.append(classify_obj)

                # 2.添加／更新文档
                if id:
                    blog_obj_list = models.BlogInfo.objects.filter(id=id)
                    blog_obj_list.update(**save_data)
                    blog_obj = blog_obj_list.first()
                    models.Article.objects.filter(blog=id).update(markdown_content=markdown_content, content=content)
                    if not save_data['is_draft']:
                        models.BlogInfo.objects.filter(id=id).update(release_date=datetime.now())
                else:
                    article_obj = models.Article.objects.create(markdown_content=markdown_content, content=content)
                    blog_obj = models.BlogInfo.objects.create(content=article_obj, **save_data)

                # 3.设置文档分类
                blog_obj.classify.set(classify_list)
            response_data = self.set_response_data(blog_obj.id, f'/{user.blog_path}/{blog_obj.id}')

        except Exception:
            response_data = self.set_response_data(id, error='事务执行失败，请重试！')

        return response_data


    def set_response_data(self, id, url=None, error=None):
        """准备发送给前端的数据"""
        return JsonResponse({
            'data': {
                'id': id,
                'url': url
            },
            'error': error,
            'status': False if error else True
        })


    def set_save_data(self):
        """获取并分析要保存到数据库中的数据"""
        d, u = self.request.POST, self.request.user

        # QueryDict对象默认是不可变的，设置属性 _mutable = True 使其可变
        # d._mutable = True

        # 未发现用处
        # articleedittype = urllib.parse.unquote(d.get('articleedittype'))  # 文档编辑类型
        # Description = urllib.parse.unquote(d.get('Description'))  # 描述

        try:
            # 提取描述信息
            content = parse.unquote(d.get('content'))
            rep_list = re.findall(r'\<.+?\>', content, re.S)
            for rep in rep_list:
                content = content.replace(rep, '')
            content = content.replace('\n', '').replace('\t', '').replace(' ', '').replace('&nbsp;', '')
            description = parse.quote(content[:ARTICLE_DESCRIPTION_LENGTH])

            # 即将写入数据库的数据
            return {
                'id': d.get('id'),
                'title': d.get('title'),
                'markdown_content': d.get('markdowncontent'),
                'content': d.get('content'),
                'description': description,  # 描述
                'is_private': True if d.get('private') else False,  # 是否私密
                'tags': d.get('tags'),  # 标签
                'classify': d.get('categories'),  # 个人分类（","分割）
                'channel': d.get('channel') or 5,  # 总体分类 / 默认为其它
                'type': d.get('type'),  # 文档类型
                # 'is_draft': self.is_draft(d.get('id'), d.get('status')),  # 是否为草稿
                'is_draft': True if d.get('status') == '2' else False,  # 是否为草稿
                'user': u,  # 用户对象
            }
        except Exception:
            return self.set_response_data(d.get('id'), error='参数有误')


    def is_draft(self, id, status):
        """
        判断当前编辑的文档是否为草稿
        情况：
            1.没有ID，状态为0/64，——发布
            2.没有ID，状态为2，——保存
            3.有ID，状态为0/64，——发布
            4.有ID，状态为2，——保存
        思路：
            if ID:
                if status == '2':
                    保存
                else:
                    发布
            else:
                if status == '2':
                    发布
                else:
                    保存
        编辑文档走的是发布流程
        """
        if id:
            draft = True if status == '2' else False
        else:
            draft = True if status == '2' else False
        return draft



class GetArticle(View):
    """获取文档信息"""

    @method_decorator(login_required)
    def get(self, request):
        id, user = request.GET.get('id'), request.user

        # 获取文档信息
        blog_obj = models.BlogInfo.objects.filter(id=id, user=user).first()

        # 文档存在则返回文档信息，否则信息全部为空
        return self.set_data(blog_obj) if blog_obj else redirect(reverse('strive:strive'))


    def set_data(self, queryset):
        """准备传给前端的数据"""
        return JsonResponse({
            'data': {
                'id': queryset.id,
                'title': parse.unquote(queryset.title),
                'markdowncontent': parse.unquote(queryset.content.markdown_content),
                'private': queryset.is_private,
                'tags': parse.unquote(queryset.tags),
                'categories': ','.join([parse.unquote(classify.name) for classify in queryset.classify.all()]),
                'channel': queryset.channel,
                'type': queryset.type,
                'status': 2 if queryset.is_draft else 0  # 2-发布的文档 0-草稿
            },
            'error': '',
            'status': True
        })



class UploadImage(View):
    """上传文档图片"""

    @method_decorator(csrf_exempt)  # 发现这个csrf_exempt装饰器必须挂在dispatch方法上，挂在post方法上不生效！
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    @method_decorator(login_required)
    def post(self, request):
        img, user = request.FILES.get('file'), request.user

        # 判断文件大小是否被允许
        if len(img) > MAX_UPLOAD_FILE_SIZE:
            return self.set_response_data(f'File size not exceeding {ALLOW_UPLOAD_FILE_SUFFIX_RE}M', 0)

        # 判断文件后缀是否被允许
        suffix = re.findall(ALLOW_UPLOAD_FILE_SUFFIX_RE, img.name, re.I)  # re.I：忽略大小写匹配

        # 如果被允许，则存储图片数据
        if suffix:
            img.name = f'{str(uuid.uuid4())}.{suffix[0].lower()}'  # 一定要改img.name，下一行的image=img会用到img.name的值
            img_obj = models.ArticleImg.objects.create(user=user, image=img)
            return self.set_response_data(f'/{MEDIA_URL}{img_obj.image}')

        # 否则的：
        return self.set_response_data('A suffix that is not allowed!', 0)


    def set_response_data(self, img_url=None, result=1):
        """准备发送给前端的数据"""
        return JsonResponse({
            'content': img_url,
            'result': result,
            # 'callback': None,  # 暂未发现用处的参数
            # 'data': None,
            # 'vote': 0,
            # 'url': img_url,
            # 'uploaded': 1
        })
