import re
import json
from urllib import parse  # URL编/解码工具

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View  # CBV继承类
from django.contrib.auth.decorators import login_required  # 用于校验用户是否登录的装饰器
from django.utils.decorators import method_decorator  # CBV装饰器，用法：@method_decorator(wrapper)，装饰到类方法上
from django.db.models import Count, Sum, F, Q  # 聚合函数
from django.db import transaction  # 事务
# from django.views.decorators.csrf import ensure_csrf_cookie  # 装饰器，强制设置csrf token到cookie
# from django.middleware.csrf import rotate_token  # CsrfViewMiddleware中间件中提供的更新csrf token的接口

# rest_framework 相关：
from rest_framework.views import APIView  # DRF CBV
from rest_framework.response import Response  # DRF 响应对象
from rest_framework.pagination import PageNumberPagination  # 内置的分页类
from blog.serializers import ArticleInfoSerializer, ClassifySerializer  # 自定义的序列化类

from blog import models
from user.models import UserProfile, Attention
from blog.models import BLOG_TYPE  # 对数据表中所有文档的分类/首页展示的分类
from config.settings import MEDIA_URL  # Meida配置
from config.settings import ERROR_INFO  # 通用报错信息
from config.settings import GLOBAL_QUERY_FIELD_LIST  # 定义可被查询的数据库字段
from config.settings import SITE_NAME, LAYOUT_TITLE, LAYOUT_TITLE_MAX_LENGTH  # 站点名称配置


def home(request, blog_path):
    """返回用户主页"""
    if request.method == 'GET':
        local_title = None
        # 根据传入的主页地址名，来获取用户id并返回
        user_obj = UserProfile.objects.filter(blog_path=blog_path).first()
        # 用户存在，则返回用户id
        if user_obj:
            return render(request, 'home.html',
                          {'user_id': user_obj.id, 'site_name': SITE_NAME, 'layout_title': local_title or LAYOUT_TITLE})
    return HttpResponse(json.dumps(ERROR_INFO, ensure_ascii=False))  # 这写，便可显示中文


def index(request):
    """返回站点首页"""
    # return redirect('http://www.gqylpy.com')
    if request.method == 'GET':
        local_title = None
        return render(request, 'index.html', {'article_type': BLOG_TYPE, 'search_global': True, 'site_name': SITE_NAME,
                                              'layout_title': local_title or LAYOUT_TITLE})
    return JsonResponse(ERROR_INFO)


