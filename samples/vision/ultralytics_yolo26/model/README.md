# YOLO26 模型仓库

本目录包含了 YOLO26 系列模型的下载脚本及相关说明。这些模型已针对 D-Robotics RDK X5 (Bayes-e) 平台进行了量化编译（`.bin` 格式），支持硬件 BPU 加速。

## 模型获取方法

我们提供了两个便捷的下载脚本：

### 1. 快速下载 (Nano 版本)
如果您只想快速体验，可以运行以下脚本下载 Nano (n) 系列模型：
```bash
sh download_model.sh
```
该脚本会下载包括检测、分割、姿态估计、旋转框和分类在内的所有 `yolo26n` 模型。

### 2. 下载全部模型
如果您需要获取所有尺寸 (n, s, m, l, x) 的模型，请运行：
```bash
sh fulldownload.sh
```

## 支持的任务与模型列表

所有模型均采用 **NV12** 格式输入。

### 目标检测 (Detection)
- 输入分辨率: 640x640
- 模型文件: `yolo26{n/s/m/l/x}_detect_bayese_640x640_nv12.bin`

### 实例分割 (Instance Segmentation)
- 输入分辨率: 640x640
- 模型文件: `yolo26{n/s/m/l/x}_seg_bayese_640x640_nv12.bin`

### 姿态估计 (Pose Estimation)
- 输入分辨率: 640x640
- 模型文件: `yolo26{n/s/m/l/x}_pose_bayese_640x640_nv12.bin`

### 旋转框检测 (OBB)
- 输入分辨率: 640x640
- 模型文件: `yolo26{n/s/m/l/x}_obb_bayese_640x640_nv12.bin`

### 图像分类 (Classification)
- 输入分辨率: 224x224
- 模型文件: `yolo26{n/s/m/l/x}_cls_bayese_224x224_nv12.bin`

## 注意事项
- 默认下载地址已更新为最新的 `YOLO26_OE_1.2.8` 版本。
- 如果下载失败，请检查网络连接是否可以访问 `archive.d-robotics.cc`。
- 运行推理示例时，请确保 `--model-path` 参数指向本目录下的对应文件。
