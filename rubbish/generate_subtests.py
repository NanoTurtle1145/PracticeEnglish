import csv
import json
import os
import random
from collections import defaultdict

def generate_subtests():
    # 读取词汇数据
    word_data = defaultdict(list)
    with open('rubbish/words.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过标题行
        for row in reader:
            if len(row) >=5 and row[4].startswith('Unit'):
                unit = row[4].strip()
                word_data[unit].append({
                    'word': row[1].strip(),
                    'definition': row[3].strip()
                })

    # 创建测试目录
    os.makedirs("tests", exist_ok=True)

    # 为每个单元生成题库
    for unit, words in word_data.items():
        main_questions = []
        
        # 生成选择题和填空题
        for word in words:
            # 选择题
            choices = [word['definition']]
            other_defs = [w['definition'] for w in words if w != word]
            
            # 修复：使用random.choices替代sample避免数量不足
            selected_defs = random.choices(other_defs, k=3) if other_defs else ["暂缺选项1", "暂缺选项2", "暂缺选项3"]
            choices += selected_defs
            
            random.shuffle(choices)
            
            main_questions.append({
                "type": "choose",
                "text": word['word'],
                "choices": choices,
                "answer": choices.index(word['definition'])
            })
            
            # 填空题
            main_questions.append({
                "type": "blank",
                "text": f"{word['definition']}的英文单词是？",
                "answer": word['word']
            })

        # 保存主题库
        main_file = f"{unit}.json"
        with open(f"tests/{main_file}", 'w', encoding='utf-8') as f:
            json.dump(main_questions, f, ensure_ascii=False, indent=2)

        # 生成子题库（基础/进阶/真题）
        for subtype in ["基础", "进阶", "真题"]:
            sub_questions = []
            # 每种题型各取2题
            choose_qs = [q for q in main_questions if q['type'] == 'choose']
            blank_qs = [q for q in main_questions if q['type'] == 'blank']
            
            # 添加安全采样逻辑
            try:
                sub_questions.extend(random.sample(choose_qs, min(2, len(choose_qs))))
                sub_questions.extend(random.sample(blank_qs, min(2, len(blank_qs))))
            except ValueError as e:
                print(f"警告：单元 {unit} 的{subtype}题库生成失败，请确保包含至少2个单词（当前：{len(words)}个）")
                continue

            sub_file = main_file.replace(".json", f"-{subtype}.json")
            with open(f"tests/{sub_file}", 'w', encoding='utf-8') as f:
                json.dump(sub_questions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate_subtests()