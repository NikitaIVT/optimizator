from collections import defaultdict
from datetime import time, timedelta, datetime
from typing import List, Tuple, Dict, Optional


class TimeSlotManager:
    def __init__(self, shift_start: time, shift_end: time):
        """
        :param shift_start: Время начала рабочей смены (например, time(9, 0))
        :param shift_end: Время окончания рабочей смены (например, time(17, 0))
        """
        self.busy_intervals = defaultdict(list)  # {wp_id: [(start, end)]}
        self.total_busy_time = defaultdict(float)  # {wp_id: total_hours}
        self.shift_start = shift_start
        self.shift_end = shift_end
        self.global_start = None
        self.global_end = None

    def add_interval(self, wp_id: int, start: datetime, end: datetime) -> None:
        """Добавляет занятый интервал и обновляет статистику"""
        # Сохраняем интервал
        intervals = self.busy_intervals[wp_id]
        intervals.append((start, end))

        # Обновляем глобальные даты
        if self.global_start is None or start < self.global_start:
            self.global_start = start
        if self.global_end is None or end > self.global_end:
            self.global_end = end

        # Объединяем пересекающиеся интервалы
        if len(intervals) > 1:
            intervals.sort()
            merged = []
            current_start, current_end = intervals[0]

            for s, e in intervals[1:]:
                if s <= current_end:
                    current_end = max(current_end, e)
                else:
                    merged.append((current_start, current_end))
                    current_start, current_end = s, e
            merged.append((current_start, current_end))
            self.busy_intervals[wp_id] = merged
        else:
            merged = intervals

        # Пересчитываем суммарное время
        total_seconds = 0
        for s, e in merged:
            total_seconds += (e - s).total_seconds()
        self.total_busy_time[wp_id] = round(total_seconds / 3600, 2)

    def get_free_slots(self, wp_id: int) -> List[Tuple[datetime, datetime]]:
        """Возвращает свободные слоты для конкретного рабочего места"""
        if self.global_start is None or self.global_end is None:
            return []

        free_slots = []
        current_date = self.global_start.date()
        end_date = self.global_end.date()

        while current_date <= end_date:
            # Определяем границы рабочего дня
            day_start = datetime.combine(current_date, self.shift_start)
            day_end = datetime.combine(current_date, self.shift_end)

            # Находим пересечения с занятыми интервалами
            busy = []
            for s, e in self.busy_intervals[wp_id]:
                if (s < day_end) and (e > day_start):
                    overlap_start = max(s, day_start)
                    overlap_end = min(e, day_end)
                    busy.append((overlap_start, overlap_end))

            # Сортируем занятые интервалы
            busy.sort()

            # Вычисляем свободные промежутки
            current_time = day_start
            for s, e in busy:
                if current_time < s:
                    free_slots.append((current_time, s))
                current_time = max(current_time, e)

            if current_time < day_end:
                free_slots.append((current_time, day_end))

            current_date += timedelta(days=1)

        return free_slots

    def print_free_slots(self) -> None:
        """Выводит все свободные слоты и суммарное время работы"""
        if not self.busy_intervals:
            print("Нет данных о занятости")
            return

        if self.global_start is None or self.global_end is None:
            print("Нет временных рамок")
            return

        for wp_id in sorted(self.busy_intervals.keys()):
            free_slots = self.get_free_slots(wp_id)
            total_time = self.total_busy_time.get(wp_id, 0.0)

            print(f"\nРабочее место {wp_id}:")
            print(f"  Занято суммарно: {total_time} ч")

            if not free_slots:
                print("  Свободных слотов нет")
                continue

            current_date = None
            for start, end in free_slots:
                # Группируем по датам
                if current_date != start.date():
                    current_date = start.date()
                    print(f"  {current_date.strftime('%Y-%m-%d')}:")

                print(f"    {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")

if __name__ == '__main__':
    manager = TimeSlotManager(time(9, 0), time(18, 0))
    manager.add_interval(choosen_wp, spaces_for_cal[choosen_wp][0]["start"], spaces_for_cal[choosen_wp][0]["end"])
    manager.print_free_slots()