from rest_framework import serializers
from UserApp.models import UserList, GoodList, OrderList, EquipList, Department


# 用户信息序列化器
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserList
        fields = '__all__'

# 商品信息序列化器
class GoodListModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodList
        fields = "__all__"
    
# 订单列表序列化器
class OrderListModelSerializer(serializers.ModelSerializer):
    # PrimaryKeyRelatedField 将关联对象序列化为关联对象的主键
    # 指定read_only=True参数时，该字段仅在序列化时使用;指定queryset参数时，将被用作反序列化时参数校验使用
    # https://blog.csdn.net/qq_38628046/article/details/129866800
    buyer_name = serializers.CharField(source='buyer.name')
    order_good_name = serializers.CharField(source='order_good.goods_name')

    class Meta:
        model = OrderList
        fields = "__all__"

# 设备列表序列化器
class EquipListModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EquipList
        fields = "__all__"

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

