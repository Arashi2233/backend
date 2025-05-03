from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse, HttpResponse
import json
from django import forms



# 解决url中文乱码
from rest_framework.response import Response

from UserApp.models import  Department
from UserApp.serializers import DepartmentSerializer
# Create your views here.

from django.core.files.storage import default_storage

# 分页器
from rest_framework.pagination import PageNumberPagination

# CBV类视图
from rest_framework.views import APIView

def depart_list(request):
    """ 部门列表 """
    queryset = Department.objects.all()

    return render(request, 'depart_list.html', {"queryset": queryset})


class DepartModelForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = "__all__"


def add_depart(request):
    if request.method == "GET":
        form = DepartModelForm()
        return render(request, 'depart_form.html', {'form': form})

    form = DepartModelForm(data=request.POST)
    if form.is_valid():
        # form.cleaned_data {....}
        form.save()  # 保存数据
        return redirect('/depart/list/')
    else:
        return render(request, 'depart_form.html', {'form': form})


def delete_depart(request):
    did = request.GET.get("did")
    Department.objects.filter(id=did).delete()
    return redirect('/depart/list/')


def edit_depart(request):
    # 根据ID获取要编辑的部门对象
    did = request.GET.get("did")
    depart_object = Department.objects.filter(id=did).first()

    if request.method == "GET":
        # 显示标签+默认数据展示
        form = DepartModelForm(instance=depart_object)
        return render(request, 'depart_form.html', {'form': form})

    form = DepartModelForm(data=request.POST, instance=depart_object)
    if form.is_valid():
        form.save()  # 更新
        return redirect('/depart/list/')
    else:
        return render(request, 'depart_form.html', {'form': form})