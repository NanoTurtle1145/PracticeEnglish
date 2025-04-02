import json
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic  # 添加uic模块导入
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtWidgets import QWidget  # 确保QWidget已导入
from particles import ParticleWidget  # 添加这行导入
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect  # 添加QRect导入
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QApplication, QGraphicsOpacityEffect, QWidget
from particles import ParticleWidget
import PyQt5 

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow ")
        MainWindow.resize(592, 418)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 使用垂直布局
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # 测试选择部分（调整控件顺序）
        test_choice_layout = QtWidgets.QHBoxLayout()
        self.choose_test = QtWidgets.QComboBox()
        self.choose_test.setObjectName("choose_test")
        self.add_test()
        
        self.start = QtWidgets.QPushButton("Start!")
        self.start.setObjectName("start")
        self.start.clicked.connect(self.start_test)
        
        self.exit_button = QtWidgets.QPushButton("退出")
        self.exit_button.setObjectName("exit")
        self.exit_button.clicked.connect(self.exit_test)
        
        test_choice_layout.addWidget(self.choose_test)
        test_choice_layout.addWidget(self.start)
        test_choice_layout.addWidget(self.exit_button)

        self.label = QtWidgets.QLabel("    Let's Practise English!")
        font = QtGui.QFont()
        font.setPointSize(14)  # 加大字号
        font.setBold(True)    # 加粗
        self.label.setFont(font)
        self.label.setObjectName("label")

        # 问题显示部分
        question_layout = QtWidgets.QVBoxLayout()
        self.text = QtWidgets.QLabel("Your test here...")
        self.text.setObjectName("text")
        question_layout.addWidget(self.text)

        # 选项部分
        choices_layout = QtWidgets.QVBoxLayout()
        self.choice1 = QtWidgets.QPushButton("A...")
        self.choice1.setObjectName("choice1")
        self.choice2 = QtWidgets.QPushButton("B...")
        self.choice2.setObjectName("choice2")
        self.choice3 = QtWidgets.QPushButton("C...")
        self.choice3.setObjectName("choice3")
        self.choice4 = QtWidgets.QPushButton("D...")
        self.choice4.setObjectName("choice4")
        choices_layout.addWidget(self.choice1)
        choices_layout.addWidget(self.choice2)
        choices_layout.addWidget(self.choice3)
        choices_layout.addWidget(self.choice4)

        # 填空部分
        blank_layout = QtWidgets.QHBoxLayout()
        self.ans = QtWidgets.QLineEdit()
        self.ans.setObjectName("ans")
        self.submit_button = QtWidgets.QPushButton("提交")
        self.submit_button.setObjectName("submit_button")
        self.submit_button.clicked.connect(self.check_answer)
        blank_layout.addWidget(self.ans)
        blank_layout.addWidget(self.submit_button)

        # 添加到主布局
        main_layout.addWidget(self.label)
        main_layout.addLayout(test_choice_layout)
        main_layout.addLayout(question_layout)
        main_layout.addLayout(choices_layout)
        main_layout.addLayout(blank_layout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 592, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.score = 0

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # 连接选择按钮的点击事件
        self.choice1.clicked.connect(lambda: self.check_answer(0))
        self.choice2.clicked.connect(lambda: self.check_answer(1))
        self.choice3.clicked.connect(lambda: self.check_answer(2))
        self.choice4.clicked.connect(lambda: self.check_answer(3))

        # 连接 QLineEdit 的回车键事件
        self.ans.returnPressed.connect(self.check_answer)

        # 初始化时禁用选项按钮
        self.disable_choices()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PractiseEnglish"))
        self.label.setText(_translate("MainWindow", "    Let\'s Practise English!"))
        self.start.setText(_translate("MainWindow", "Start!"))
        self.choice1.setText(_translate("MainWindow", "A..."))
        self.choice4.setText(_translate("MainWindow", "D..."))
        self.choice3.setText(_translate("MainWindow", "C..."))
        self.choice2.setText(_translate("MainWindow", "B..."))
        self.text.setText(_translate("MainWindow", "Your test here..."))

    def add_test(self):
        files = os.listdir('tests')
        for file in files:
            if file.endswith('.json'):
                file_name = os.path.splitext(file)[0]  # 去掉 .json 后缀
                self.choose_test.addItem(file_name)

    def start_test(self):
        self.data = []
        try:
            with open("tests/" + self.choose_test.currentText() + '.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.current_question_index = 0
            self.score = 0
            self.show_question()
            self.enable_choices()  # 启用选项按钮

            # 禁用 start 按钮和 choose_test 下拉菜单
            self.start.setEnabled(False)
            self.choose_test.setEnabled(False)
        except FileNotFoundError:
            self.label.setText("Test file not found!")
        except json.JSONDecodeError:
            self.label.setText("Error decoding JSON file!")
        except Exception as e:
            self.label.setText(f"An error occurred: {str(e)}")

    def show_question(self):
        if self.current_question_index < len(self.data):
            question = self.data[self.current_question_index]
            self.text.setText(question['text'])
            if question['type'] == 'choose':
                self.choice1.setText(question['choices'][0])
                self.choice2.setText(question['choices'][1])
                self.choice3.setText(question['choices'][2])
                self.choice4.setText(question['choices'][3])
                self.ans.setVisible(False)
                self.choice1.setVisible(True)
                self.choice2.setVisible(True)
                self.choice3.setVisible(True)
                self.choice4.setVisible(True)
                self.submit_button.setEnabled(False)  # 禁用提交按钮
            elif question['type'] == 'blank':
                self.choice1.setVisible(False)
                self.choice2.setVisible(False)
                self.choice3.setVisible(False)
                self.choice4.setVisible(False)
                self.ans.setVisible(True)
                self.ans.setText("")  # 重置 QLineEdit 内容
                self.submit_button.setEnabled(True)  # 启用提交按钮
        else:
            # 检查最后一道题的答案
            self.check_answer()
            self.show_final_result()

    def check_answer(self, choice_index=None):
        if not hasattr(self, 'data') or not self.data:
            self.label.setText("请先开始测试！")
            return

        question = self.data[self.current_question_index]
        if question['type'] == 'choose':
            if choice_index is not None and choice_index == question['answer']:
                self.label.setText("正确！")
                self.score += 1
            else:
                correct_answer = question['choices'][question['answer']]
                self.label.setText(f"错误！正确答案是：{correct_answer}")
        elif question['type'] == 'blank':
            user_answer = self.ans.text().strip()
            if user_answer == question['answer']:
                self.label.setText("正确！")
                self.score += 1
            else:
                self.label.setText(f"错误！正确答案是：{question['answer']}")

        self.current_question_index += 1

        if self.current_question_index < len(self.data):
            self.show_question()
        else:
            # 检查最后一道题的答案
            self.show_final_result()

    def show_final_result(self):
        self.label.setText("测试结束，你的正确率是：" + str(self.score / len(self.data) * 100) + "%" +
                           " (" + str(self.score) + "/" + str(len(self.data)) + ")")
        self.disable_choices()
        # 启用 start 按钮和 choose_test 下拉菜单
        self.start.setEnabled(True)
        self.choose_test.setEnabled(True)

    def disable_choices(self):
        self.choice1.setEnabled(False)
        self.choice2.setEnabled(False)
        self.choice3.setEnabled(False)
        self.choice4.setEnabled(False)
        self.ans.setEnabled(False)
        self.submit_button.setEnabled(False)

    def enable_choices(self):
        self.choice1.setEnabled(True)
        self.choice2.setEnabled(True)
        self.choice3.setEnabled(True)
        self.choice4.setEnabled(True)
        self.ans.setEnabled(True)
        self.submit_button.setEnabled(False)  # 初始化时禁用提交按钮

    def exit_test(self):
        """中途退出测试"""
        if hasattr(self, 'data') and self.data:
            # 计算当前正确率
            current_progress = f"当前正确率：{self.score}/{self.current_question_index}"
            self.label.setText(f"已退出测试，{current_progress}")
            
            # 重置测试状态
            self.current_question_index = 0
            self.score = 0
            del self.data
            
            # 恢复界面状态
            self.disable_choices()
            self.start.setEnabled(True)
            self.choose_test.setEnabled(True)
            self.text.setText("Your test here...")
    def show_about_dialog(self):
        about_dialog = QtWidgets.QDialog()
        about_dialog.setWindowTitle("关于")
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Practice English v0.1.7-Alpha\n\n点击十次触发彩蛋")
        layout.addWidget(label)
        ok_button = QtWidgets.QPushButton("OK")
        ok_button.clicked.connect(about_dialog.close)
        layout.addWidget(ok_button)
        about_dialog.setLayout(layout)
        about_dialog.exec_()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QtWidgets.QApplication(sys.argv)
    
    # 添加样式表
    style_sheet = """
    QMainWindow {
        background-color: #f0f8ff;
    }
    QLabel {
        font-size: 12px;
        color: #333;
    }
    QPushButton {
        background-color: #007BFF;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: #0056b3;
    }
    QComboBox {
        background-color: white;
        border: 1px solid #ccc;
        padding: 3px;
        border-radius: 3px;
    }
    QLineEdit {
        background-color: white;
        border: 1px solid #ccc;
        padding: 3px;
        border-radius: 3px;
    }
    """
    app.setStyleSheet(style_sheet)

    MainWindow = QtWidgets.QMainWindow()
    
    # 创建粒子效果部件
    particle_widget = ParticleWidget(MainWindow)
    particle_widget.lower()  # 置于底层
    
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    # 添加版本号标签
    version_label = QtWidgets.QLabel("v0.1.7-Alpha", MainWindow)
    version_label.setStyleSheet("color: #666666; font-size: 10px;")
    version_label.move(MainWindow.width() - 80, MainWindow.height() - 30)
    version_label.mousePressEvent = lambda event: ui.show_about_dialog()
    
    MainWindow.show()
    sys.exit(app.exec_())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置半透明窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 添加阴影效果
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.shadow.setOffset(0, 0)
        
        # 创建中心部件
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.central_widget.setGraphicsEffect(self.shadow)
        self.central_widget.setStyleSheet("""
            #CentralWidget {
                background: rgba(50, 50, 50, 200);
                border-radius: 15px;
            }
        """)
        
        # 添加进入动画
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(0.95)
        self.fade_in.setEasingCurve(QEasingCurve.InOutQuad)
        
    def showEvent(self, event):
        self.fade_in.start()
        super().showEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

    # 添加关于对话框方法到Ui_MainWindow类中（确保在setupUi之后）
    