# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from models import GoodsInfo,TypeInfo
from django.core.paginator import Paginator

# Create your views here.
# 查询每类商品最新的4个和点击率最高的4个
def index(request):
    count = request.session.get('count')
    fruit = GoodsInfo.objects.filter(gtype__id=2).order_by("-id")[:4]
    fruit2 = GoodsInfo.objects.filter(gtype__id=2).order_by("-gclick")[:4]
    fish = GoodsInfo.objects.filter(gtype__id=4).order_by("-id")[:4]
    fish2 = GoodsInfo.objects.filter(gtype__id=4).order_by("-gclick")[:4]
    meat = GoodsInfo.objects.filter(gtype__id=1).order_by("-id")[:4]
    meat2 = GoodsInfo.objects.filter(gtype__id=1).order_by("-gclick")[:4]
    egg = GoodsInfo.objects.filter(gtype__id=5).order_by("-id")[:4]
    egg2 = GoodsInfo.objects.filter(gtype__id=5).order_by("-gclick")[:4]
    vegetables = GoodsInfo.objects.filter(gtype__id=3).order_by("-id")[:4]
    vegetables2 = GoodsInfo.objects.filter(gtype__id=3).order_by("-gclick")[:4]
    frozen = GoodsInfo.objects.filter(gtype__id=6).order_by("-id")[:4]
    frozen2 = GoodsInfo.objects.filter(gtype__id=6).order_by("-gclick")[:4]

    # 构造上下文
    context = {
        'title':'首页','fruit':fruit,
        'fish':fish,'meat':meat,'egg':egg,
        'vegetables':vegetables,'frozen':frozen,
        'fruit2':fruit2,'fish2':fish2,'meat2':meat2,
        'egg2':egg2,'vegetables2':vegetables2,'frozen2':frozen,
        'guest_cart':1,'page_name':0,'count':count
    }

    return render(request,'df_goods/index.html',context)

# 商品列表
def goodlist(request,typeid,pageid,sort):
    count = request.session.get('count')
    # 获取最新发布的商品
    newgood = GoodsInfo.objects.all().order_by("-id")[:2]
    # 根据条件查询所有商品
    if sort == '1': # 按添加时间
        sumGoodList = GoodsInfo.objects.filter(gtype__id=typeid).order_by('-id')
    elif sort == '2': # 按价格
        sumGoodList = GoodsInfo.objects.filter(gtype__id=typeid).order_by('gprice')
    elif sort == '3': # 按点击量
        sumGoodList = GoodsInfo.objects.filter(gtype__id=typeid).order_by('-gclick')

    # 分页
    paginator = Paginator(sumGoodList,15)
    goodList = paginator.pagee(int(pageid))
    pindexlist = paginator.page_range

    # 确定商品类型
    goodtype = TypeInfo.objects.get(id=typeid)

    # 构造上下文
    context = {
        'title':'商品详情','list':1,
        'guest_cart':1,'goodtype':goodtype,
        'newgood':newgood,'goodList':goodList,
        'typeid':typeid,'sort':sort,
        'pindexlist':pindexlist,'pageid':int(pageid),'count':count
    }
    # 渲染返回结果
    return render(request,'df_goods/list.html',context)


# 商品详情页
def detail(request,id):
    goods = GoodsInfo.objects.get(pk=int(id))
    goods.gclick = goods.gclick + 1
    goods.save()

    # 查询当前商品的类型
    goodtype = goods.gtype

    count = request.session.get('count')
    news = goods.gtype.goodsinfo_set.order_by('-id')[:2]

    context = {
        'title':goods.gtype.ttitle,'guest_cart':1,
        'g':goods,'newgood':news,'id':id,
        'isDelete':True,'list':1,'goodtype':goodtype,'count':count
    }

    response = render(request,'df_goods/detail.html',context)

    # 使用cookies记录最近浏览的商品id
    # 获取cookies
    goods_ids = request.COOKIES.get('goods_ids','')
    # 获取当前商品id
    goods_id = '%d' % goods.id
    # 判断cookies中商品id是否为空
    if goods_ids != '':
        # 分割出每个商品id
        goods_id_list = goods_ids.split(',')
        # 判断商品是否存在于列表
        if goods_id_list.count(goods_id) >= 1:
            # 存在则移除
            goods_id_list.remove(goods_id)
        goods_id_list.insert(0,goods_id)
        # 判断列表数是否超过5个
        if len(goods_id_list) >= 6:
            # 超过5个则删除第6个
            del goods_id_list[5]
        # 添加商品id到cookies
        goods_ids = ','.join(goods_id_list)
    else:
        goods_ids = goods_id
    response.set_cookie('goods_ids',goods_ids)

    return response



