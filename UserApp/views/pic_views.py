import os
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from faker import Faker


@csrf_exempt
def UploadPic(request):
    file = request.FILES['file']
    file_name = Faker().pystr() + '.png'
    pic_name = default_storage.save(file_name, file)
    print(pic_name)
    return JsonResponse({'code': 200, 'message': '图片上传成功', 'data': pic_name}, safe=False)


#  Django 处理文件上传 https://docs.djangoproject.com/zh-hans/4.2/topics/http/file-uploads/
@csrf_exempt
def DeletePic(request):
    filename = request.GET['file_name']

    pwd = os.getcwd()
    print(pwd)

    file_path = os.path.join(pwd, 'Photos', filename)
    # print(file_path)
    # C:\Users\18807750721\Desktop\front-back\myproject\demo_code\DjangoAPI\Photos\2.png
    try:
        os.remove(file_path)
        return JsonResponse({'code': 200, 'message': '删除图片成功'})

    except:
        return JsonResponse({'code': -999, 'message': '删除图片失败'})

