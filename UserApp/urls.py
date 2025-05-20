from django.urls import path, re_path
from UserApp.views import log_views, department, mytestview, mystudyview, user_views, pic_views, goods_views, order_views, equip_views, algorithm_views, chart_views, pwd_views



from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('modify/', mytestview.modify),
                  # 用户操作
                  path('user/getUser/', user_views.getUserView.as_view()),
                  path('user/addUser/', user_views.addUserView.as_view()),
                  path('user/editUser/', user_views.editUserView.as_view()),
                  path('user/delUser/', user_views.delUserView.as_view()),

                  # 密码
                  path('pwd/editPwd/', pwd_views.EditPwdView.as_view()),

                  # 用户登录
                  path('login/', log_views.login),
                  path('logout/', log_views.logout),
                  path('img/code/', log_views.img_code),

                  # 图片
                  re_path(r'^pic/uploadPic/', pic_views.UploadPic),
                  re_path(r'^pic/deletePic/', pic_views.DeletePic),

                  # 商品
                  path('goods/goodList/', goods_views.GoodListView.as_view()),
                  path('goods/addGood/', goods_views.AddGoodView.as_view()),
                  path('goods/delGood/', goods_views.DelGoodView.as_view()),
                  path('goods/editGood/', goods_views.EditGoodView.as_view()),
                  path('goods/editGoodStatus/', goods_views.EditGoodStatus.as_view()),

                  # 订单
                  path('order/orderList/', order_views.OrderListView.as_view()),
                  path('order/delOrder/', order_views.DelOrderView.as_view()),
                  path('order/editOrder/', order_views.EditOrderView.as_view()),
                  path('order/addOrder/', order_views.AddOrderView.as_view()),

                  # 设备
                  path('equip/equipList/', equip_views.EquipListView.as_view()),
                  path('equip/updateProcessingId/', equip_views.UpdateProcessingId.as_view()),

                  # 算法
                  path('algorithm/timePredict/', algorithm_views.TimePredict),
                  path('algorithm/agvSchedule/', algorithm_views.AgvSchedule),
                  path('algorithm/dataGet/', algorithm_views.DataGet),

                  # 图表
                  path('chart/', chart_views.charts_data),


                  
                  # 部门
                  path('depart/list/', department.depart_list),
                  path('add/depart/', department.add_depart),
                  path('delete/depart/', department.delete_depart),
                  path('edit/depart/', department.edit_depart),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 正则表达式规则：https://www.runoob.com/regexp/regexp-syntax.html
