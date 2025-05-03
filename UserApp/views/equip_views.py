# -*-coding:utf-8 -*-
import datetime
import json
import os

from django.shortcuts import render
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from UserApp.models import  EquipList
from UserApp.serializers import OrderListModelSerializer,  GoodListModelSerializer, EquipListModelSerializer
    
# Create your views here.

from django.core.files.storage import default_storage


# CBV类视图
from rest_framework.views import APIView

from django.conf import settings


# 获取设备数据
class EquipListView(APIView):
    @csrf_exempt
    def get(self, request):
        # 序列化器的第一个参数：instance 用于序列化操作
        # 序列化器的第二个参数：data 用于反序列化操作
        try:
            equip_objs = EquipList.objects.all().order_by('equip_id')
            equip_json = EquipListModelSerializer(instance=equip_objs, many=True)
            dataset = {
                'status': 200,  # 创建成功的状态码
                'message': '设备信息获取成功',
                'data': equip_json.data,
            }
            return JsonResponse(dataset, safe=False)
        except:
            return JsonResponse({'code': -999, 'message': '设备信息获取失败'}, safe=False)


# 删除工位
class DelEquipView(APIView):
    pass


# 修改工位信息
class EditEquipView(APIView):
    pass


# 工位加工的商品的更新
# params:{equip_id:..., goods_id: ...}
class UpdateProcessingId(APIView):
    @csrf_exempt
    def get(self, request):
        equip_id = int(request.GET['equip_id'])
        print(equip_id)
        goods_id = int(request.GET['goods_id'])
        print(goods_id)

        equip_obj = EquipList.objects.get(equip_id=equip_id)
        if goods_id != -1:
            equip_obj.status = 1
        else:
            equip_obj.status = 0
        equip_obj.processing_goodId = goods_id
        equip_obj.save()
        return JsonResponse({'code': 200, 'message': '设备信息更新成功'}, safe=False)
