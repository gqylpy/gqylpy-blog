import os
import json
import uuid
import base64

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required  # 用于校验用户是否登录的装饰器
from django.utils.decorators import method_decorator  # CBV装饰器，用法：@method_decorator(wrapper)，装饰到类方法上
from django.db import transaction  # 事务
from django.db.models import Q  # 聚合函数

# rest_framework 相关：
from rest_framework.views import APIView  # DRF CBV
from rest_framework.response import Response  # DRF 响应对象
from edit import serializers  # 自定义的序列化类
from edit.pagination import PageNumberPg  # 自定义的分页器类

from blog import models
from user.models import Attention
from config.settings import MEDIA_ROOT  # Meida配置
from config.settings import ERROR_INFO  # 通用报错信息
from config.settings import MAX_UPLOAD_FILE_SIZE  # 上传文件规则
from config.settings import SITE_NAME, LAYOUT_TITLE  # 站点名称配置


@login_required
def edit(request):
    """返回编辑页面"""
    if request.method == 'GET':
        local_title = None
        return render(request, 'edit.html', {'site_name': SITE_NAME, 'layout_title': local_title or LAYOUT_TITLE})
    return JsonResponse(ERROR_INFO)


class ArticleListView(APIView):
    """获取文章数据"""

    _TYPE = {
        'open': {'is_private': False, 'is_draft': False, 'is_delete': False},  # 公开的
        'private': {'is_private': True, 'is_draft': False, 'is_delete': False},  # 私密的
        'draft': {'is_draft': True, 'is_delete': False},  # 草稿
        'delete': {'is_delete': True},  # 删除的
    }

    @method_decorator(login_required)
    def post(self, request):
        try:
            # 获取要查询的数据类型
            ar_type = request.data.get('type', 'open')

            # 提取查询条件
            query_con = self._TYPE.get(ar_type)

            # 开始查询数据
            queryset = models.BlogInfo.objects.filter(user=request.user, **query_con).order_by('-release_date')

            # 对查询到的数据集进行分页
            page_obj = PageNumberPg()
            page_data = page_obj.paginate_queryset(queryset, request)

            # 对分页后的数据进行序列化
            ser_obj = serializers.ArticleListSerializer(page_data, many=True)

            return Response({
                'data': {
                    'article_list': ser_obj.data,  # 序列化后的数据
                    'html_context': page_obj.get_html_context(),  # 分页链接
                    'ar_type': ar_type,
                },
                'msg': 'ok',
            })

        except Exception:
            return Response(ERROR_INFO)


class SetArticlePwdView(APIView):
    """设置文章密码"""

    @method_decorator(login_required)
    def patch(self, request):
        try:
            # 提取文章id，和要设置的密码
            id, pwd = request.data.get('id', 0), request.data.get('pwd')

            # 密码不可为空
            if not pwd:
                return Response({'status': False, 'msg': '密码不可为空'})

            # 查询更新数据
            receipt = models.BlogInfo.objects.filter(id=id, user=request.user).update(access_password=pwd)

            # 判断是否更新成功
            ret = {'status': True, 'msg': 'ok'} if receipt else {'status': False, 'msg': '无匹配数据'}

            return Response(ret)

        except Exception:
            return Response(ERROR_INFO)


class DeleteArticlePwdView(APIView):
    """删除文章密码"""

    @method_decorator(login_required)
    def delete(self, request):
        try:
            # 提取文章id
            id = request.data.get('id', 0)

            # 查询更新数据
            receipt = models.BlogInfo.objects.filter(id=id, user=request.user).update(access_password=None)

            # 判断是否更新成功
            ret = {'status': True, 'msg': 'ok'} if receipt else {'status': False, 'msg': '无匹配数据'}

            return Response(ret)

        except Exception:
            return Response(ERROR_INFO)


class DeleteArticleView(APIView):
    """删除文章"""

    @method_decorator(login_required)
    def delete(self, request):
        try:
            # 提取文章id
            id = request.data.get('id', 0)

            # 查询更新数据
            receipt = models.BlogInfo.objects.filter(id=id, user=request.user, is_delete=False).update(is_delete=True)

            # 判断是否更新成功
            ret = {'status': True, 'msg': 'ok'} if receipt else {'status': False, 'msg': '无匹配数据'}

            return Response(ret)

        except Exception:
            return Response(ERROR_INFO)


