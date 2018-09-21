from django.shortcuts import render, HttpResponseRedirect
from django.template import RequestContext
from django.utils.deprecation import (
    RemovedInDjango20Warning, RemovedInDjango110Warning
    # 关于版本问题的报错
)
# Create your views here.

import warnings  # 用作war报错而不影响正常运行，配合fuunctools使用
import functools  # 使用其中的wraps作为修饰器使用，报错不中断程序

from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
)
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.conf import settings as djset


# 创建修饰器，用于截获函数运行中的错误并war出，而不中断程序
def deprecate_current_app(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if 'current_app' in kwargs:
            warnings.warn(
                "Waring App : {0}".format(func.__name__),
                RemovedInDjango20Warning
            )
            print(kwargs)
            current_app = kwargs.pop('current_app')
            request = kwargs.get('request', None)
            if request and current_app is not None:
                request.current_app = current_app
        return func(*args, **kwargs)

    return inner


# 修饰器，如果未登录就跳转到settings里的login_url配置去
@login_required
def index(request):
    # TODO:登录后返回的页面
    return render(request, 'index.html')


@deprecate_current_app
# 过滤post请求中的所有变量，参数内可以写单独的变量名,如果在实例，也就是类使用这个装饰器
# 可以使用method_decorator(sensitive_post_parameters)
@sensitive_post_parameters()
# 使这个函数进行csrf验证
@csrf_protect
# 完全禁用缓存，服务端客户端都不会缓存
@never_cache
# 这里的操作包括

def login(request, redirect_field_name=REDIRECT_FIELD_NAME, authentication_form=AuthenticationForm):
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, '/'))
    # REDIRECT_FIELD_NAME默认为next，也就是下一跳的网址在urls内可以设置,这个参数显示为?next=*
    # get函数第二个参数为默认值，这里将其默认为GET的next的值，没有则为根目录，这里实际已经为根目录,因为当未登录时访问的为/,上面的login_required修饰器将其记录并作为next参数的值然后重定向到login页面
    # 这里的login函数参考django官方的认证函数
    if request.method == "POST":
        if 'login' in request.POST:  # 根据登录按钮判断是否为登录
            form = authentication_form(request, data=request.POST)  # 用POST的数据填充这个验证表单
            if form.is_valid():  # 这个会自动验证用户名密码，例如manage.py创建的超级用户
                if form.get_user() and form.get_user().is_active:  # 这里判定是否为激活的用户
                    if not is_safe_url(url=redirect_to, host=request.get_host()):
                        redirect_to = resolve_url(djset.LOGIN_REDIRECT_URL)  # 在设置文件内设置的跳转页面
                    auth_login(request, form.get_user())  # 验证通过用户
                    # TODO：记录用户登录日志
                    return HttpResponseRedirect(redirect_to)  # 这里跳转到了index函数的返回页面
            else:
                pass
                # TODO:用户验证失败记录日志
    else:
        form = authentication_form(request)  # 直接返回这个请求对象，这个表单内包含html标签，直接在html文件内循环变量就可以出现输入框

    return render(request, 'login.html', {'form': form})  # context_instance这个是必须的，这个返回函数默认为ConText会报错csrf验证失败


@deprecate_current_app
@login_required
def logout(request, next_page=None, redirect_field_name=REDIRECT_FIELD_NAME):
    # TODO:用户登出日志
    auth_logout(request)
    if next_page is not None:
        next_page = resolve_url(next_page)  # 将下一跳的地址格式化
    if (redirect_field_name in request.POST or redirect_field_name in request.GET):
        #next_page = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name))
        #这里实际上并没有next值传入，所以只能是手工输入的访问
        #if not is_safe_url(url=next_page, host=request.get_host()):
           # next_page = request.path
            #这里的安全url判定实际测试并不好使所以不使用，直接将手工的访问重置回去
        next_page=request.path
    if next_page:
        return HttpResponseRedirect(next_page)
    return HttpResponseRedirect(djset.LOGIN_REDIRECT_URL)
