from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse, HttpResponse
import json
from io import BytesIO

# 辅助函数
from utils.encrypt import md5
from utils.helper import check_code

# 解决url中文乱码
import urllib.parse
from rest_framework.response import Response
from base64 import b64encode

from UserApp.models import UserList

from uuid import uuid4
from django.core.cache import cache  # 默认内存，也可配置 Redis

def store_code(code_str):
    code_id = uuid4().hex
    cache.set(code_id, code_str, timeout=60)  # 有效期60秒
    print(code_str, code_id)
    return code_id

def get_code(code_id):
    return cache.get(code_id)

def delete_code(code_id):
    cache.delete(code_id)

@csrf_exempt
def login(request):
    """ 用户登录 """
    user_data = JSONParser().parse(request)
    code_input = user_data.get("code")
    code_id = user_data.get("code_id")

    real_code = get_code(code_id)
    if not real_code or real_code.upper() != code_input.upper():
        return JsonResponse({'code': -999, 'message': '验证码错误'}, safe=False)

    delete_code(code_id)

    # 验证码正确，去数据库校验用户名和密码
    user = user_data['name']
    pwd = user_data['password']
    role = user_data['role']
    encrypt_pasword = md5(pwd)
    print( user, pwd, encrypt_pasword)
    user_object = UserList.objects.filter(name=user, pwd=encrypt_pasword,role = role).first()
    if not user_object:
        return JsonResponse({'code': -999, 'message': '用户名或密码错误'}, safe=False)

    return JsonResponse({'code': 200, 'message': '登录成功', 'user_id': user_object.id, 'head_img': user_object.head_img}, safe=False)
    
@csrf_exempt
def img_code(request):
    # 1.生成图片
    image_object, code_str = check_code()
    code_id = store_code(code_str)

    # 2.图片内容返回写入内存，从内存读取并返回
    stream = BytesIO()
    image_object.save(stream, 'png')
    base64_image = b64encode(stream.getvalue()).decode()

    return JsonResponse({
        "code_id": code_id,
        "image": f"data:image/png;base64,{base64_image}"
    })

@csrf_exempt
def logout(request):
    request.session.clear()
    return JsonResponse({'code': 201, 'message': '退出成功'}, safe=False)