from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.http.response import JsonResponse, HttpResponse


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 1.不用登录就可以访问处理
        if request.path_info in ["/login/", "/img/code/", "/modify/"]:
            return

        # 2.获取session
        info_dict = request.session.get("info")

        # 未登录
        if not info_dict:
            # return JsonResponse({"status": False, "error": "用户未登录"}, status=401,safe=False)
            return redirect("/login/")

        # 已登录
        request.info_dict = info_dict
        return
