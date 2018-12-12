# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,redirect,HttpResponseRedirect
from django.http import HttpResponse
from models import *
from hashlib import sha1
from django.http import JsonResponse
from .islogin import islogin
from df_goods.models import GoodsInfo
from df_order.models import OrderInfo
from django.core.paginator import Paginator
from df_cart.models import *


def register(request):
    """
    注册页面
    :param request:
    :return:
    """
    return render(request,'df_user/register.html')

def register_handle(request):
    """
    登录处理
    :param request:
    :return:
    """
    response = HttpResponse()
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    ucpwd = post.get('cpwd')
    uemail = post.get('email')

    if upwd != ucpwd:
        return redirect('/user/register/')
    s1 = sha1()
    s1.update(upwd)
    upwd3 = s1.hexdigest()


    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()

    return redirect('/user/login')

def register_exist(request):
    """
    判断用户是否已存在
    :param request:
    :return:
    """
    uname = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count':count})

def login(request):
    """
    登录页面
    :param request:
    :return:
    """
    uname = request.COOKIES.get('uname','')
    context = {'title':'用户登录','error_name':0,'error_pwd':0,'uname':uname}
    return render(request,'df_user/login.html',context)

def login_handle(request):
    """
    登录处理
    :param request:
    :return:
    """
    get = request.POST
    uname = get.get('username')
    upwd = get.get('pwd')
    jizhu = get.get('jizhu',0)
    users = UserInfo.objects.filter(uname=uname) # 根据用户名查询对象
    if len(users) == 1: # 判断如果未查到则用户名错，查到再判断密码是否正确，正确则转到用户中心
        s1 = sha1()
        s1.update(upwd)
        if s1.hexdigest() == users[0].upwd:
            red = HttpResponseRedirect('/user/info')
            count = CartInfo.objects.filter(user_id=users[0].id).count()

            if jizhu != 0: # 记住用户名
                red.set_cookie('uname',uname)
            else:
                red.set_cookie('uname','',max_age=-1)
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            request.session['count'] = count

            return red
        else:
            context = {'title':'用户登录','error_name':0,'error_pwd':1,'uname':uname}
            return render(request,'df_user/login.html',context)
    else:
        context = {'title':'用户登录','error_name':1,'error_pwd':0,'uname':uname}
        return render(request,'df_user/login.html',context)

@islogin
def info(request):
    """
    登录用户中心
    :param request:
    :return:
    """
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail
    goods_ids = request.COOKIES.get('goods_ids','')
    goods_id_list = goods_ids.split(',')
    goods_list = []
    if len(goods_ids):
        for goods_id in goods_id_list:
            goods_list.append(GoodsInf.objects.get(id=int(goods_id)))
    context = {
        'title':'用户中心',
        'user_email':user_email,
        'user_name':request.session['user_name'],
        'page_name':1,
        'info':1,
        'goods_list':goods_list
    }
    return render(request,'df_user/user_center_info.html',context)

@islogin
def order(request):
    """
    订单
    :param request:
    :return:
    """
    context = {
        'title':'用户中心',
        'page_name':1,
        'order':1,
    }
    return render(request,'df_user/user_center_order.html',context)

@islogin
def site(request):
    """
    收货地址
    :param request:
    :return:
    """
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method = 'POST':
        post = request.POST
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uphone = post.get('uphone')
        user.uyoubian = post.get('uyoubian')
        user.save()
    context = {
        'title':'用户中心',
        'user':user,
        'page_name':1,
        'site':1,
    }
    return render(request,'df_user/user_center_site.html',context)

@islogin
def logout(request):
    """
    退出当前账号
    :param request:
    :return:
    """
    request.session.flush()
    return redirect('/')

@islogin
def user_center_order(request,pageid):
    """
    展示用户提交的订单
    :param request:
    :param pageid:
    :return:
    """
    uid = request.session.get('user_id')
    orderinfos = OrderInfo.objects.filter(user_id=uid).order_by('zhifu','-oid')
    paginator = Paginator(orderinfos,2) # 分页
    orderlist = paginator.page(int(pageid))
    plist = paginator.page_range
    qian1 = 0
    hou = 0
    hou2 = 0
    qian2 = 0
    dd = int(pageid)
    lenn = len(plist)
    if dd > 1:
        qian1 = dd - 1
    if dd >= 3:
        qian2 = dd - 2
    if dd < lenn:
        hou = dd + 1
    if dd + 2 <= lenn:
        hou2 = dd + 2

    context = {
        'page_name':1,
        'title':'全部订单',
        'pageid':int(pageid),
        'order':1,
        'orderlist':orderlist,
        'plist':plist,
        'pre':qian1,
        'next':hou,
        'pree':qian2,
        'lenn':lenn,
        'nextt':hou2
    }
    return render(request,'df_user/user_center_order.html',context)
