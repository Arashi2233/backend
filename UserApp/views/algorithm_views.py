import pandas as pd
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import matplotlib.pyplot as plt

plt.switch_backend('agg')  # 切换到Agg后端
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# 时序预测工具库 Prophet
from prophet import Prophet

# ARIMA 时序预测
import statsmodels.api as sm

# Pmdarima在底层使用statsmodels，是一个用于自动化 ARIMA 模型拟合的 Python 库
# 模型根据数据自动选择ARIMA模型的order参数（即自动确定p、d和q）-- 使用pmdarima库中的auto_arima函数。
# 这个函数可以根据AIC（赤池信息准则）或BIC（贝叶斯信息准则）来选择最优的order参数。
from pmdarima import auto_arima

import subprocess
from django.views.decorators.http import require_http_methods


def plot_comparison(data, forecast):
    plt.plot(data['ds'], data['y'], label='Actual')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast')
    plt.title('Forecast-Actual-Prophet')
    plt.savefig('plot_Prophet.png')

def DataGet(request):
    try:
        # 读取csv的最后100个数据
        data = pd.read_csv('data.csv').tail(100)
        data.columns = ['ds', 'y']
        print(data, type(data))
        data['ds'] = pd.to_datetime(data['ds'])

        # 原来的代码
        date=data['ds'].tolist()
        data.set_index('ds', inplace=True)
        sales = data['y'].tolist()
        # date即为日期戳
        print(date)
        print(data)
        print(sales)

        context = {
            'date': date,
            'yhat': sales
        }
        return JsonResponse({'code': 200, 'msg': '获取csv成功', 'context': context}, safe=False)
    except:
        return JsonResponse({'code': -999, 'msg': '获取csv失败'}, safe=False)
    

# params:{ model: ... , }
def TimePredict(request):
    try:
        # 从数据库中获取时间序列数据
        # data = pd.DataFrame(list(Sales.objects.all().values('date', 'value')))

        # 选择的预测模型 model
        model = request.GET['model']
        print(model)
        
        # data = request.GET['data']
        # date = request.GET['date']
        


        # 读取csv文件 规定csv文件只有列[date, val] -> [ds, y], 并对 ds 列日期格式转化
        data = pd.read_csv('data.csv')
        data.columns = ['ds', 'y']
        print(data, type(data))
        data['ds'] = pd.to_datetime(data['ds'])

        if model == 'Prophet':

            # 创建一个Prophet对象
            prophet = Prophet()
            # 为Prophet对象传入时间序列数据
            prophet.fit(data)

            # 创建一个日期范围以进行预测
            future = prophet.make_future_dataframe(periods=365)

            # 进行预测
            forecast = prophet.predict(future)

            # 使用plot_comparison函数绘制对比图
            plot_comparison(data, forecast)

            print(forecast, type(forecast))
            forecast.ds = pd.to_datetime(forecast.ds, format='%Y-%m-%d')
            print(forecast['ds'].head())
            context = {
                'date': forecast['ds'][-365:].tolist(),
                'yhat': forecast['yhat'][-365:].tolist()
            }
            return JsonResponse({'code': 200, 'msg': '获取csv成功', 'context': context}, safe=False)

        elif model == 'ARIMA':
            print('arima')
            p = request.GET['p']
            d = request.GET['d']
            q = request.GET['q']
            length = request.GET['length']
            # 将数据格式转化为ARIMA需要的格式

            # 原来的代码
            date=data['ds'].tolist()
            data.set_index('ds', inplace=True)
            sales = data['y'].tolist()
            # date即为日期戳
            print(date)
            print(data)
            print(sales)

            # 手动构建ARIMA模型 模型参数选取 (训练数据, order=(p,d,q))
            Amodel = sm.tsa.arima.ARIMA(data, order=(int(p), int(d), int(q)))

            # 使用auto_arima函数自动选择最优的order参数
            # seasonal: 是否考虑季节性；
            # suppress_warnings: 是否禁止显示警告信息
            # Amodel = auto_arima(sales, seasonal=True, suppress_warnings=True)
            # 打印选择的p、d、q参数
            print("Selected p,d,q parameters:", Amodel.order)
            # 根据选择的order参数构建ARIMA模型
            Amodel_fit = Amodel.fit()
            # Amodel_fit = Amodel.fit(y=sales)

            # 绘制ACF图
            plot_acf(Amodel_fit.resid)
            plt.xlabel('Lag')
            plt.ylabel('ACF')
            plt.title('Autocorrelation Function (ACF)')
            plt.savefig('plot2.png')

            # 绘制PACF图
            plot_pacf(data['y'])
            plt.xlabel('Lag')
            plt.ylabel('PACF')
            plt.title('Partial Autocorrelation Function (PACF)')
            plt.savefig('plot1.png')

            # 进行预测(未来30天)
            forecast = Amodel_fit.forecast(steps=int(length))
            # forecast = Amodel_fit.predict(n_periods=int(length))
            # 输出预测结果
            print(forecast,len(forecast))

            # 组织返回数据
            # 获取最后一项的索引作为起始日期
            start_date = data.index[-1]
            print(start_date)

            future_dates = pd.date_range(start=start_date, periods=int(length), freq='D')
            print(future_dates.tolist())
            context = {
                'date': future_dates.tolist(),
                'yhat': forecast.tolist()
            }

            # 将真实值和预测值绘制在一起
            # plt.figure(figsize=(10, 6))
            # plt.plot(data.index, data['y'], label='Actual')
            # plt.plot(future_dates, forecast, label='Forecast', color='red')
            # plt.xlabel('Date')
            # plt.ylabel('Sales')
            # plt.title('Actual vs Forecast')
            # plt.legend()
            # plt.savefig('plot_ARIMA.png')

            return JsonResponse({'code': 200, 'msg': '获取csv成功', 'context': context}, safe=False)
    except:
        return JsonResponse({'code': -999, 'msg': '获取csv失败'}, safe=False)