class RecoverArticleView(APIView):
    """撤销删除文章"""

    method_decorator(login_required)

    def patch(self, request):
        try:
            # 提取文章id
            id = request.data.get('id', 0)

            # 查询更新数据
            receipt = models.BlogInfo.objects.filter(id=id, user=request.user, is_delete=True).update(is_delete=False)

            # 判断是否更新成功
            ret = {'status': True, 'msg': 'ok'} if receipt else {'status': False, 'msg': '无匹配数据'}

            return Response(ret)

        except Exception:
            return Response(ERROR_INFO)


class CommentListView(APIView):
    """获取评论数据"""

    @method_decorator(login_required)
    def post(self, request):
        try:
            # 评论类型的查询条件
            com_type_query_con = {'to_me': {'blog__user': request.user}, 'me_to': {'user': request.user}}

            # 获取要查询的数据类型
            com_type = request.data.get('type', 'to_me')

            # 提取查询条件
            query_con = com_type_query_con.get(com_type, com_type_query_con.get('to_me'))

            # 根据查询条件查询数据
            queryset = models.Comment.objects.filter(**query_con, is_delete=False).order_by('-comment_date')

            # 对查询到的数据进行分页
            page_obj = PageNumberPg()
            page_data = page_obj.paginate_queryset(queryset, request)

            # 对分页后的数据进行序列化
            ser_obj = serializers.CommentListSerializer(page_data, many=True)

            return Response({
                'data': {
                    'comment_list': ser_obj.data,  # 序列化后的数据
                    'html_context': page_obj.get_html_context(),  # 分页链接
                    'com_type': com_type,
                },
                'msg': 'ok',
            })

        except Exception:
            return Response(ERROR_INFO)


class DeleteCommentView(APIView):
    """删除评论"""

    @method_decorator(login_required)
    def delete(self, request):
        try:
            # 获取要删除的评论id，和user对象
            id, u = request.data.get('id'), request.user

            # 查询更新数据
            receipt = models.Comment.objects.filter(Q(user=u) | Q(blog__user=u), id=id, is_delete=False).update(
                is_delete=True)

            # 判断是否更新成功
            ret = {'status': True, 'mes': 'ok'} if receipt else {'status': False, 'msg': '无匹配数据'}

            return Response(ret)

        except Exception:
            return Response(ERROR_INFO)


class AttentionListView(APIView):
    """获取关注数据"""

    @method_decorator(login_required)
    def post(self, request):
        try:
            # 关注类型的查询条件
            all_type_query_con = {'to_me': {'to_user': request.user}, 'me_to': {'from_user': request.user}}

            # 获取要查询的数据类型
            at_type = request.data.get('type', 'to_me')

            # 提取查询条件
            query_con = all_type_query_con.get(at_type, all_type_query_con.get('to_me'))

            # 根据查询条件查询数据
            queryset = Attention.objects.filter(**query_con).order_by('-attention_date')

            # 对查询到数数据进行分页
            page_obj = PageNumberPg()
            page_data = page_obj.paginate_queryset(queryset, request)

            # 对分页后的数据进行序列化
            ser_obj = serializers.AttentionListSerializer(page_data, many=True)

            return Response({
                'data': {
                    'attention_list': ser_obj.data,  # 序列化后的数据
                    'html_context': page_obj.get_html_context(),  # 分页链接
                    'at_type': at_type,
                },
                'msg': 'ok',
            })

        except Exception:
            return Response(ERROR_INFO)


class GetClassifyListView(APIView):
    """获取个人分类数据"""

    @method_decorator(login_required)
    def post(self, request):
        try:
            # 查询该用户的分类数据
            queryset = models.Classify.objects.filter(user=request.user).order_by('sort')

            # 对查询到的数据进行分页
            # page_obj = PageNumberPg()
            # page_data = page_obj.paginate_queryset(queryset, request)

            # 行序列化
            ser_obj = serializers.ClassifyListSerializer(queryset, many=True)

            return Response({
                'data': {
                    'classify_list': ser_obj.data,  # 序列化后的数据
                    # 'html_context': page_obj.get_html_context(),  # 分页链接
                },
                'msg': 'ok',
            })

        except Exception:
            return Response(ERROR_INFO)


