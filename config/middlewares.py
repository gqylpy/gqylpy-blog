import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.conf import settings

ERROR_INFO = settings.ERROR_INFO
VIEW_ERROR_LOG_FILE = settings.VIEW_ERROR_LOG_FILE  # 记录视图异常的日志文件路径
HOLD_BACK_USER_AGENT = settings.HOLD_BACK_USER_AGENT  # 客户端标识不可包含的字符串列表


class RecordRequestTime(MiddlewareMixin):
    """记录请求耗时"""

    def process_request(self, request):
        self.start_time = time.time()

    def process_response(self, request, response):
        over_time = time.time() - self.start_time
        response['Response-Time'] = round(over_time, 2)
        return response


class RecordViewError(MiddlewareMixin):
    """记录视图异常信息，以便后续分析"""

    def process_exception(self, request, exception):
        """
        此方法只在是视图触发异常时执行
        :param request: 请求对象，与视图中用到的request参数是同一个对象
        :param exception: 视图函数触发异常时产生的Exception对象
        :return: None：按正常的流程走；HttpResponse对象：不再执行后续中间件的process_exception方法
        """
        f = open(VIEW_ERROR_LOG_FILE, 'a', encoding='utf-8')
        print(f"[{request.get_full_path()}] [{time.strftime('%Y-%m-%d %H:%M:%S')}] -- {exception}", file=f)
        f.flush()
        f.close()


class HoldBackThiefStrategy(MiddlewareMixin):
    """反爬策略"""

    CRAWLER_RESPONSE = '你好，%s'  # 面向爬虫响应

    def process_request(self, request):

        # 获取浏览器标识
        http_user_agent = str(request.META.get('HTTP_USER_AGENT')).lower()

        # 爬虫判断
        ret = [http_user_agent for user_agent in HOLD_BACK_USER_AGENT if user_agent in http_user_agent]
        return ret if not ret else HttpResponse(self.CRAWLER_RESPONSE % http_user_agent, status=403)
