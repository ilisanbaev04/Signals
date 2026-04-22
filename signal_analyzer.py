import numpy as np

class SignalAnalyzer:
    """
    Класс для анализа одномерного сигнала.
    Принимает массив y (значения сигнала), x по умолчанию - индексы.
    """
    def __init__(self, y, x=None):
        self.y = np.asarray(y, dtype=float)
        if x is None:
            self.x = np.arange(len(self.y))
        else:
            self.x = np.asarray(x, dtype=float)
            assert len(self.x) == len(self.y), "x и y должны быть одинаковой длины"

    def get_mean_line(self):
        mean_val = np.mean(self.y)
        return mean_val


    def get_global_max(self):
        idx = np.argmax(self.y)
        return self.x[idx], self.y[idx]


    def get_global_min(self):
        idx = np.argmin(self.y)
        return self.x[idx], self.y[idx]


    def get_local_extrema(self):

        maxima_x, maxima_y = [], []
        minima_x, minima_y = [], []
        for i in range(1, len(self.y) - 1):
            if self.y[i] > self.y[i-1] and self.y[i] > self.y[i+1]:
                maxima_x.append(self.x[i])
                maxima_y.append(self.y[i])
            elif self.y[i] < self.y[i-1] and self.y[i] < self.y[i+1]:
                minima_x.append(self.x[i])
                minima_y.append(self.y[i])
        return (maxima_x, maxima_y), (minima_x, minima_y)


    def get_inflection_points(self):
        if len(self.y) < 3:
            return [], []
        d2 = np.diff(np.diff(self.y))
        inflection_idx = []
        for i in range(len(d2)-1):
            if d2[i] * d2[i+1] < 0:

                inflection_idx.append(i+1)

        inflection_idx = sorted(set(inflection_idx))
        x_inf = [self.x[i] for i in inflection_idx]
        y_inf = [self.y[i] for i in inflection_idx]
        return x_inf, y_inf


    def find_periodic_segment(self, tolerance=0.05, min_period_len=3):
        """
        tolerance: допустимая относительная погрешность сравнения значений (0.05 = 5%)
        min_period_len: минимальная длина периода (в точках)
        """
        y = self.y
        n = len(y)
        best_start, best_end = None, None
        best_len = 0


        for period in range(min_period_len, n//2 + 1):

            for start in range(0, n - 2*period + 1):

                seg1 = y[start:start+period]
                seg2 = y[start+period:start+2*period]

                ok = True
                for a, b in zip(seg1, seg2):
                    if abs(a - b) > tolerance * max(1.0, abs(a)):
                        ok = False
                        break
                if ok:

                    left = start
                    right = start + 2*period

                    while left - period >= 0:
                        prev_seg = y[left-period:left]
                        curr_seg = y[left:left+period]
                        match = all(abs(a-b) <= tolerance * max(1.0, abs(a)) for a,b in zip(prev_seg, curr_seg))
                        if match:
                            left -= period
                        else:
                            break

                    while right + period <= n:
                        next_seg = y[right:right+period]
                        curr_seg = y[right-period:right]
                        match = all(abs(a-b) <= tolerance * max(1.0, abs(a)) for a,b in zip(curr_seg, next_seg))
                        if match:
                            right += period
                        else:
                            break
                    segment_len = right - left
                    if segment_len > best_len:
                        best_len = segment_len
                        best_start, best_end = left, right
        if best_len > 0:
            return self.x[best_start], self.x[best_end-1]
        else:
            return None