@csrf_exempt
@require_http_methods(["GET"])
def AgvSchedule(request):
    # 获取前端传入参数 AGV_num,equip_num(工位数/设备数)
    AGV_num = request.GET['AGV_num']
    equip_num = request.GET['equip_num']
    print(AGV_num)
    print(equip_num)
    # 创建参数列表，把整数转换为字符串
    args = ["python", "agv.py", "--AGV_num", str(AGV_num), "--equip_num", str(equip_num)]
    # 运行子进程并传递参数
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print(result.stdout)
    # 返回执行结果
    return JsonResponse({'stdout': result.stdout, 'stderr': result.stderr})

from djutils.yolomodel import run_inference
@csrf_exempt
def DefectDetection(request):
    """
    接收前端 POST 上传的一张图片（字段名 'image')
    保存到 MEDIA_ROOT/inference_input/ 下做推理，
    最后返回 JSON: { detections: [...], annotated_image_url: '...' }
    """
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持 POST 方法'}, status=405)

    image_file = request.FILES.get('image', None)
    if image_file is None:
        return JsonResponse({'error': '请上传图片，字段名为 image'}, status=400)

    # ---------- 1. 将上传文件临时保存到 MEDIA_ROOT/inference_input/ ----------
    input_dir = os.path.join(settings.MEDIA_ROOT, 'inference_input')
    os.makedirs(input_dir, exist_ok=True)

    # default_storage 在 Windows 上会默认像相对 MEDIA_ROOT 保存
    saved_path = default_storage.save(f"inference_input/{image_file.name}", ContentFile(image_file.read()))
    # saved_path 例如 "inference_input/img1.png"
    abs_input_path = os.path.join(settings.MEDIA_ROOT, saved_path)

    # ---------- 2. 调用 run_inference 做推理 ----------
    try:
        result = run_inference(abs_input_path)
    except Exception as e:
        # 推理出错时清理上传的临时文件，再返回错误
        default_storage.delete(saved_path)
        return JsonResponse({'error': f'推理出错：{str(e)}'}, status=500)

    # 3. 删除临时上传文件（如果你不需要保留原图）
    default_storage.delete(saved_path)

    # 4. 拼接带框图的 URL： MEDIA_URL + relative_path
    #    settings.MEDIA_URL = '/Photos/'
    #    annotated_image_rel_path 例如 'inference_results/result_img1.jpg'
    abs_out_path = result['annotated_image_path']  
    # abs_out_path 形如 "F:/.../Photos/inference_results/result_xxx.jpg"

    # 先把它变成相对于 MEDIA_ROOT 的路径
    rel_path = os.path.relpath(abs_out_path, settings.MEDIA_ROOT).replace('\\', '/')
    # rel_path 现在是 "inference_results/result_xxx.jpg"

    annotated_url = request.build_absolute_uri(settings.MEDIA_URL + rel_path)

    # ---------- 5. 返回 JSON ----------
    return JsonResponse({
        'status': 'success',
        'detections': result['detections'],
        'annotated_image_url': annotated_url
    })