class CopyMaker():
    def set_copy(self):
        # Создаем новый объект того же класса
        self.copy = self.__class__()
        # Перебираем все атрибуты текущего объекта
        for attr_name in dir(self):
            # Проверяем, что это не метод и не приватный атрибут
            if not attr_name.startswith('__') and not callable(getattr(self, attr_name)):
                # Получаем значение атрибута
                value = getattr(self, attr_name)
                # Проверяем, является ли атрибут списком
                if isinstance(value, list):
                    # Копируем список, чтобы избежать ссылок на один и тот же объект
                    l = 0
                    if value:
                        l = len(value)
                    copy_value = [None] * l
                    for i, v in enumerate(value):
                        v.set_copy()
                        copy_value[i] = v.get_copy()
                    setattr(self.copy, attr_name, copy_value)
                else:
                    # Копируем значение атрибута в копию объекта
                    setattr(self.copy, attr_name, value)

    def get_copy(self):
        return self.copy
