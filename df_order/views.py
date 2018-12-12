# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.db import transaction
from datetime import datetime
from decimal import Decimal
from models import OrderInfo,OrderDetailInfo
from df_user.islogin import islogin
from df_cart.models import CartInfo
from df_goods.models import GoodsInfo
from df_user.models import UserInfo
from django.http import JsonResponse


# Create your views here.
@islogin
def order(request):
    """
    订单页面展示数据
    :param request:
    :return:
    """
    uid = request.session.get('user_id')
    user = UserInfo.objects.get(id=uid)

    orderid = request.GET.getlist('orderid')
    orderlist = []

    for id in orderid:
        orderlist.append(CartInfo.objects.get(id=int(id)))

    # 判断用户手机号是否为空，分别展示
    if user.uphone == '':
        uphone = ''
    else:
        uphone = user.uphone[0:4] + '****' + user.uphone[-4:]

    # 构造上下文
    context = {
        'title':'提交订单','page_name':2,'orderlist':orderlist,
        'user':user,'ureceive_phone':uphone
    }

    return render(request,'df_order/place_order.html',context)

@transaction.atomic() # 事物装饰器
@islogin
def order_handle(request):
    tran_id = transaction.savepoint() # 保留一个事物点
    try:
        post = request.POST
        orderlist = post.getlist('id[]')
        total = post.get('total')
        address = post.get('address')
        order = OrderInfo
        now = datetime.now()
        uid = request.session.get('user_id')
        order.oid = '%s%d' % (now.strftime('%Y%m%d%H%M%S'),uid)
        order.user_id = uid
        order.odate = now
        order.ototal = Decimal(total)
        order.oaddress = address
        order.save()

        for orderid in orderlist: # 遍历购物车中提交信息，创建订单详情表
            cartinfo = CartInfo.objects.get(id=orderid)
            good = GoodsInfo.objects.get(pk=cartinfo.goods_id)
            if int(good.gkucun) >= int(cartinfo.count):
                good.gkuncun -= int(cartinfo.count)
                good.save()
                goodinfo = GoodsInfo.objects.get(cartinfo_id=orderid)

                # 创建订单详情表
                detailinfo = OrderDetailInfo()
                detailinfo.goods_id = int(goodinfo.id)
                detailinfo.order_id = int(order.oid)
                detailinfo.price = Decimal(int(goodinfo.gprice))
                detailinfo.save()

                # 循环删除购物车对象
                cartinfo.delete()
            else:
                transaction.savepoint_rollback(tran_id) # 库存不够事物回滚
                return JsonResponse({'status':2}) # 返回json供前台提示失败

    except Exception as e:
        transaction.savepoint_rollback(tran_id)

    return JsonResponse({'status':1})

def pay(request,oid):
    """
    支付处理
    :param request:
    :param oid:
    :return:
    """
    tran_id = transaction.savepoint()
    order = OrderInfo.objects.get(oid=oid)
    order.zhifu = 1

    order.save()
    context = {'oid':oid}
    return render(request,'df_order/pay.html',context)