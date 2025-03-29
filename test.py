import pytesseract
from PIL import Image

# 生成测试图片（白底黑字）
image = Image.new('RGB', (400, 100), color='white')
image.save('test.png')

# 测试中英文识别
print("中文测试:", pytesseract.image_to_string('test.png', lang='chi_sim'))
print("英文测试:", pytesseract.image_to_string('test.png', lang='eng'))