class ShowOrConcealClassifyView(APIView):
    """主页显示或隐藏分类"""

    @method_decorator(login_required)
    def patch(self, request):
        try:
            # 获取要修改的分类id，和该分类的当前状态（显示/隐藏）
            id, is_show = request.data.get('id', 0), json.loads(request.data.get('is_show'))

            # 开始修改数据
            receipt = models.Classify.objects.filter(id=id, user=request.user, is_show=is_show).update(
                is_show=not is_show)

            # 判断是否修改成功
            ret = {'status': True, 'msg': 'ok'} if receipt else {'status': False, 'msg': '无匹配数据'}

            return Response(ret)

        except Exception:
            return (ERROR_INFO)


class alterClassifyNameView(APIView):
    """修改分类名称"""

    @method_decorator(login_required)
    def patch(self, request):
        try:
            # 获取要操作的分类id，和当前用户对象
            id, u = request.data.get('id', 0), request.user

            # 先提取要更新的数据
            classify_obj = models.Classify.objects.filter(id=id, user=u).first()

            # 进行反序列化
            ser_obj = serializers.ClassifySer(user=u, instance=classify_obj, data=request.data,
                                              partial=True)  # partial=True：部分校验（即未上传的字段不校验）
            # ! 如果instance=None，则下面的ser_obj.save()将执行 create 方法

            # 开始校验
            if ser_obj.is_valid():
                ser_obj.save()  # 保存数据，其内部将执行 update 方法
                return Response({'status': True, 'msg': 'ok'})

            # 校验不通过，将返回错误信息
            return Response({'status': False, 'msg': ser_obj.errors})

        except Exception:
            return Response(ERROR_INFO)


class DeleteClassifyView(APIView):
    """删除分类（永久删除）"""

    @method_decorator(login_required)
    def delete(self, request):
        try:
            # 获取要删除的分类id
            id = request.data.get('id', 0)

            # 删除数据
            receipt, obj = models.Classify.objects.filter(id=id, user=request.user).delete()

            # 判断是否删除成功
            ret = {'status': True, 'msg': 'ok'} if receipt else {'status': False, 'msg': '无匹配数据'}

            return Response(ret)

        except Exception:
            return Response(ERROR_INFO)


class SetClassifySortView(APIView):
    """设置分类排序"""

    def patch(self, request):
        try:
            # 获取分类id，和动作
            self.id, self.ac = request.data.get('id', 0), request.data.get('ac', 'up')

            # 获取准备操作的，和受影响的数据
            oper_obj, be_oper_obj = self.get_oper_data()

            # 改变排序顺序
            oper_obj.sort, be_oper_obj.sort = be_oper_obj.sort, oper_obj.sort
            # 这里赋值操作写在一行，不会出现数据混乱的情况

            # 事务保存
            with transaction.atomic():
                [obj.save() for obj in (oper_obj, be_oper_obj)]

            return Response({'status': True, 'msg': 'ok'})

        except Exception:
            return Response(ERROR_INFO)

    def get_oper_data(self):
        """获取准备操作的和受影响的数据"""
        u = self.request.user

        # 获取准备操作的数据
        oper_obj = models.Classify.objects.filter(id=self.id, user=u).first()

        # 获取受影响的数据
        if self.ac == 'up':
            be_oper_obj = models.Classify.objects.filter(user=u, sort__lt=oper_obj.sort).order_by('-sort').first()
        else:
            be_oper_obj = models.Classify.objects.filter(user=u, sort__gt=oper_obj.sort).order_by('sort').first()

        return oper_obj, be_oper_obj


class AddClassifyView(APIView):
    """添加分类"""

    @method_decorator(login_required)
    def post(self, request):
        try:
            # 进行反序列化
            ser_obj = serializers.ClassifySer(user=request.user, data=request.data)

            # 开始校验
            if ser_obj.is_valid():
                ser_obj.save()  # 保存数据，其内部将执行 create 方法
                return Response({'status': True, 'msg': 'ok'})

            # 校验不通过，将返回错误信息
            return Response({'status': False, 'msg': ser_obj.errors})

        except Exception:
            return Response(ERROR_INFO)


