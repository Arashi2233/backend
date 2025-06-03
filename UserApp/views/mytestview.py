from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse, HttpResponse
import json
from django import forms
from django.core.validators import RegexValidator
from io import BytesIO

# 辅助函数
from djutils.encrypt import md5
from faker import Faker
from django.utils import timezone
# 解决url中文乱码
import urllib.parse
from rest_framework.response import Response

from UserApp.models import UserList,Department, OrderList, GoodList, EquipList
from UserApp.serializers import UserListSerializer,DepartmentSerializer
# Create your views here.


def generate_random_name():
    return Faker().pystr(max_chars=20)

@csrf_exempt
def modify(request):
    # UserList.objects.create(name = 'hyx', gender = 1, age = 21, pwd=md5('20040521'), role=1)
    # UserList.objects.create(name = 'lzj', gender = 1, age = 21, pwd=md5('123456'), role=1)
    # UserList.objects.create(name = 'cff', gender = 1, age = 21, pwd=md5('123456'), role=0)

    # obj = OrderList.objects.filter(order_id=1).first()
    # print(timezone.localtime())
    # local_time = timezone.localtime(obj.create_time)
    # print(local_time)
    
    # GoodList.objects.create(goods_name = '产品A', goods_number = 50, goods_price = 100)
    # GoodList.objects.create(goods_name = '产品B', goods_number = 40, goods_price = 200)
    # GoodList.objects.create(goods_name = '产品C', goods_number = 30, goods_price = 300)
    # GoodList.objects.create(goods_name = '产品D', goods_number = 20, goods_price = 400)

    return JsonResponse({"status": True, 'error': 'ID不能为空'}, safe=False)
    # return HttpResponse("hello world")
    # return redirect('/login/')

