import os
import re
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from PIL import ImageEnhance

# ==================== 配置区 ====================
# 注意：以下路径需根据实际安装位置修改
POPPLER_PATH = r'C:\poppler-24.08.0\Library\bin'  # Poppler工具路径
TESSERACT_PATH = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'  # Tesseract可执行文件路径
TESSDATA_PATH = r'C:\Program Files\Tesseract-OCR\tessdata'  # 语言包路径

# 配置Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ['TESSDATA_PREFIX'] = TESSDATA_PATH


# ================== 核心函数 ====================
def ocr_pdf_to_csv(pdf_path, output_csv="vocabulary.csv"):
    """
    将PDF单词表转换为CSV文件
    参数:
        pdf_path: 输入PDF文件路径
        output_csv: 输出CSV文件名
    返回:
        DataFrame格式的数据
    """

    # 创建临时图片存储目录
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)

    # Step 1: PDF转高清图片（增强图像质量）
    try:
        images = convert_from_path(
            pdf_path,
            dpi=400,  # 提高DPI增强清晰度
            poppler_path=POPPLER_PATH,
            output_folder=temp_dir,
            fmt="png",  # 使用无损格式
            thread_count=4  # 多线程加速
        )
    except Exception as e:
        print(f"PDF转换失败: {str(e)}")
        return pd.DataFrame()

    # Step 2: 图像预处理函数
    def enhance_image(image):
        """图像增强处理"""
        # 转换为灰度图
        image = image.convert('L')
        # 增强对比度
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(2.5)

    all_data = []
    current_unit = None  # 当前单元号
    unit_pattern = re.compile(r'Unit\s+(\d+)', re.IGNORECASE)  # 单元检测正则

    # Step 3: 处理每一页图片
    for page_num, image in enumerate(images, 1):
        try:
            # 图像预处理
            enhanced_img = enhance_image(image)

            # OCR识别（中英混合模式）
            text = pytesseract.image_to_string(
                enhanced_img,
                lang='chi_sim+eng',
                config='--psm 6 --oem 3'  # 优化识别模式
            )

            # ===== 调试输出：打印OCR结果（处理前注释掉） =====
            # print(f"\n===== 第 {page_num} 页 OCR 结果 =====")
            # print(text)
            # print("="*60)

            # Step 4: 检测单元号（优先保留跨页信息）
            unit_match = unit_pattern.search(text)
            if unit_match:
                current_unit = int(unit_match.group(1))
                # print(f"检测到单元号: Unit {current_unit}")

            # Step 5: 数据提取正则（优化版）
            # 匹配模式：序号 单词 [音标] 释义
            pattern = re.compile(
                r'^(\d+)[\.\s]*'  # 序号（兼容数字后跟点或空格）
                r'([a-zA-Z\s\-]+?)\s+'  # 单词（允许连字符）
                r'(\[.*?\])?\s*'  # 音标（可选）
                r'([\u4e00-\u9fa5].*?)\s*$',  # 中文释义
                re.MULTILINE
            )

            # 逐行处理提高准确性
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # 执行匹配
                match = pattern.match(line)
                if match:
                    order = match.group(1)
                    word = match.group(2).strip()
                    pronunciation = match.group(3).strip('[] ') if match.group(3) else ''
                    definition = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。]', '', match.group(4).strip())

                    # 存入数据
                    all_data.append({
                        "unit": current_unit,
                        "order": order,
                        "word": word,
                        "pronunciation": pronunciation,
                        "definition": definition
                    })
                    # print(f"提取成功: {order} {word}")

        except Exception as e:
            print(f"第 {page_num} 页处理异常: {str(e)}")

    # Step 6: 清理临时文件
    try:
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)
    except Exception as e:
        print(f"临时文件清理失败: {str(e)}")

    # Step 7: 保存结果
    df = pd.DataFrame(all_data)
    if not df.empty:
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"成功保存至 {output_csv}")
    return df


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 测试文件路径
    test_pdf = "words7.pdf"

    # 执行转换
    result_df = ocr_pdf_to_csv(test_pdf)

    # 打印结果摘要
    if not result_df.empty:
        print("\n===== 提取结果摘要 =====")
        print(f"总条目数: {len(result_df)}")
        print("前5条数据:")
        print(result_df.head())
    else:
        print("未提取到有效数据，请检查输入文件或调试设置")