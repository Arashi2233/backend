# -*-coding:utf-8 -*-
import datetime
import json
import os
from faker import Faker
from django.utils import timezone
from django.shortcuts import render
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from UserApp.models import OrderList, EquipList, GoodList,  UserList
from UserApp.serializers import OrderListModelSerializer,  GoodListModelSerializer
# Create your views here.

from django.core.files.storage import default_storage

# 分页器
from rest_framework.pagination import PageNumberPagination

# CBV类视图
from rest_framework.views import APIView

from django.conf import settings


class OrderListView(APIView):
    @csrf_exempt
    def get(self, request):
        # 序列化器的第一个参数：instance 用于序列化操作
        # 序列化器的第二个参数：data 用于反序列化操作
        # try:
        if not request.GET.get('order_name'):
            order_list = OrderList.objects.all().order_by('order_id')

        else:
            order_name = request.GET['order_name']
            order_list = OrderList.objects.filter(order_name=order_name).order_by('order_id')  # 此处只有一个对象
            print(order_name)  # str

        # 第二步:实力化产生一个分页类对象,不需要传参数
        page_pagination = PageNumberPagination()
        # 接收分页4个参数
        page_pagination.page_size = 10  # 默认每页显示多少条
        page_pagination.page_query_param = 'pagenum'  # URL中页码的参数
        page_pagination.page_size_query_param = 'pagesize'  # URL中每页显示条数的参数
        page_pagination.max_page_size = None  # 最大页码数限制

        # 第一个参数是要分页的queryset对象,第二个参数是request对象
        order_ret = page_pagination.paginate_queryset(order_list, request)

        # 第三步,再序列化的时候用ret对象,此时返回序列化之后的分页数据
        # 序列化器的第一个参数：instance 用于序列化操作
        # 序列化器的第二个参数：data 用于反序列化操作
        order_json = OrderListModelSerializer(instance=order_ret, many=True)
        dataset = {
            'status': 200,  # 创建成功的状态码
            'message': '订单获取成功',
            'data': order_json.data,
            'total': len(order_list)
        }
        return JsonResponse(dataset, safe=False)
        # except:
        #     return JsonResponse({'code': -999, 'message': '商品分类获取失败'}, safe=False)


# 参数 params:{order_id:id}
class DelOrderView(APIView):
    @csrf_exempt
    def get(self, request):
        try:
            order_obj = OrderList.objects.get(order_id=request.GET.get('order_id'))

            # 序列化器的第一个参数：instance 用于序列化操作
            # 序列化器的第二个参数：data 用于反序列化操作
            order_obj.delete()
            return JsonResponse({'code': 200, 'message': '订单删除成功'}, safe=False)
        except:
            return JsonResponse({'code': -999, 'message': '订单删除失败'}, safe=False)


# 参数 params: {order_id:id,new_status:1}
class EditOrderView(APIView):
    @csrf_exempt
    def get(self, request):
        order_obj = OrderList.objects.get(order_id=request.GET.get('order_id'))
        new_status = int(request.GET.get('new_status'))
        print(new_status)
        order_obj.status = new_status
        order_obj.save()
        return JsonResponse({'code': 200, 'message': '订单状态修改成功'}, safe=False)
        # except:
        #     return JsonResponse({'code': -999, 'message': '订单状态修改失败'}, safe=False)

def generate_random_name():
    return Faker().pystr(max_chars=20)
# 加入新订单
# params:{buyer_name: ,order_good_id: ,}
class AddOrderView(APIView):
    @csrf_exempt
    def get(self, request):
        # 根据名字找到用户id
        buyer_name = request.GET['buyer_name']
        print(buyer_name)
        buyer = UserList.objects.get(name=buyer_name)
        if not buyer:
            return JsonResponse({'code': -999, 'message': '用户不存在'}, safe=False)
        buyer_id = buyer.id
        print(buyer_id)
        order_good_id = request.GET['order_good_id']
        print(order_good_id)
        OrderList.objects.create(status=0, buyer_id=buyer_id, order_name=generate_random_name(), order_good_id=order_good_id)
        return JsonResponse({'code': 200, 'message': '添加订单成功'}, safe=False)




