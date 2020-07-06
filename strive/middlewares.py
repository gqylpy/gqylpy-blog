from django.utils.deprecation import MiddlewareMixin
from config.settings import DISABLE_CSRF_CHECK  # 禁用CSRF校验的URL列表


# 取消个别请求进行csrf_token校验
class DisableCSRFCheck(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info in DISABLE_CSRF_CHECK:
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None  # 正常的流程走

# 已使用装饰器取消校验
