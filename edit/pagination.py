# 局部分页器

from rest_framework import pagination
from config.settings import EDIT_PAGE_SIZE  # 管理页面显示数据的最大条数


class PageNumberPg(pagination.PageNumberPagination):
    """查第n页，每页显示y条数据"""

    page_size_query_description = 'size'  # URL参数中，每页显示条数的参数
    page_query_param = 'page'  # URL中页面的参数
    page_size = EDIT_PAGE_SIZE  # 每页显示多少条数据
    max_page_size = 50  # 每页最多显示多少条数据
