# coding:utf-8

from django.conf.urls import url
from . import views


urlpatterns = [
    url('^register/$',views.register),
    url(r'^register_handle/$',views.register_handle),
    url(r'^register_exist/$',views.register_exist),
    url(r'^login_handle/$',views.login_handle),
    url(r'^login/$',views.login),
    url(r'^info/$',views.info),
    url(r'^site/$',views.site),
    url(r'^logout/$',views.logout),
    url(r'^user_center_order&(\d+)/$',views.user_center_order)，
]