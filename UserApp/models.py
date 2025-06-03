from django.db import models
import django
import random
import django.utils
import django.utils.timezone
from faker import Faker

# Create your models here.

# 在前端设置校验规则 email, phone 的规则
# addr 应该是可以选择的（此处未处理）
class UserList(models.Model):
    choices = (
        (1, '男'), (0, '女')
    )
    roles = (
        (1, 'admin'), (0, 'client')
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)  # 昵称（默认为收件人）
    addr = models.CharField(max_length=500, null=True)  # 收件地址
    age = models.IntegerField(null=True)
    gender = models.IntegerField(choices=choices, default=1)  # 性别，默认为男
    email = models.CharField(max_length=500, null=True)
    phone = models.CharField(max_length=500, null=True)
    pwd = models.CharField(max_length=500)
    head_img = models.CharField(max_length=500, null=True)  # 头像，图片需要上传到后端，和goods_pic一样
    role = models.IntegerField(choices=roles,default=0)  # 默认为客户
    @property
    def order_count(self):
        return self.user_order.count()

class GoodList(models.Model):
    # choices = (
    #     (1, 'cart'), (0, 'order')
    # )
    choices = (
        (1, '智能小车'), (2, '摄像头'), (3, '传感器'), (4, '标准件'), (5, '定制件'), (0, '其他')
    )   
    goods_id = models.AutoField(primary_key=True)
    goods_name = models.CharField(max_length=500)
    goods_number = models.IntegerField(default=3)  # 创建的该商品数量
    goods_price = models.IntegerField(default=100)
    goods_introduce = models.CharField(max_length=500, default='商品介绍')
    goods_pic = models.CharField(max_length=500, default='1.png')  # 只允许存放一张图片的名字
    goods_stockNum = models.IntegerField(default=50)  # 该类商品库存数量
    goods_category = models.IntegerField(default=0,choices=choices)  # 商品分类，默认为1
    # 判断是否已经下单，已经下单的商品不会放在购物车，而是订单列表，此字段只对客户有意义
    # status = models.IntegerField(choices=choices, default=1)



class OrderList(models.Model):
    choices = (
        (0, '待处理'), (1, '处理中'), (2, '已完成'), (3, '退回')
    )  # 用户层面 —— 0:待处理 ；1：未发货 ；2：已发货 ；3：订单被退回
    order_id = models.AutoField(primary_key=True)
    order_name = models.CharField(max_length=20,null=True )  # 默认生成随机订单名字
    #时间字段
    create_time = models.DateTimeField(default=django.utils.timezone.localtime)  # 订单创建时间
    status = models.IntegerField(choices=choices)
    # 一个订单限制允许一个用户创建
    buyer = models.ForeignKey(to=UserList, related_name='user_order', on_delete=models.CASCADE,
                              blank=True, null=True,
                              verbose_name='买家')  # models.CASCADE: 级联删除,删除关联对象时同时删除本对象。
    #user = order.buy
    #order = user.user_order.all()  # 反向查询
    # 一个订单限制允许订购一个商品
    order_good = models.ForeignKey(to=GoodList, related_name='good_order', on_delete=models.CASCADE,
                                   blank=True, null=True,
                                   verbose_name='订购商品')  # models.CASCADE: 级联删除,删除关联对象时同时删除本对象。
    number = models.IntegerField(default=1)  # 订购商品数量
    


# 工位对应（A、B、C、D）只设置四个加工设备
# 设置工位是否空闲

# 假设一次只允许一件商品在一个工位上加工
class EquipList(models.Model):
    choices = (
        (0, '空闲'), (1, '忙碌')
    )
    equip_id = models.AutoField(primary_key=True)
    equip_name = models.CharField(max_length=100)
    status = models.IntegerField(choices=choices, default=0)
    # -1代表无加工商品
    processing_goodId = models.IntegerField(default=-1)


# insert into  userapp_equiplist values(1,'工位A',0,-1);
# insert into  userapp_equiplist values(2,'工位B',0,-1); 另外： (3,'工位C',0,-1)  (4,'工位D',0,-1)



class Department(models.Model):
    title = models.CharField(verbose_name="标题", max_length=32)
    count = models.IntegerField(verbose_name="人数")

    def __str__(self):
        return self.title

