# inference/utils.py
import os
import torch
from pathlib import Path
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.plots import Annotator, colors
from yolov5.utils.general import non_max_suppression, scale_boxes
from yolov5.utils.augmentations import letterbox
import cv2
import numpy as np

# 模型和权重路径
BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_PATH = BASE_DIR / 'models' / 'best.pt'

# 全局变量
MODEL = None
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model():
    """
    只加载一次模型，并缓存到全局 MODEL 里。
    DetectMultiBackend 会自动根据设备选择最优后端(CPU/GPU)。
    """
    global MODEL
    if MODEL is None:
        MODEL = DetectMultiBackend(weights=str(WEIGHTS_PATH), device=DEVICE)
        MODEL.eval()
    return MODEL

def run_inference(image_path, img_size=640, conf_thres=0.25, iou_thres=0.45):
    """
    对单张图片做推理，返回：
      - detections: [
            {
              'bbox': [x1, y1, x2, y2],
              'confidence': float,
              'class_id': int,
              'class_name': str
            },
            ...
        ]
      - annotated_image_path: 标注后图片在 MEDIA 下的保存路径
    """
    model = load_model()

    # ----------------------------------------------------------------
    # 1. 读取并预处理图片
    img0 = cv2.imread(str(image_path))  # BGR
    if img0 is None:
        raise ValueError(f"无法读取图片：{image_path}")
    h0, w0 = img0.shape[:2]

    img = letterbox(img0, new_shape=img_size)[0]                 # 缩放，padding
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR->RGB, HWC->CHW
    img = np.ascontiguousarray(img)

    im_tensor = torch.from_numpy(img).to(DEVICE)
    im_tensor = im_tensor.float() / 255.0
    if im_tensor.ndimension() == 3:
        im_tensor = im_tensor.unsqueeze(0)

    # ----------------------------------------------------------------
    # 2. 推理
    pred = model(im_tensor)[0]
    pred = non_max_suppression(pred, conf_thres, iou_thres)

    # ----------------------------------------------------------------
    # 3. 解析结果并画框
    results = []
    save_img = img0.copy()
    annotator = Annotator(save_img, line_width=2, example=str(0))

    # **从模型中读取类别名称列表**：
    # DetectMultiBackend 会把原始 .yaml 里的 names 加载到 model.names
    names = model.names  # e.g. {0: '缺陷类型A', 1: '缺陷类型B'}

    for det in pred:  # 虽然这里只推理了一张图，但 pred 还是个列表
        if det is not None and len(det):
            # det[:, :4] 存的是归一化后bounding box，需要缩放回原图
            det[:, :4] = scale_boxes(im_tensor.shape[2:], det[:, :4], (h0, w0)).round()
            for *xyxy, conf, cls_id in det:
                xyxy = [int(x.item()) for x in xyxy]      # [x1, y1, x2, y2]
                conf = float(conf.item())
                cls_id = int(cls_id.item())
                cls_name = names[cls_id]                  # 取中文类名

                results.append({
                    'bbox': xyxy,
                    'confidence': round(conf, 3),
                    'class_id': cls_id,
                    'class_name': cls_name
                })

                # 画框并加 label
                label = f"{cls_name} {conf:.2f}"
                annotator.box_label(xyxy, label, color=colors(cls_id, True))

    annotated_img = annotator.result()

    # ----------------------------------------------------------------
    # 4. 将带框图保存到 Photos/inference_results/
    out_dir = BASE_DIR / 'Photos' / 'inference_results'
    os.makedirs(out_dir, exist_ok=True)
    out_path = out_dir / f"result_{Path(image_path).stem}.jpg"
    cv2.imwrite(str(out_path), annotated_img)

    return {
        'detections': results,
        'annotated_image_path': str(out_path)
    }