class ArticleInfo(View):
    """返回查看文档页面"""

    def get(self, request, blog_path, article_id):
        try:
            # 获取上一个页面
            from_page = request.GET.get('from', '')

            # 获取用户id
            # 如果访问者是本人，则可查看本人隐私的、删除的文档
            if request.user.is_authenticated() and request.user.blog_path == blog_path:
                user_id = models.BlogInfo.objects.filter(id=article_id, user=request.user,
                                                         user__blog_path=blog_path).values('id', 'user_id').first().get(
                    'user_id')
            else:
                user_id = models.BlogInfo.objects.filter(id=article_id, user__blog_path=blog_path, is_private=False,
                                                         is_draft=False, is_delete=False).values('id',
                                                                                                 'user_id').first().get(
                    'user_id')  # 为空时，会出现：'NoneType'报错

            # 设置网页标题
            ar_title = models.BlogInfo.objects.filter(id=article_id, user__blog_path=blog_path).values(
                'title').first().get('title')
            nickname = models.UserProfile.objects.filter(id=user_id).values('nickname').first().get('nickname')
            ar_title = parse.unquote(ar_title)
            ar_title = ar_title if len(ar_title) <= LAYOUT_TITLE_MAX_LENGTH else ar_title[
                                                                                 :LAYOUT_TITLE_MAX_LENGTH] + '...'

            # 获取文档内容
            ar_content = self.fetch_content(article_id, blog_path)

            # 如果访问者不是本人，则将访问量加1
            if not request.user.is_authenticated or not request.user.blog_path == blog_path or blog_path == 'aiops':
                models.BlogInfo.objects.filter(id=article_id).select_for_update().update(visit=F('visit') + 1)
            # select_for_update()：行级锁，所有匹配的行将被锁定，直到事务执行结束
            # 一般情况下，如果其它事务锁定了相关行，那么本查询将被阻塞，直到锁被释放
            # 如果不要使查询被阻塞，添加参数 nowait=True
            # 如果其它事务特有冲突的锁，互斥锁，那么查询将引发 DatabaseError异常
            # 你也可以使用参数 skip_locked=True 忽略锁定的行
            # 但要注意的是：nowait=True 与 skip_locked=True 是互斥的，同时使用将抛出异常

            return render(request, 'show_article.html',
                          {'ar_content': ar_content, 'title': f'{ar_title} - {nickname}', 'user_id': user_id,
                           'article_id': article_id, 'blog_path': blog_path, 'site_name': SITE_NAME,
                           'layout_title': ar_title or LAYOUT_TITLE, 'from_page': from_page})

        except Exception:
            return HttpResponse(json.dumps(ERROR_INFO, ensure_ascii=False))  # 这样写，便可显示中文

    def fetch_content(self, article_id, blog_path):
        # 获取文档内容
        blog_obj = models.BlogInfo.objects.filter(id=article_id, user__blog_path=blog_path).first()

        # 如果该文有访问限制：
        if blog_obj.access_password or blog_obj.is_private or blog_obj.is_draft or blog_obj.is_delete:
            content = ''
        else:
            content = parse.unquote(blog_obj.content.content)

        # return re.sub(r'<.+?>', '', content, flags=re.S)
        return content


class ArticleListView(APIView):
    """返回文档列表"""

    def post(self, request):
        try:
            self.user_id = request.data.get('user_id', 0)

            # 判断访问者是否为本人
            self.is_self = True if str(request.user.id) == self.user_id else False

            # 获取文档和分页链接
            article_list, html_context = self.get_data()

            return Response({
                'self': self.is_self,
                'article_list': article_list,
                'html_context': html_context,
            })

        except Exception:
            return Response(ERROR_INFO)

    def get_data(self):
        """获取文档"""

        # 1.获取分类id, 获取排序方式
        classify_id, sort_method = self.request.data.get('classify_id', 0), self.request.data.get('sort_method',
                                                                                                  'release_date')
        # 2.按查找条件提取文档
        if classify_id:
            article_list = models.BlogInfo.objects.filter(user_id=self.user_id, is_private=False, is_draft=False,
                                                          is_delete=False, classify=classify_id)
        else:
            article_list = models.BlogInfo.objects.filter(user_id=self.user_id, is_private=False, is_draft=False,
                                                          is_delete=False)

        try:
            sort_article_list = article_list.order_by(f'-{sort_method}')
        except Exception:
            sort_article_list = article_list.order_by('-release_date')

        # 4.最后进行分页
        page_obj = PageNumberPagination()
        page_sort_article_list = page_obj.paginate_queryset(sort_article_list, self.request)

        return ArticleInfoSerializer(is_show_article=None, instance=page_sort_article_list,
                                     many=True).data, page_obj.get_html_context()  # many=True：表示序列化多条数据


