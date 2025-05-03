from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from django import forms
from django.core.validators import RegexValidator
from io import BytesIO

# 辅助函数
from utils.encrypt import md5
from utils.helper import check_code


from UserApp.models import UserList, Department
# Create your views here.

from django.core.files.storage import default_storage


class LoginForm(forms.Form):
    name = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "请输入用户名"}),
        validators=[RegexValidator(r'^\w{2,}$', '用户名格式错误')] # 用户名长度大于等于2
    )
    pwd = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': "请输入密码"}, render_value=True),
    )
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "输入验证码"}),
    )

def login(request):
    """ 用户登录 """
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {"form": form})

    form = LoginForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'login.html', {"form": form})

    # 判断验证码是否正确
    image_code = request.session.get("image_code")
    if not image_code:
        form.add_error("code", "验证码已过期")
        return render(request, 'login.html', {"form": form})
    if image_code.upper() != form.cleaned_data['code'].upper():
        form.add_error("code", "验证码错误")
        return render(request, 'login.html', {"form": form})

    # 验证码正确，去数据库校验用户名和密码
    user = form.cleaned_data['name']
    pwd = form.cleaned_data['pwd']
    encrypt_pasword = md5(pwd)
    print(user, encrypt_pasword)
    user_object = UserList.objects.filter(name=user, pwd=encrypt_pasword).first()
    if not user_object:
        return render(request, 'login.html', {"form": form, 'error': "用户名或密码错误"})

    request.session['info'] = {"id": user_object.id, 'name': user_object.name}
    request.session.set_expiry(60 * 60 * 24 * 7)

    return redirect("/home/")
    
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


def logout(request):
    request.session.clear()
    return redirect('/login/')


def home(request):
    # request.info_dict['name']
    return render(request, 'home.html')

def user_list(request):
    """ 用户列表 """

    # [obj,]
    queryset = UserList.objects.all().order_by("-id")
    # for row in queryset:
    #     print(row.username, row.password, row.gender, row.get_gender_display(), row.depart_id, row.depart.title)

    return render(request, 'user_list.html', {"queryset": queryset})


class UserModelForm(forms.ModelForm):
    class Meta:
        model = UserList
        fields = ['name', 'pwd', 'age', 'gender']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 自定义操作，找到所有的字段
        # print(self.fields)
        for name, filed_object in self.fields.items():
            # print(name, filed_object)
            filed_object.widget.attrs = {"class": "form-control"}


def user_add(request):
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'user_form.html', {"form": form})

    form = UserModelForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'user_form.html', {"form": form})

    # 读取密码并更新成md5加密之后的密文
    form.instance.pwd = md5(form.instance.pwd)

    # 保存到数据库
    form.save()
    return redirect('/user/list/')


class UserEditModelForm(forms.ModelForm):
    class Meta:
        model = UserList
        fields = ['name', 'age', 'gender']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 自定义操作，找到所有的字段
        # print(self.fields)
        for name, filed_object in self.fields.items():
            # print(name, filed_object)
            filed_object.widget.attrs = {"class": "form-control"}


def user_edit(request, aid):
    admin_object = UserList.objects.filter(id=aid).first()

    if request.method == "GET":
        form = UserEditModelForm(instance=admin_object)
        return render(request, 'user_form.html', {"form": form})

    form = UserEditModelForm(instance=admin_object, data=request.POST)
    if not form.is_valid():
        return render(request, 'user_form.html', {"form": form})

    # 更新
    form.save()

    return redirect('/user/list/')


def user_delete(request):
    aid = request.GET.get("aid")
    # print("要删除的ID:", aid)
    UserList.objects.filter(id=aid).delete()

    # return JsonResponse({"status": False, 'error': "ID不能为空"})
    return JsonResponse({"status": True})


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
