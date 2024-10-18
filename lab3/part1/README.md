
# picture.py

## 简介

`picture.py` 是一个实现了 OCR & Agent 识别医疗发票图片数据的脚本，采用百度 OCR API 进行 OCR 识别，GPT-4o 进行解析。

## 使用方法

```bash
python picture.py --base_dir [base_dir]
```

## 参数

- `base_dir`: 图片所在的文件夹路径

## 示例

```bash
python picture.py --base_dir ..\医疗发票数据1\image
```

## 结果

结果为一个 JSON 文件，位于当前目录下，文件名为 `result_ocr&agent_{cur_time}.json`。
