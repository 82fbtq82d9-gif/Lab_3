"""
Функциональный подход к сериализации объектов Person
Использование чистых функций и структур данных
"""
import json
import datetime as dt
from typing import Dict, List, Any, Set, Tuple, Callable, Optional
import uuid

# Типы для функционального подхода
PersonData = Dict[str, Any]
PersonFactory = Callable[[str, dt.datetime], PersonData]


def create_person_data(name: str, born_in: dt.datetime) -> PersonData:
    """
    Создание структуры данных, представляющей человека
    
    Args:
        name: Имя человека
        born_in: Дата рождения
    
    Returns:
        Словарь с данными человека
    """
    return {
        'id': str(uuid.uuid4()),
        'name': name,
        'born_in': born_in,
        'friends': []  # Список ID друзей
    }


def add_friend(person1: PersonData, person2: PersonData, 
               persons_dict: Dict[str, PersonData]) -> None:
    """
    Добавление взаимной дружбы между двумя людьми
    
    Args:
        person1: Данные первого человека
        person2: Данные второго человека
        persons_dict: Словарь всех людей по ID
    """
    if person2['id'] not in person1['friends']:
        person1['friends'].append(person2['id'])
        person2['friends'].append(person1['id'])


def serialize_functional(root_person: PersonData, 
                        persons_dict: Dict[str, PersonData]) -> bytes:
    """
    Функциональная сериализация графа объектов
    
    Args:
        root_person: Корневой объект для сериализации
        persons_dict: Словарь всех объектов по ID
    
    Returns:
        Байтовое представление в формате JSON
    """
    objects_to_save: List[PersonData] = []
    visited_ids: Set[str] = set()
    
    def collect_objects(person_id: str) -> None:
        """Рекурсивный сбор всех связанных объектов"""
        if person_id in visited_ids:
            return
        
        visited_ids.add(person_id)
        person = persons_dict[person_id]
        
        # Создаем копию с сериализуемыми данными
        obj_copy = person.copy()
        obj_copy['born_in'] = person['born_in'].isoformat()
        objects_to_save.append(obj_copy)
        
        # Рекурсивно обрабатываем друзей
        for friend_id in person['friends']:
            collect_objects(friend_id)
    
    collect_objects(root_person['id'])
    
    # Добавляем информацию о корневом объекте
    result = {
        'root_id': root_person['id'],
        'objects': objects_to_save
    }
    
    return json.dumps(result, indent=2).encode('utf-8')


def deserialize_functional(data: bytes, 
                          factory: PersonFactory) -> Tuple[PersonData, Dict[str, PersonData]]:
    """
    Функциональная десериализация графа объектов
    
    Args:
        data: Байтовое представление в формате JSON
        factory: Функция для создания объектов
    
    Returns:
        Кортеж: (корневой объект, словарь всех объектов)
    """
    parsed = json.loads(data.decode('utf-8'))
    root_id = parsed['root_id']
    
    # Восстановление объектов
    persons_dict: Dict[str, PersonData] = {}
    
    # Фаза 1: Создание объектов
    for obj_data in parsed['objects']:
        person = factory(obj_data['name'], 
                        dt.datetime.fromisoformat(obj_data['born_in']))
        person['id'] = obj_data['id']
        person['friends'] = obj_data['friends'].copy()  # Пока только ID
        persons_dict[person['id']] = person
    
    # Фаза 2: Замена ID на ссылки на объекты
    for person in persons_dict.values():
        # Создаем новый список с ссылками на объекты
        friend_objects = [persons_dict[friend_id] for friend_id in person['friends']]
        person['friends'] = friend_objects
    
    return persons_dict[root_id], persons_dict


# Вспомогательные функции
def create_person_with_friends(name: str, born_in: dt.datetime) -> PersonData:
    """Фабрика для создания структуры человека"""
    return create_person_data(name, born_in)


# Демонстрация работы
if __name__ == "__main__":
    print("=== Функциональный подход к сериализации ===")
    
    # Создание словаря для хранения всех людей
    all_persons: Dict[str, PersonData] = {}
    
    # Создание данных людей
    p1 = create_person_with_friends("Иван", dt.datetime(1990, 5, 15))
    p2 = create_person_with_friends("Мария", dt.datetime(1992, 8, 22))
    p3 = create_person_with_friends("Алексей", dt.datetime(1988, 3, 10))
    
    # Добавление в общий словарь
    all_persons[p1['id']] = p1
    all_persons[p2['id']] = p2
    all_persons[p3['id']] = p3
    
    # Создание связей
    add_friend(p1, p2, all_persons)
    add_friend(p2, p3, all_persons)
    add_friend(p3, p1, all_persons)  # Циклическая ссылка
    
    # Сериализация
    serialized_data = serialize_functional(p1, all_persons)
    
    print(f"Сериализованные данные ({len(serialized_data)} байт):")
    print(serialized_data[:200].decode('utf-8') + "...")
    
    # Десериализация
    def person_factory(name: str, birth_date: dt.datetime) -> PersonData:
        return create_person_with_friends(name, birth_date)
    
    restored_person, all_restored = deserialize_functional(serialized_data, person_factory)
    
    # Проверка
    print(f"\nВосстановленный объект:")
    print(f"Имя: {restored_person['name']}")
    print(f"Дата рождения: {restored_person['born_in']}")
    print(f"Количество друзей: {len(restored_person['friends'])}")
    
    if restored_person['friends']:
        print(f"Первый друг: {restored_person['friends'][0]['name']}")
        print(f"Проверка цикла: {restored_person['friends'][0]['friends'][1]['name']}")
    
    print(f"\nВсего восстановлено объектов: {len(all_restored)}")
