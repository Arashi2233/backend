from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse, HttpResponse
import json

from rest_framework.response import Response

from UserApp.models import UserList, GoodList, OrderList
from UserApp.serializers import UserListSerializer
# Create your views here.

from django.core.files.storage import default_storage
from django.utils import timezone
import datetime
from django.db.models import Sum,Case, When, Value, IntegerField, Count
from collections import defaultdict



def charts_data(request):
    try:
        # 获取上海时间的当日日期
        local_today = timezone.localtime().date()  # 当前上海日期，如 2023-10-10

        # 生成上海时间的当日开始和结束时间（需转换为 UTC 时间）
        local_start = timezone.make_aware(datetime.datetime.combine(local_today, datetime.time.min))  # 上海时间 00:00:00
        local_end = local_start + datetime.timedelta(days=1)  # 上海时间次日 00:00:00

        # 查询当天的订单
        today_orders_count = OrderList.objects.filter(
            create_time__gte=local_start,
            create_time__lt=local_end
        ).count()

        total_number = OrderList.objects.filter(
            create_time__gte=local_start,
            create_time__lt=local_end
        ).aggregate(total=Sum('number'))['total'] or 0
        raw_orders_count = OrderList.objects.filter(status=0).count()
        raw_orders_count = raw_orders_count or 0
        # 定义区间条件并统计各商品数量区间内订单数量
        num_result = (
            OrderList.objects
            .annotate(
                range_label=Case(
                    When(number=1, then=Value(1)),
                    When(number=2, then=Value(2)),
                    When(number=3, then=Value(3)),
                    When(number__gte=4, number__lte=8, then=Value(4)),
                    When(number__gt=8, then=Value(5)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .values('range_label')
            .annotate(count=Count('order_id'))
            .order_by('range_label')
        )

        # 转换为更易读的区间标签
        range_mapping = {
            1: ("1", "数量为1的订单"),
            2: ("2", "数量为2的订单"),
            3: ("3", "数量为3的订单"),
            4: ("4-8", "数量4到8的订单"),
            5: ("8+", "数量超过8的订单"),
        }

        # 重组结果并填充缺失区间（数量为0的区间）
        final_result = {
            label: next((item["count"] for item in num_result if item["range_label"] == key), 0)
            for key, (label, _) in range_mapping.items()
        }
        # 输出：{'1': 5, '2': 3, '3': 2, '4-8': 10, '8+': 7}

        # 获取所有可能的状态和名称
        status_choices = dict(OrderList.choices)
        all_status = status_choices.keys()

        # 按状态分组统计
        status_counts = (
            OrderList.objects
            .values('status')
            .annotate(count=Count('status'))
        )

        # 创建默认值为0的字典
        status_result = defaultdict(int)
        for item in status_counts:
            status_result[item['status']] = item['count']

        # 确保所有状态都包含在结果中（没有的设为0）
        for status in all_status:
            status_result[status] = status_result.get(status, 0)
        # 输出示例：{0: 5, 1: 3, 2: 10, 3: 2}
        data_set = {
            'code': 200,
            'message': '获取成功',
            'today_orders_count': today_orders_count,
            'total_number': total_number,
            'raw_orders_count': raw_orders_count,
            'num_result': final_result,
            'status_result': status_result
        }
        return JsonResponse(data_set, safe=False)
    except:
        return JsonResponse({'code': -999, 'message': '数据读取错误'}, safe=False)
