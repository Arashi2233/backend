from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse, HttpResponse
import json
from django import forms
from django.core.validators import RegexValidator
from io import BytesIO

# 辅助函数
from utils.encrypt import md5

# 解决url中文乱码
import urllib.parse
from rest_framework.response import Response

from UserApp.models import UserList
from UserApp.serializers import UserListSerializer
# Create your views here.

from django.core.files.storage import default_storage

# 分页器
from rest_framework.pagination import PageNumberPagination

# CBV类视图
from rest_framework.views import APIView


# all、filter和get得到的数据返回类型是不一样的
# 仅仅能实现名字的搜索
class getUserView(APIView):
    # 通过params接受前端传来的参数，eg：id = request.GET['id']
    # 前端 params 定义：
    # 分页器数据 pageData: {
    #     page: 1, //当前页码
    #     limit: 3 // 每页显示3条
    # },
    # 查询的人的信息（只定义了名字） userForm: {
    #     name: ''
    # }
    @csrf_exempt
    def get(self, request):
        if 'name' in request.GET:
            users_list = UserList.objects.filter(name=request.GET['name']).order_by('id')
        elif 'role' in request.GET:
            users_list = UserList.objects.filter(role=request.GET['role']).order_by('id')
        else:
            users_list = UserList.objects.all().order_by('id')
        # 第二步:实力化产生一个分页类对象,不需要传参数
        page_pagination = PageNumberPagination()
        # 接收分页4个参数
        page_pagination.page_size = 5  # 默认每页显示多少条
        page_pagination.page_query_param = 'page'  # URL中页码的参数
        page_pagination.page_size_query_param = 'limit'  # URL中每页显示条数的参数
        page_pagination.max_page_size = None  # 最大页码数限制

        # 第一个参数是要分页的queryset对象,第二个参数是request对象
        users_ret = page_pagination.paginate_queryset(users_list, request)

        # 第三步,再序列化的时候用ret对象,此时返回序列化之后的分页数据
        # 序列化器的第一个参数：instance 用于序列化操作
        # 序列化器的第二个参数：data 用于反序列化操作
        users_serializer = UserListSerializer(instance=users_ret, many=True)

        # 返回字典
        dataset = {
            'code': 200,  # 创建成功的状态码
            'count': len(users_list),
            'list': users_serializer.data
        }
        return JsonResponse(dataset, safe=False)


class addUserView(APIView):
    @csrf_exempt
    def post(self, request):  # 新增一条 (若需要一次新增多条数据 一条数据的新增也必须以列表套字典形式提交 修改 many=True )
        users_data = JSONParser().parse(request)
        print(users_data)
        # 密码加密处理
        users_data['pwd'] = md5(users_data['pwd'])
        users_serializer = UserListSerializer(data=users_data)
        if users_serializer.is_valid():
            users_serializer.save()
            dataset = {
                'code': 201,
                'message': '添加成功'
            }
            return JsonResponse(dataset, safe=False)
        return JsonResponse({'code': -999, 'message': '添加失败'}, safe=False)

# 修改用户信息（不包括密码）
class editUserView(APIView):
    @csrf_exempt
    def put(self, request):  # 修改数据
        users_data = JSONParser().parse(request)
        # 获取对应用户obj
        user = UserList.objects.get(id=users_data['id'])
        # instance 修改前数据
        users_serializer = UserListSerializer(instance=user, data=users_data)# partial=True只传要改的字段即可，未传的字段保持原值。
        if users_serializer.is_valid():
            users_serializer.save()
            dataset = {
                'code': 200,
                'message': '修改成功'
            }
            return JsonResponse(dataset, safe=False)
        return JsonResponse({
            'code': -999,
            'message': '修改失败'
        }, safe=False)


class delUserView(APIView):
    @csrf_exempt
    def post(self, request):  # 在url处传入参数
        raw_data = request.body.decode("utf-8")
        json_data = json.loads(raw_data)
        user_id = json_data.get('id')
        print(user_id)
        try:
            user = UserList.objects.get(id=user_id)  # get只能拿到第一条符合条件的数据
            user.delete()
            dataset = {
                'code': 204,
                'message': '删除成功'
            }
            return JsonResponse(dataset, safe=False)
        except:
            return JsonResponse({'code': -999, 'message': '删除失败，参数不正确'}, safe=False)





