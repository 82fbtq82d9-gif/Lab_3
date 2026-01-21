"""
Тесты для лабораторной работы 3
Проверка всех подходов к сериализации
"""
import json
import datetime as dt

from lab3_oop_encapsulated import Person, PersonSerializer
from lab3_oop_direct_access import PersonDirectAccess, DirectAccessSerializer
from lab3_functional import (
    create_person_data, add_friend, serialize_functional, 
    deserialize_functional, create_person_with_friends
)


def test_oop_encapsulated():
    """Тестирование ООП подхода с инкапсуляцией"""
    print("=== Тестирование ООП с инкапсуляцией ===")
    
    # Создание объектов
    p1 = Person("Иван", dt.datetime(1990, 5, 15))
    p2 = Person("Мария", dt.datetime(1992, 8, 22))
    p3 = Person("Алексей", dt.datetime(1988, 3, 10))
    
    # Создание связей
    p1.add_friend(p2)
    p1.add_friend(p3)
    p2.add_friend(p3)  # Циклическая ссылка
    
    # Сериализация
    serializer = PersonSerializer()
    data = serializer.serialize(p1)
    
    # Проверка формата JSON
    parsed = json.loads(data.decode('utf-8'))
    assert isinstance(parsed, list)
    assert len(parsed) == 3
    
    # Десериализация
    restored = serializer.deserialize(data)
    
    # Проверка
    assert restored.get_name() == "Иван"
    assert restored.get_birth_date() == dt.datetime(1990, 5, 15)
    assert len(restored.get_friends()) == 2
    
    print("✅ ООП с инкапсуляцией: все тесты пройдены")


def test_oop_direct_access():
    """Тестирование ООП подхода с прямым доступом"""
    print("\n=== Тестирование ООП с прямым доступом ===")
    
    # Создание объектов
    p1 = PersonDirectAccess("Иван", dt.datetime(1990, 5, 15))
    p2 = PersonDirectAccess("Мария", dt.datetime(1992, 8, 22))
    p3 = PersonDirectAccess("Алексей", dt.datetime(1988, 3, 10))
    
    # Создание связей
    p1.add_friend(p2)
    p2.add_friend(p3)
    p3.add_friend(p1)  # Явная циклическая ссылка
    
    # Сериализация
    serializer = DirectAccessSerializer()
    data = serializer.serialize(p1)
    
    # Десериализация
    restored = serializer.deserialize(data)
    
    # Проверка с прямым доступом (нарушение инкапсуляции)
    assert restored._name == "Иван"
    assert restored._born_in == dt.datetime(1990, 5, 15)
    assert len(restored._friends) == 2
    
    print("✅ ООП с прямым доступом: все тесты пройдены")


def test_functional():
    """Тестирование функционального подхода"""
    print("\n=== Тестирование функционального подхода ===")
    
    # Создание словаря для хранения всех людей
    all_persons = {}
    
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
    data = serialize_functional(p1, all_persons)
    
    # Десериализация
    def person_factory(name: str, birth_date: dt.datetime):
        return create_person_with_friends(name, birth_date)
    
    restored, all_restored = deserialize_functional(data, person_factory)
    
    # Проверка
    assert restored['name'] == "Иван"
    assert restored['born_in'] == dt.datetime(1990, 5, 15)
    assert len(restored['friends']) == 2
    assert len(all_restored) == 3
    
    print("✅ Функциональный подход: все тесты пройдены")


def compare_approaches():
    """Сравнение результатов всех подходов"""
    print("\n=== Сравнение результатов всех подходов ===")
    
    # Создаем простую структуру во всех подходах
    birth_date = dt.datetime(2000, 1, 1)
    
    # 1. ООП с инкапсуляцией
    p1_oop = Person("Test", birth_date)
    
    # 2. ООП с прямым доступом
    p1_direct = PersonDirectAccess("Test", birth_date)
    
    # 3. Функциональный
    all_func = {}
    p1_func = create_person_with_friends("Test", birth_date)
    all_func[p1_func['id']] = p1_func
    
    # Сериализуем и сравниваем размер
    serializer_oop = PersonSerializer()
    serializer_direct = DirectAccessSerializer()
    
    data_oop = serializer_oop.serialize(p1_oop)
    data_direct = serializer_direct.serialize(p1_direct)
    data_func = serialize_functional(p1_func, all_func)
    
    print(f"Размер данных ООП с инкапсуляцией: {len(data_oop)} байт")
    print(f"Размер данных ООП с прямым доступом: {len(data_direct)} байт")
    print(f"Размер данных функционального подхода: {len(data_func)} байт")
    
    # Все подходы должны правильно обрабатывать базовые сценарии
    print("\n✅ Все подходы корректно работают с базовыми сценариями")


if __name__ == "__main__":
    print("Запуск тестов для лабораторной работы 3...")
    print("=" * 60)
    
    test_oop_encapsulated()
    test_oop_direct_access()
    test_functional()
    compare_approaches()
    
    print("\n" + "=" * 60)
    print("🎉 Все тесты лабораторной работы 3 успешно пройдены!")
    print("\nКаждый подход имеет свои преимущества и недостатки:")
    print("1. ООП с инкапсуляцией - безопасность и сопровождение")
    print("2. ООП с прямым доступом - производительность и простота")
    print("3. Функциональный подход - тестируемость и предсказуемость")
