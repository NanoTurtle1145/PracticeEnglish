from PyQt5.QtCore import QPoint, QTimer
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox  # 添加QLabel和QMessageBox导入
import random  # 添加random模块导入

class ParticleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        for _ in range(50):
            self.particles.append({
                'pos': QPoint(random.randint(0, 800), random.randint(0, 600)),
                'size': random.randint(5, 20),
                'color': QColor(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    80
                ),
                'speed': random.uniform(0.5, 2)
            })
            
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(30)
        
        # 添加版本标签
        self.version_label = QLabel("v1.0", self)
        self.version_label.setStyleSheet("color: white; font-size: 10px;")
        self.version_label.move(10, 10)
        self.version_label.mousePressEvent = self.handle_version_click
        self.click_count = 0

    def handle_version_click(self, event):
        self.click_count += 1
        if self.click_count >= 10:
            self.click_count = 0
            dialog = QMessageBox()
            dialog.setWindowTitle("关于")
            dialog.setText("Practice English v1.0\n\n点击十次触发彩蛋")
            dialog.exec_()

    def update_particles(self):
        for p in self.particles:
            new_x = p['pos'].x() + p['speed']
            p['pos'].setX(int(new_x))  # 将浮点数转换为整数
            if p['pos'].x() > self.width():
                p['pos'].setX(0)
                p['pos'].setY(random.randint(0, self.height()))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 限制绘制区域，避开控件区域
        for p in self.particles:
            if p['pos'].y() > 150:  # 假设控件在y=150以上区域
                painter.setBrush(p['color'])
                painter.drawEllipse(p['pos'], p['size'], p['size'])