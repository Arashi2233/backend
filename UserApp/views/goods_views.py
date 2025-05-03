# -*-coding:utf-8 -*-
import json
import os

from django.shortcuts import render
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from UserApp.models import  GoodList
from UserApp.serializers import GoodListModelSerializer
# Create your views here.

# 分页器
from rest_framework.pagination import PageNumberPagination

# CBV类视图
from rest_framework.views import APIView

from django.conf import settings
from faker import Faker



class GoodListView(APIView):
    @csrf_exempt
    def get(self, request):
        # 序列化器的第一个参数：instance 用于序列化操作
        # 序列化器的第二个参数：data 用于反序列化操作
        # try:
        if not request.GET.get('goods_name'):
            goods_list = GoodList.objects.all().order_by('goods_id')
            print(goods_list)
            if request.GET.get('goods_id'):  # 若有id传入
                goods_id = request.GET.get('goods_id')
                goods_list = GoodList.objects.filter(goods_id=goods_id).order_by('goods_id')
        else:
            goods_name = request.GET['goods_name']
            goods_list = GoodList.objects.filter(goods_name=goods_name).order_by('goods_id')  # 此处只有一个对象
            print(goods_name)  # str

        # 第二步:实力化产生一个分页类对象,不需要传参数
        page_pagination = PageNumberPagination()
        # 接收分页4个参数
        page_pagination.page_size = 10  # 默认每页显示多少条
        page_pagination.page_query_param = 'pagenum'  # URL中页码的参数
        page_pagination.page_size_query_param = 'pagesize'  # URL中每页显示条数的参数
        page_pagination.max_page_size = None  # 最大页码数限制

        if request.GET.get('pagenum', None) is not None:
            # 第一个参数是要分页的queryset对象,第二个参数是request对象
            goods_ret = page_pagination.paginate_queryset(goods_list, request)
        else:  # 若无分页需求
            goods_ret = goods_list
        # 第三步,再序列化的时候用ret对象,此时返回序列化之后的分页数据
        # 序列化器的第一个参数：instance 用于序列化操作
        # 序列化器的第二个参数：data 用于反序列化操作
        goods_json = GoodListModelSerializer(instance=goods_ret, many=True)
        dataset = {
            'status': 200,  # 创建成功的状态码
            'message': '商品列表获取成功',
            'data': goods_json.data,
            'total': len(goods_list)
        }
        return JsonResponse(dataset, safe=False)
        # except:
        #     return JsonResponse({'code': -999, 'message': '商品列表获取失败'}, safe=False)


# 添加商品（分类只能选择已有的，属性添加新的）
# 前端数据 addForm: {
#         goods_name: '',
#         goods_price: null,
#         goods_weight: null,
#         goods_number: null,
#         // // 富文本添加的说明(商品内容)
#         goods_introduce:'',
#       },
class AddGoodView(APIView):
    @csrf_exempt
    def post(self, request):
        goods_data = JSONParser().parse(request)
        
        good_serializer = GoodListModelSerializer(data=goods_data)
        if good_serializer.is_valid():
            good_serializer.save()            
            dataset = {
                'code': 200,
                'message': '添加成功'
            }
            return JsonResponse(dataset, safe=False)
        return JsonResponse({'code': -999, 'message': '添加失败'}, safe=False)
       


# 传入 params:{id:...} 删除对应数据项
# 一次删除一条，商品删除了，对应的商品属性会级联删除
class DelGoodView(APIView):
    @csrf_exempt
    def get(self, request):  # 在url处传入参数
        goods_id = request.GET.get('id')
        print(goods_id)

        try:
            good = GoodList.objects.get(goods_id=goods_id)  # get只能拿到第一条符合条件的数据,GoodList object (1)
            print(good)
            good.delete()

            dataset = {
                'code': 200,
                'message': '删除成功'
            }
            return JsonResponse(dataset, safe=False)
        except:
            return JsonResponse({'code': -999, 'message': '删除失败，参数不正确'}, safe=False)


# 修改商品信息
class EditGoodView(APIView):
    @csrf_exempt
    def put(self, request):  # 修改数据
        good_data = JSONParser().parse(request)
        # 获取对应用户obj
        good = GoodList.objects.get(id=good_data['id'])
        # instance 修改前数据
        good_serializer = GoodListModelSerializer(instance=good, data=good_data)
        if good_serializer.is_valid():
            good_serializer.save()
            dataset = {
                'code': 200,
                'message': '修改成功'
            }
            return JsonResponse(dataset, safe=False)
        return JsonResponse({
            'code': -999,
            'message': '修改失败'
        }, safe=False)



# 商品下单后加入订单列表，状态：1->0
# params:{goods_id:  ,status:  }
class EditGoodStatus(APIView):
    def get(self, request):
        new_status = int(request.GET['status'])
        print(new_status)
        goods_id = int(request.GET['goods_id'])
        print(goods_id)
        good = GoodList.objects.get(goods_id=goods_id)
        # 赋予新值
        good.status = new_status
        # 保存
        good.save()
        dataset = {
            'code': 200,
            'message': '修改成功'
        }
        return JsonResponse(dataset, safe=False)