class GetUserInfoView(APIView):
    """获取用户信息"""

    @method_decorator(login_required)
    def post(self, request):
        try:
            # 序列化，过滤字段
            ser_obj = serializers.UserInfoSerializer(request.user)

            return Response({
                'data': {'userinfo': ser_obj.data},  # 序列化后的数据
                'msg': 'ok'
            })

        except Exception:
            return Response(ERROR_INFO)


class UploadAvatarView(APIView):
    """上传头像"""

    @method_decorator(login_required)
    def patch(self, request):
        try:
            # 获取上传的头像（base数据），和该用户对象
            b64_img, u = request.data.get('file'), request.user

            # 转为字节
            bytes_img = base64.b64decode(b64_img[23:])  # [23:]：去除 data:image/jpng;base64,

            # 文件大小校验
            if len(bytes_img) > MAX_UPLOAD_FILE_SIZE:
                return self.response(False, f'确保文件大小不超过{MAX_UPLOAD_FILE_SIZE}M')

            # 准备存入数据库的文件路径
            save_path = f'ua/{str(uuid.uuid4())}.jpg'

            # 保存
            with transaction.atomic():
                # 保存文件内容到磁盘
                with open(os.path.join(MEDIA_ROOT, save_path), 'wb') as fp:
                    fp.write(bytes_img)
                # 保存文件路径到数据库
                u.avatar = save_path
                u.save()

            return self.response(True, 'ok')

        except Exception:
            return Response(ERROR_INFO)

    def response(self, status, msg):
        return Response({'status': status, 'msg': msg})


class SetNicknameView(APIView):
    """修改昵称"""

    @method_decorator(login_required)
    def patch(self, request):
        try:
            # 进行序列化
            ser_obj = serializers.UserInfoSer(instance=request.user, data=request.data, partial=True)

            # 开始校验
            if ser_obj.is_valid():
                ser_obj.save()  # 保存数据，其内部将执行 update 方法
                return Response({'status': True, 'msg': 'ok'})

            # 校验不通过，将返回错误信息
            return Response({'status': False, 'msg': ser_obj.errors})

        except Exception:
            return Response(ERROR_INFO)


class SetBlogPathView(APIView):
    """修改主页地址"""

    @method_decorator(login_required)
    def patch(self, request):
        try:
            # 进行序列化
            ser_obj = serializers.UserInfoSer(instance=request.user, data=request.data, partial=True)

            # 开始校验
            if ser_obj.is_valid():
                ser_obj.save()
                return Response({'status': True, 'msg': 'ok'})

            # 校验不通过，将返回错误信息
            return Response({'status': False, 'msg': ser_obj.errors})

        except Exception:
            return Response(ERROR_INFO)


class SetUserNameView(APIView):
    """修改用户名"""

    @method_decorator(login_required)
    def patch(self, request):
        try:
            # 进行序列化
            ser_obj = serializers.UserInfoSer(instance=request.user, data=request.data, partial=True)

            # 开始校验
            if ser_obj.is_valid():
                ser_obj.save()
                return Response({'status': True, 'msg': 'ok'})

            # 校验不通过，将返回错误信息
            return Response({'status': False, 'msg': ser_obj.errors})

        except Exception:
            return Response(ERROR_INFO)


class SetEmailView(APIView):
    """修改邮箱"""

    @method_decorator(login_required)
    def patch(self, request):
        try:
            # 进行序列化
            ser_obj = serializers.UserInfoSer(instance=request.user, data=request.data, partial=True)

            # 开始校验
            if ser_obj.is_valid():
                ser_obj.save()
                return Response({'status': True, 'msg': 'ok'})

            # 校验不通过，将返回错误信息
            return Response({'status': False, 'msg': ser_obj.errors})

        except Exception:
            return Response(ERROR_INFO)


class SetUserPwdView(APIView):
    """修改密码"""

    @method_decorator(login_required)
    def patch(self, request):
        try:
            # 获取当前用户对象
            u = request.user

            # 进行序列化
            ser_obj = serializers.UserInfoSer(user=u, instance=u, data=request.data, partial=True)

            # 开始校验
            if ser_obj.is_valid():
                ser_obj.save()
                return Response({'status': True, 'msg': 'ok'})

            # 校验不通过，将返回错误信息
            return Response({'status': False, 'msg': ser_obj.errors})

        except Exception:
            return Response(ERROR_INFO)