class UserInfoView(APIView):
    """返回用户信息"""

    def post(self, request):
        try:
            self.user_id = request.data.get('user_id', 0)
            self.is_self = True if str(request.user.id) == self.user_id else False  # 判断访问者是否为本人

            return Response({
                'self': self.is_self,
                'userinfo': self.get_userinfo(),  # 获取用户信息
                'classify_list': self.get_classify_list(),  # 获取分类
            })
        except Exception:
            return Response(ERROR_INFO)

    def get_userinfo(self):
        """获取用户信息"""

        # 获取用户的所有文档
        blog_list = models.BlogInfo.objects.filter(user_id=self.user_id, is_private=False, is_draft=False,
                                                   is_delete=False)

        # 统计数量
        data = blog_list.aggregate(article_count=Count('id'), praise_count=Sum('praise'),
                                   visit_count=Sum('visit'))  # type: dict
        data.update(blog_list.filter(comment__is_delete=False).aggregate(comment_count=Count('comment')))
        # 评论要与其它的分开统计，否则会出现数据混乱

        # 用户没有文档时，Sum()求和的值为None
        for k, v in data.items():
            if v is None:
                data[k] = 0

        # 获取用户信息（昵称和头像），并加入data
        data.update(UserProfile.objects.filter(id=self.user_id).values('nickname', 'avatar').first())
        data['avatar'] = f'/{MEDIA_URL}{data.get("avatar")}'  # 设置用户头像路径，完整路径

        # 获取所有粉丝，并将粉丝总数加入data
        data.update(Attention.objects.filter(to_user_id=self.user_id).aggregate(bean_count=Count('id')))

        # 判断访问者是否已关注该用户（如果访问者是本人，就不添加此k-v）
        if not self.is_self:
            att_obj = Attention.objects.filter(from_user=self.request.user.id).first()
            data['is_attention'] = True if att_obj else False

        return data

    def get_classify_list(self):
        """获取分类"""
        classify_list = models.Classify.objects.filter(user_id=self.user_id, is_show=True).order_by('sort')
        return ClassifySerializer(classify_list, many=True).data


class DoFollowView(APIView):
    """用户关注的逻辑"""

    @method_decorator(login_required)
    def post(self, request):
        try:
            from_user_id, to_user_id = request.user.id, request.data.get('to_user')

            # 不可自关注
            if from_user_id == to_user_id:
                return Response({'status': False, 'msg': '不可以关注自己'})

            # 添加或删除关注关系
            obj, created = Attention.objects.get_or_create(from_user_id=from_user_id, to_user_id=to_user_id)

            if created:
                msg = '已关注'
                code = 1
            else:
                obj.delete()  # 删除关注
                msg = '关注'
                code = 0

            return Response({'status': True, 'code': code, 'msg': msg})

        except Exception:
            return Response(ERROR_INFO)


class ArticleInfoView(APIView):
    """获取文档详细内容"""

    def post(self, request):
        try:
            user_id, article_id = request.data.get('user_id', 0), request.data.get('article_id', 0)
            from_page = request.data.get('from_page', '')

            # 判断访问者是否为本人
            is_self = True if request.user.id and str(request.user.id) == user_id else False
            # request.user.id：无用户时返回值为None，
            # if request.user.id：以防止传入user_id为None进行窃取

            # 获取文档
            # 如果访问者是本人，则可查看本人隐私的、删除的文档
            if is_self:
                article_obj = models.BlogInfo.objects.filter(id=article_id, user_id=user_id, user=request.user).first()
            else:
                article_obj = models.BlogInfo.objects.filter(id=article_id, user_id=user_id, is_private=False,
                                                             is_draft=False, is_delete=False).first()

            # 该文档是否有访问密码
            access_restriction = True if article_obj.access_password else False

            # 进行序列化
            ser_obj = ArticleInfoSerializer(is_show_article=True, instance=article_obj, from_page=from_page)

            return Response({
                'self': is_self,
                'access_restriction': access_restriction,
                'data': ser_obj.data,
            })

        except Exception:
            return Response(ERROR_INFO)


class ArticleContentView(APIView):
    """获取文档内容，有密码时"""

    def post(self, request):
        try:
            article_id, pwd = request.data.get('article_id'), request.data.get('pwd')
            article_obj = models.BlogInfo.objects.filter(id=article_id, access_password=pwd).first()
            if article_obj:
                return Response({'state': True, 'data': parse.unquote(article_obj.content.content)})
            return Response({'state': False, 'data': None, 'msg': 'article_id or pwd Error.'})

        except Exception:
            return Response(ERROR_INFO)


