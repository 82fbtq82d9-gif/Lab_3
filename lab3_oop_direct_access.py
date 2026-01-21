"""
ООП подход с прямым доступом к приватным полям
Нарушение инкапсуляции для упрощения кода
"""
import json
import datetime as dt
from typing import Dict, List, Any, Set
import uuid


class PersonDirectAccess:
    """Класс Person с приватными полями, но доступными для прямого доступа"""
    
    def __init__(self, name: str, born_in: dt.datetime) -> None:
        self._name = name
        self._friends: List['PersonDirectAccess'] = []
        self._born_in = born_in
        self._id = str(uuid.uuid4())
    
    def add_friend(self, friend: 'PersonDirectAccess') -> None:
        """Добавление друга (взаимная связь)"""
        if friend not in self._friends:
            self._friends.append(friend)
            if self not in friend._friends:
                friend.add_friend(self)


class DirectAccessSerializer:
    """Сериализатор с прямым доступом к приватным полям"""
    
    @staticmethod
    def serialize(person: PersonDirectAccess) -> bytes:
        """
        Сериализация с прямым доступом к полям _name, _friends, _born_in
        
        Нарушение инкапсуляции: прямой доступ к приватным полям
        """
        objects_to_save: List[Dict[str, Any]] = []
        visited_ids: Set[str] = set()
        
        def collect_objects(p: PersonDirectAccess) -> None:
            if p._id in visited_ids:  # Прямой доступ к _id
                return
            
            visited_ids.add(p._id)
            
            # ПРЯМОЙ ДОСТУП к приватным полям - нарушение инкапсуляции!
            obj_data = {
                'id': p._id,
                'name': p._name,  # Напрямую обращаемся к приватному полю
                'born_in': p._born_in.isoformat(),  # Напрямую!
                'friends': [friend._id for friend in p._friends]  # Напрямую!
            }
            objects_to_save.append(obj_data)
            
            # Рекурсивно собираем друзей
            for friend in p._friends:  # Прямой доступ
                collect_objects(friend)
        
        collect_objects(person)
        return json.dumps(objects_to_save, indent=2).encode('utf-8')
    
    @staticmethod
    def deserialize(data: bytes) -> PersonDirectAccess:
        """
        Десериализация с прямым доступом к приватным полям
        
        Создание объектов без использования конструктора
        """
        objects_data = json.loads(data.decode('utf-8'))
        obj_cache: Dict[str, PersonDirectAccess] = {}
        
        # Фаза 1: Создание объектов без вызова __init__
        for obj_data in objects_data:
            # Создаем объект без конструктора
            obj = PersonDirectAccess.__new__(PersonDirectAccess)
            # Прямой доступ для установки значений
            obj._id = obj_data['id']
            obj._name = obj_data['name']
            obj._born_in = dt.datetime.fromisoformat(obj_data['born_in'])
            obj._friends = []  # Временный пустой список
            obj_cache[obj._id] = obj
        
        # Фаза 2: Восстановление связей
        for obj_data in objects_data:
            obj = obj_cache[obj_data['id']]
            # Прямой доступ для восстановления связей
            obj._friends = [obj_cache[friend_id] for friend_id in obj_data['friends']]
        
        return obj_cache[objects_data[0]['id']]


# Демонстрация работы
if __name__ == "__main__":
    print("=== ООП подход без инкапсуляции (прямой доступ) ===")
    
    # Создание объектов
    p1 = PersonDirectAccess("Иван", dt.datetime(1990, 5, 15))
    p2 = PersonDirectAccess("Мария", dt.datetime(1992, 8, 22))
    p3 = PersonDirectAccess("Алексей", dt.datetime(1988, 3, 10))
    
    # Создание сложных связей
    p1.add_friend(p2)
    p2.add_friend(p3)
    p3.add_friend(p1)  # Явная циклическая ссылка
    
    # Сериализация
    serializer = DirectAccessSerializer()
    serialized_data = serializer.serialize(p1)
    
    print(f"Сериализованные данные ({len(serialized_data)} байт):")
    print(serialized_data.decode('utf-8'))
    
    # Десериализация
    restored_person = serializer.deserialize(serialized_data)
    
    # Проверка с прямым доступом к полям
    print(f"\nВосстановленный объект (прямой доступ к полям):")
    print(f"Имя (через _name): {restored_person._name}")  # Нарушение инкапсуляции!
    print(f"Дата рождения (через _born_in): {restored_person._born_in}")  # Нарушение!
    print(f"Количество друзей (через _friends): {len(restored_person._friends)}")
    
    if restored_person._friends:
        print(f"Первый друг (через _friends[0]._name): {restored_person._friends[0]._name}")
    
    # Демонстрация проблемы: мы можем напрямую изменить приватные поля
    print(f"\nДемонстрация проблемы безопасности:")
    print(f"До изменения: {restored_person._name}")
    restored_person._name = "ВзломанныйИван"  # Можем напрямую изменить!
    print(f"После прямого изменения: {restored_person._name}")
