"""
ООП подход с соблюдением инкапсуляции
Использование публичного API для сериализации
"""
import json
import datetime as dt
from typing import Dict, List, Any, Optional, Set
import uuid


class Person:
    """
    Класс Person с инкапсуляцией данных.
    Доступ к приватным полям только через публичные методы.
    """
    
    def __init__(self, name: str, born_in: dt.datetime) -> None:
        """
        Инициализация объекта Person.
        
        Args:
            name: Имя человека
            born_in: Дата рождения
        """
        self._name = name
        self._friends: List['Person'] = []
        self._born_in = born_in
        self._id = str(uuid.uuid4())  # Уникальный идентификатор
    
    def add_friend(self, friend: 'Person') -> None:
        """Добавление друга (взаимная связь)"""
        if friend not in self._friends:
            self._friends.append(friend)
            if self not in friend._friends:
                friend.add_friend(self)
    
    # Публичные геттеры (интерфейс для доступа к данным)
    def get_name(self) -> str:
        return self._name
    
    def get_birth_date(self) -> dt.datetime:
        return self._born_in
    
    def get_friends(self) -> List['Person']:
        return self._friends.copy()  # Возвращаем копию для защиты
    
    def get_id(self) -> str:
        return self._id
    
    # Методы сериализации
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта в словарь для сериализации"""
        return {
            'id': self._id,
            'name': self._name,
            'born_in': self._born_in.isoformat(),
            'friends': [friend._id for friend in self._friends]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        """Создание объекта из словаря"""
        obj = cls.__new__(cls)
        obj._id = data['id']
        obj._name = data['name']
        obj._born_in = dt.datetime.fromisoformat(data['born_in'])
        obj._friends = []  # Временный пустой список
        return obj


class PersonSerializer:
    """Сериализатор объектов Person с соблюдением инкапсуляции"""
    
    @staticmethod
    def serialize(person: Person) -> bytes:
        """
        Сериализация объекта Person в байты (JSON)
        
        Args:
            person: Объект для сериализации
            
        Returns:
            Байтовое представление в формате JSON
        """
        objects_to_save: List[Dict[str, Any]] = []
        visited_ids: Set[str] = set()
        
        def collect_objects(p: Person) -> None:
            """Рекурсивный сбор всех объектов в графе связей"""
            if p.get_id() in visited_ids:
                return
            
            visited_ids.add(p.get_id())
            objects_to_save.append(p.to_dict())
            
            # Рекурсивно обрабатываем друзей
            for friend in p.get_friends():
                collect_objects(friend)
        
        collect_objects(person)
        return json.dumps(objects_to_save, indent=2).encode('utf-8')
    
    @staticmethod
    def deserialize(data: bytes) -> Person:
        """
        Десериализация байтов в объект Person
        
        Args:
            data: Байтовое представление в формате JSON
            
        Returns:
            Восстановленный объект Person
        """
        objects_data = json.loads(data.decode('utf-8'))
        obj_cache: Dict[str, Person] = {}
        
        # Фаза 1: Создание всех объектов
        for obj_data in objects_data:
            obj_cache[obj_data['id']] = Person.from_dict(obj_data)
        
        # Фаза 2: Восстановление связей
        for obj_data in objects_data:
            person = obj_cache[obj_data['id']]
            person._friends = [obj_cache[friend_id] for friend_id in obj_data['friends']]
        
        return obj_cache[objects_data[0]['id']]


# Демонстрация работы
if __name__ == "__main__":
    print("=== ООП подход с инкапсуляцией ===")
    
    # Создание объектов
    p1 = Person("Иван", dt.datetime(1990, 5, 15))
    p2 = Person("Мария", dt.datetime(1992, 8, 22))
    p3 = Person("Алексей", dt.datetime(1988, 3, 10))
    
    # Создание связей
    p1.add_friend(p2)
    p1.add_friend(p3)
    p2.add_friend(p3)  # Создает циклическую ссылку через p3
    
    # Сериализация
    serializer = PersonSerializer()
    serialized_data = serializer.serialize(p1)
    
    print(f"Сериализованные данные ({len(serialized_data)} байт):")
    print(serialized_data[:200].decode('utf-8') + "...")
    
    # Десериализация
    restored_person = serializer.deserialize(serialized_data)
    
    # Проверка
    print(f"\nВосстановленный объект:")
    print(f"Имя: {restored_person.get_name()}")
    print(f"Дата рождения: {restored_person.get_birth_date()}")
    print(f"Количество друзей: {len(restored_person.get_friends())}")
    
    if restored_person.get_friends():
        print(f"Первый друг: {restored_person.get_friends()[0].get_name()}")
        print(f"Второй друг: {restored_person.get_friends()[1].get_name()}")
    
    # Проверка циклической ссылки
    print(f"\nПроверка циклических ссылок:")
    print(f"У {restored_person.get_friends()[0].get_name()} друзей: "
          f"{len(restored_person.get_friends()[0].get_friends())}")