class CommentView(APIView):
    """文档评论"""

    @method_decorator(login_required)
    def post(self, request):
        try:
            # 获取评论id、文档id，以及评论内容
            com_id, article_id = request.data.get('com_id', 0), request.data.get('article_id', 0)
            com_content = parse.quote(request.data.get('com_content').strip())
            uid = request.user.id

            # 如果是回复，否则是评论
            if com_id:
                models.Comment.objects.create(reply_id=com_id, blog_id=article_id, user_id=uid, content=com_content)
            else:
                models.Comment.objects.create(blog_id=article_id, user_id=uid, content=com_content)

            return Response(True)

        except Exception:
            return Response(False)


class PraiseView(APIView):
    """文档点赞"""

    def post(self, request):
        try:
            # 获取被点赞文档的id
            article_id = request.data.get('article_id')

            # 将点赞量加1
            models.BlogInfo.objects.filter(id=article_id).select_for_update().update(praise=F('praise') + 1)
            # select_for_update()：行级锁，所有匹配的行将被锁定，直到事务执行结束
            # 一般情况下，如果其它事务锁定了相关行，那么本查询将被阻塞，直到锁被释放
            # 如果不要使查询被阻塞，添加参数 nowait=True
            # 如果其它事务特有冲突的锁，互斥锁，那么查询将引发 DatabaseError异常
            # 你也可以使用参数 skip_locked=True 忽略锁定的行
            # 但要注意的是：nowait=True 与 skip_locked=True 是互斥的，同时使用将抛出异常

            return Response({'status': True, 'msg': 'ok'})

        except Exception:
            return Response({'status': False, 'msg': '点赞失败'})


class IndexArticleListView(APIView):
    """获取首页文档列表"""

    def post(self, request):
        try:
            # 获取文档类型，排序方式
            article_type, sort_method = int(request.data.get('article_type')), request.data.get('sort_method')

            # 获取文档列表
            if article_type:
                article_list = models.BlogInfo.objects.filter(channel=article_type, is_private=False,
                                                              is_draft=False, is_delete=False,
                                                              access_password__isnull=True)  # # ~Q(user_id=1),
            else:
                article_list = models.BlogInfo.objects.filter(is_private=False, is_draft=False,
                                                              is_delete=False, access_password__isnull=True)

            # 3.对文档进行排序
            try:
                sort_article_list = article_list.order_by(f'-{sort_method}')
            except Exception:
                sort_article_list = article_list.order_by('-release_date')

            # 4.最后进行分页
            page_obj = PageNumberPagination()
            page_sort_article_list = page_obj.paginate_queryset(sort_article_list, request)

            return Response({
                'article_list': ArticleInfoSerializer(is_show_article=False, is_index=True,
                                                      instance=page_sort_article_list, many=True).data,
                'html_context': page_obj.get_html_context(),
            })

        except Exception:
            return Response(ERROR_INFO)


class SreachArticleView(APIView):
    """查询文档"""

    QUERY_FIELD_LIST = []  # 定义可被查询的数据库字段

    def post(self, request):
        try:
            # 获取被查询的用户的id，和查询关键字
            user_id, keyword = int(request.data.get('user_id')), request.data.get('keyword', '')

            # 查询者是否为本人
            is_self = True if request.user.id == user_id else False

            # 如果有用户id，则查该用户文档，否则查全站，且可查自己的全部文档
            field_dict = {} if is_self else {'is_private': False, 'is_draft': False, 'is_delete': False}
            user_id and field_dict.setdefault('user_id', user_id)
            query_list = models.BlogInfo.objects.filter(self.get_search_content(keyword), **field_dict)

            # 进行序列化
            query_list = ArticleInfoSerializer(is_show_article=False, instance=query_list.order_by('-release_date'),
                                               many=True)

            return Response({
                'data': query_list.data,
                'self': is_self,
                'msg': 'ok',
            })

        except Exception:
            return Response(ERROR_INFO)

    def get_search_content(self, keyword):
        """模糊查询"""
        q = Q()
        q.connector = Q.OR
        for field in self.QUERY_FIELD_LIST or GLOBAL_QUERY_FIELD_LIST:
            q.children.append(Q((f'{field}__contains', parse.quote(keyword))))
        return q
