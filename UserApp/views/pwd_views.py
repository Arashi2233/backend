from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse


from UserApp.models import UserList
from UserApp.serializers import UserListSerializer
# Create your views here.

# 分页器

# CBV类视图
from rest_framework.views import APIView
# 辅助函数
from utils.encrypt import md5


# 修改密码需要验证原密码
# params:{user_id: ,old_pwd: ,new_pwd: }
class EditPwdView(APIView):
    @csrf_exempt
    def get(self, request):
        user_id = request.GET['user_id']
        old_pwd = request.GET['old_pwd']
        new_pwd = request.GET['new_pwd']
        print(user_id, type(user_id))
        print(old_pwd, type(old_pwd))
        print(new_pwd, type(new_pwd))
        # 加密
        new_make = md5(new_pwd)
        # 获取对应用户obj
        user = UserList.objects.get(id=user_id)
        # 密码验证成功
        if user.pwd == md5(old_pwd):
            user.pwd = new_make
            # 保存新密码
            user.save()
            return JsonResponse({'code': 200, 'message': '密码修改成功'}, safe=False)
        # 密码验证失败
        return JsonResponse({'code': -999, 'message': '密码验证失败'}, safe=False)


