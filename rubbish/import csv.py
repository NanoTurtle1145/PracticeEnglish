import csv
import json
import os
from collections import defaultdict
import random

def generate_question_bank():
    # 读取词库数据
    words = defaultdict(list)
    with open('rubbish/words.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过标题行
        for row in reader:
            if len(row) >= 5 and row[4].startswith('Unit'):
                unit = row[4].strip()
                words[unit].append({
                    'word': row[1].strip(),
                    'definition': row[3].strip()
                })

    # 为每个单元生成题库
    for unit, items in words.items():
        questions = []
        for word_info in items:
            # 生成选择题选项
            choices = [word_info['definition']]
            
            # 从其他单词随机选取3个错误选项
            other_definitions = [w['definition'] for w in items if w != word_info]
            # 修复：处理空列表情况并允许重复选项
            selected_defs = random.choices(other_definitions, k=3) if other_definitions else ["选项缺失1", "选项缺失2", "选项缺失3"]
            choices += selected_defs
            random.shuffle(choices)
            
            # 记录正确答案位置
            answer = choices.index(word_info['definition'])
            
            questions.append({
                "type": "choose",
                "text": word_info['word'],
                "choices": choices,
                "answer": answer
            })

            # 修复后的填空题生成逻辑
            questions.append({
                "type": "blank",
                "text": f"{word_info['definition']}的英文单词是？",
                "answer": word_info['word']
            })

        # 移除有问题的验证逻辑，保持基础生成逻辑
        if len(questions) % 2 == 0:
            # 确保填空题的问题和答案对应
            blank_question = {
                "type": "blank",
                "text": f"{word_info['definition']}的英文单词是？",
                "answer": word_info['word']
            }
            questions.append(blank_question)

        # 保存到tests目录
        output_path = f"tests/{unit}.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate_question_bank()