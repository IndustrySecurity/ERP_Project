from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import activate
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not request.path.startswith(reverse('login')):
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)


import threading

_thread_locals = threading.local()

def get_current_request():
    """
    获取当前请求对象
    """
    return getattr(_thread_locals, "request", None)

class CurrentUserMiddleware:
    """
    中间件，用于将当前请求绑定到线程。
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response

class LocalTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        activate(settings.TIME_ZONE)  # 激活本地时区
        return self.get_response(request)