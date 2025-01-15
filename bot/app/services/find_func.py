import aiosqlite
import re

from .ocr_processor import ocr_func

async def get_ingredients_list(text):
    """
    Разделяет текст на ингредиенты, удаляет скобки и их содержимое,
    заменяет ';' и ':' на ',', а затем разделяет по запятой.
    """
    if text is None: return []

    # Удаляем все, что находится в круглых скобках, включая скобки
    text = re.sub(r'\([^)]*\)', '', text)

    # Заменяем ';' и ':' на ',', чтобы упростить разбиение
    text = text.replace(';', ',').replace(':', ',').replace('  ', ' ')

    # Разделяем текст по запятой, получаем список ингредиентов и убираем лишние пробелы
    ingredients = [ingredient.strip() for ingredient in text.split(',')]
    ingredients = [ingredient for ingredient in ingredients if ingredient]
    return ingredients


async def get_ingredient_info_by_name(ingredient_name, db_name):
    """
    Ищет ингредиент в базе данных по имени (точное и примерное совпадение).
    """
    async with aiosqlite.connect(db_name) as conn:
        cursor = await conn.cursor()

        # точное совпадение
        await cursor.execute("""
        SELECT i.name, i.description, i.sources, i.effect, 
               i.role, i.danger, i.not_for_skin_type, i.for_skin_type
        FROM ingredients i
        WHERE i.name ==
            (SELECT name FROM synonyms WHERE synonym = ?)
        GROUP BY i.name
        """, (ingredient_name,))
        result = await cursor.fetchone()
        if result:
            return result

        # примерное совпадение, если точного нет
        await cursor.execute("""
        SELECT i.name, i.description, i.sources, i.effect, 
               i.role, i.danger, i.not_for_skin_type, i.for_skin_type
        FROM ingredients i
        WHERE i.name ==
            (SELECT name FROM synonyms WHERE synonym LIKE ?)
        GROUP BY i.name
        """, ('%' + ingredient_name + '%',))
        result = await cursor.fetchone()
        return result


async def process_ingredients(ingredients_list, db_name):
    """
    Ищет каждый ингредиент из списка в базе данных и подсчитывает найденные.
    """
    found_count = 0
    dangerous_count = 0
    not_recommended_count = 0
    
    for ingredient in ingredients_list:
        ingredient = ingredient.lower().strip()  # приводим к нижнему регистру и убираем пробелы
        ingredient_info = await get_ingredient_info_by_name(ingredient, db_name)
        if ingredient_info:
            found_count += 1
            if ingredient_info[5] == '':
                continue
            else:
                if ingredient_info[5].startswith('Запрещен'):
                    dangerous_count += 1
                else:
                    not_recommended_count += 1

    return found_count, dangerous_count, not_recommended_count


async def analyze_ingredients(text=None):
    """
    Получает список ингредиентов, анализирует их опасность и выводит результаты.
    """

    if not text:
        text = await ocr_func()
    
    ingredients_list = await get_ingredients_list(text)
    found_ingredients_count = await process_ingredients(ingredients_list, db_name="ingredients.db")

    if found_ingredients_count[1] > 1:
        conclusion = "Ваше средство опасно для кожи!"
    elif found_ingredients_count[2] > 1:
        conclusion = "Ваше средство может иметь индивидуальные противопоказания!"
    else:
        conclusion = "Ваше средство безопасно!"

    return (
        f"Найдено {found_ingredients_count[1]} опасных для кожи ингредиентов!\n"
        f"Также найдено {found_ingredients_count[2]} нерекомендуемых ингредиентов.\n\n"
        f"{conclusion}"
    )
