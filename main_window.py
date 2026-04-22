import sys
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QCheckBox, QGroupBox,
                             QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from signal_analyzer import SignalAnalyzer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализ одномерного сигнала")
        self.setGeometry(100, 100, 1000, 700)


        self.x = None
        self.y = None
        self.analyzer = None


        self.mean_val = None
        self.global_max = None
        self.global_min = None
        self.local_max = None
        self.local_min = None
        self.inflection = None
        self.periodic_segment = None


        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)


        control_panel = QVBoxLayout()
        control_panel.setAlignment(Qt.AlignTop)


        btn_load = QPushButton("Загрузить сигнал из файла")
        btn_load.clicked.connect(self.load_signal)
        control_panel.addWidget(btn_load)

        btn_test = QPushButton("Сгенерировать тестовый сигнал")
        btn_test.clicked.connect(self.generate_test_signal)
        control_panel.addWidget(btn_test)


        group = QGroupBox("Отображаемые элементы")
        group_layout = QVBoxLayout()
        self.cb_mean = QCheckBox("Средняя линия")
        self.cb_mean.setChecked(True)
        self.cb_global_max = QCheckBox("Глобальный максимум")
        self.cb_global_max.setChecked(True)
        self.cb_global_min = QCheckBox("Глобальный минимум")
        self.cb_global_min.setChecked(True)
        self.cb_local_extrema = QCheckBox("Локальные экстремумы")
        self.cb_local_extrema.setChecked(True)
        self.cb_inflection = QCheckBox("Точки перегиба")
        self.cb_inflection.setChecked(True)
        self.cb_periodic = QCheckBox("Периодический участок")
        self.cb_periodic.setChecked(True)

        group_layout.addWidget(self.cb_mean)
        group_layout.addWidget(self.cb_global_max)
        group_layout.addWidget(self.cb_global_min)
        group_layout.addWidget(self.cb_local_extrema)
        group_layout.addWidget(self.cb_inflection)
        group_layout.addWidget(self.cb_periodic)
        group.setLayout(group_layout)
        control_panel.addWidget(group)


        btn_refresh = QPushButton("Обновить график")
        btn_refresh.clicked.connect(self.update_plot)
        control_panel.addWidget(btn_refresh)


        btn_save = QPushButton("Сохранить график")
        btn_save.clicked.connect(self.save_plot)
        control_panel.addWidget(btn_save)

        control_panel.addStretch()

        left_widget = QWidget()
        left_widget.setLayout(control_panel)
        main_layout.addWidget(left_widget, 1)


        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas, 4)


        for cb in [self.cb_mean, self.cb_global_max, self.cb_global_min,
                   self.cb_local_extrema, self.cb_inflection, self.cb_periodic]:
            cb.stateChanged.connect(self.update_plot)

    def load_signal(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл сигнала", "",
                                                   "Text files (*.txt *.csv);;All files (*)")
        if not file_path:
            return
        try:
            with open(file_path, 'r') as f:
                data = f.read().strip()
            data = data.replace(',', ' ')
            numbers = list(map(float, data.split()))
            if len(numbers) < 3:
                QMessageBox.warning(self, "Ошибка", "Файл должен содержать минимум 3 числа")
                return
            self.y = np.array(numbers)
            self.x = np.arange(len(self.y))
            self._perform_analysis()
            self.update_plot()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def generate_test_signal(self):
        t = np.linspace(0, 10, 300)
        y = np.sin(2 * np.pi * 0.5 * t) + 0.1 * np.random.randn(len(t))
        pattern = np.sin(2 * np.pi * 1.2 * np.linspace(0, 2, 50))
        y[100:150] = pattern[:50]
        y[150:200] = pattern[:50]
        self.x = t
        self.y = y
        self._perform_analysis()
        self.update_plot()

    def _perform_analysis(self):
        if self.y is None:
            return
        self.analyzer = SignalAnalyzer(self.y, self.x)
        self.mean_val = self.analyzer.get_mean_line()
        self.global_max = self.analyzer.get_global_max()
        self.global_min = self.analyzer.get_global_min()
        self.local_max, self.local_min = self.analyzer.get_local_extrema()
        self.inflection = self.analyzer.get_inflection_points()
        self.periodic_segment = self.analyzer.find_periodic_segment(tolerance=0.1)

    def update_plot(self):
        if self.y is None:
            return
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.plot(self.x, self.y, 'b-', linewidth=1.5, label='Сигнал')

        if self.cb_mean.isChecked() and self.mean_val is not None:
            ax.axhline(y=self.mean_val, color='gray', linestyle='--', linewidth=1.5, label='Средняя линия')

        if self.cb_global_max.isChecked() and self.global_max is not None:
            xm, ym = self.global_max
            ax.plot(xm, ym, 'ro', markersize=8, label='Глобальный максимум')

        if self.cb_global_min.isChecked() and self.global_min is not None:
            xm, ym = self.global_min
            ax.plot(xm, ym, 'go', markersize=8, label='Глобальный минимум')

        if self.cb_local_extrema.isChecked():
            max_x, max_y = self.local_max
            min_x, min_y = self.local_min
            if max_x:
                ax.plot(max_x, max_y, 'r^', markersize=6, label='Локальные максимумы')
            if min_x:
                ax.plot(min_x, min_y, 'gv', markersize=6, label='Локальные минимумы')

        if self.cb_inflection.isChecked() and self.inflection is not None:
            ix, iy = self.inflection
            if ix:
                ax.plot(ix, iy, 'ms', markersize=6, label='Точки перегиба')

        if self.cb_periodic.isChecked() and self.periodic_segment is not None:
            start, end = self.periodic_segment
            ax.axvspan(start, end, alpha=0.3, color='yellow', label='Периодический участок')

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Анализ одномерного сигнала")
        ax.legend(loc='best')
        ax.grid(True, linestyle=':', alpha=0.6)
        self.figure.tight_layout()
        self.canvas.draw()

    def save_plot(self):
        """Сохраняет текущий график в файл (PNG, PDF, SVG)"""
        if self.y is None:
            QMessageBox.warning(self, "Предупреждение", "Нет данных для сохранения графика.")
            return
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Сохранить график",
            "",
            "PNG Image (*.png);;PDF Document (*.pdf);;SVG Vector (*.svg)"
        )
        if file_path:
            try:

                self.update_plot()

                self.figure.savefig(file_path, dpi=150, bbox_inches='tight')
                QMessageBox.information(self, "Успех", f"График сохранён:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить график:\n{str(e)}")