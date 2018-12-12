# coding:utf-8

from django.http import HttpResponseRedirect


def islogin(func):
    """
    如果登录，则转到登录页面
    :param func:
    :return:
    """
    def login_fun(request,*args,**kw):
        if request.session.get('user_id'):
            return func(request,*args,**kwargs)
        else:
            red = HttpResponseRedirect('/user/login')
            red.set_cookie('url',request.get_full_path)
            return red
    return login_fun