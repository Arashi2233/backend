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

from UserApp.models import UserList
# Create your views here.


@csrf_exempt
def login(request):
    """ 用户登录 """
    user_data = JSONParser().parse(request)
    # 判断验证码是否正确
    image_code = request.session.get("image_code")
    if image_code.upper() != user_data['code'].upper():
        return JsonResponse({'code': -999, 'message': '验证码错误'}, safe=False)

    # 验证码正确，去数据库校验用户名和密码
    user = user_data['name']
    pwd = user_data['pwd']
    encrypt_pasword = md5(pwd)
    print(user, encrypt_pasword)
    user_object = UserList.objects.filter(name=user, pwd=encrypt_pasword).first()
    if not user_object:
        return JsonResponse({'code': -999, 'message': '用户名或密码错误'}, safe=False)

    request.session['info'] = {"id": user_object.id, 'name': user_object.name}
    request.session.set_expiry(60 * 60 * 24 * 7)

    return JsonResponse({'code': 200, 'message': '登录成功'}, safe=False)
    
@csrf_exempt
def img_code(request):
    # 1.生成图片
    image_object, code_str = check_code()

    # 2.图片内容返回写入内存，从内存读取并返回
    stream = BytesIO()
    image_object.save(stream, 'png')

    # 3.图片的内容写入session中 + 60s
    request.session['image_code'] = code_str
    request.session.set_expiry(60)

    return HttpResponse(stream.getvalue(), content_type='image/png')

@csrf_exempt
def logout(request):
    request.session.clear()
    return JsonResponse({'code': 201, 'message': '退出成功'}, safe=False)