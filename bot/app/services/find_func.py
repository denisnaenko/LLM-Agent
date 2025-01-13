import sqlite3
import re

from ocr_processor import ocr_func

def get_ingredients_list(text):
    """
    Разделяет текст на ингредиенты, удаляет скобки и их содержимое,
    заменяет ';' и ':' на ',', а затем разделяя по запятой.
    """
    if text is None:
        return []
    print(text)
    # Удаляем все, что находится в круглых скобках, включая скобки
    text = re.sub(r'\([^)]*\)', '', text)

    # Заменяем ';' и ':' на ',', чтобы упростить разбиение
    text = text.replace(';', ',').replace(':', ',').replace('  ',' ')

    # Разделяем текст по запятой, получаем список ингредиентов и убираем лишние пробелы
    ingredients = [ingredient.strip() for ingredient in text.split(',')]
    ingredients = [ingredient for ingredient in ingredients if ingredient]
    return ingredients



def get_ingredient_info_by_name(ingredient_name, db_name):
    """
    Ищет ингредиент в базе данных по имени (точное и примерное совпадение).
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # точное совпадение
    cursor.execute("""
    SELECT i.name, i.description, i.sources, i.effect, 
           i.role, i.danger, i.not_for_skin_type, i.for_skin_type
    FROM ingredients i
    WHERE i.name ==
        (SELECT name FROM synonyms WHERE synonym = ?)
    GROUP BY i.name
    """, (ingredient_name,))

    result = cursor.fetchone()
    if result:
        conn.close()
        return result

    # примерное совпадение, если точного нет
    cursor.execute("""
    SELECT i.name, i.description, i.sources, i.effect, 
           i.role, i.danger, i.not_for_skin_type, i.for_skin_type
    FROM ingredients i
    WHERE i.name ==
        (SELECT name FROM synonyms WHERE synonym LIKE ?)
    GROUP BY i.name
    """, ('%' + ingredient_name + '%',))

    result = cursor.fetchone()
    conn.close()
    return result


def process_ingredients(ingredients_list, db_name):
    """
    Ищет каждый ингредиент из списка в базе данных и подсчитывает найденные.
    """
    found_count = 0
    dangerous_count = 0
    not_recommended_count= 0
    for ingredient in ingredients_list:
        ingredient = ingredient.lower().strip()  # приводим к нижнему регистру и убираем пробелы
        print(f"Проверка ингредиента: {ingredient}")
        ingredient_info = get_ingredient_info_by_name(ingredient, db_name)
        if ingredient_info:
            print(f"  -> Найден: {ingredient_info[0]}")
            found_count += 1
            if ingredient_info[5] == '':
                continue
            else:
                if ingredient_info[5].startswith('Запрещен'):
                    dangerous_count += 1
                else:
                    not_recommended_count += 1
        else:
            print(f"  -> Ингредиент не найден: {ingredient}")
    return found_count, dangerous_count, not_recommended_count


def analyze_ingredients(db_name):
    """
    Получает список ингредиентов, анализирует их опасность и выводит результаты.
    """
    ingredients_list = get_ingredients_list(ocr_func())
    found_ingredients_count = process_ingredients(ingredients_list, db_name)

    print(f'''\nНайдено ингредиентов: {found_ingredients_count[0]} из {len(ingredients_list)}
Опасных: {found_ingredients_count[1]}\nНерекомендуемых: {found_ingredients_count[2]}''')

    if found_ingredients_count[1] > 1:
        print("Средство опасно!")
    elif found_ingredients_count[2] > 1:
        print("Средство может иметь индивидуальные противопоказания!")
    else:
        print("Средство безопасно!")


if __name__ == '__main__':
    db_name = 'db212.db'
    analyze_ingredients(db_name)

