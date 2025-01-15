import aiosqlite
from .ocr_processor import ocr_func
from .organize_text import get_organized_text

async def get_ingredients_str(text):
    """
    Разделяет текст на ингредиенты, удаляет скобки и их содержимое,
    заменяет ';' и ':' на ',', а затем разделяя по запятой.
    """
    if text is None:
        return []

    # Заменяем ';' и ':' на ',', чтобы упростить разбиение
    text = text.replace(';', ',').replace(':', ',').replace('  ',' ')
    return text

async def get_ingredient_id_and_name_accurate(db_name, ingredient_name, see_many_results=False):
    async with aiosqlite.connect(db_name) as conn:
        cursor = await conn.execute("""
        SELECT i.id, i.name,
            (SELECT synonym FROM synonyms WHERE synonym = ?) AS found_synonym
        FROM ingredients i
        WHERE i.name in (SELECT name FROM synonyms WHERE synonym = ?)
        """, (ingredient_name, ingredient_name))

        result = await cursor.fetchone()
        await cursor.close()
    
    if result: return result

    return None

async def get_ingredient_id_and_name_approximate(db_name, ingredient_name, see_many_results=False):
    async with aiosqlite.connect(db_name) as conn:        
        cursor = await conn.execute("""
        SELECT i.id, i.name,
            (SELECT synonym FROM synonyms WHERE synonym LIKE ?) AS found_synonym
        FROM ingredients i
        WHERE i.name in 
            (SELECT name FROM synonyms WHERE synonym LIKE ?)
        """, ('%' + ingredient_name + '%', '%' + ingredient_name + '%'))

        result = await cursor.fetchall()
        await cursor.close()

    if result:
        if not see_many_results: return result[0]
        else: return result
    
    return None

async def get_ingredient_id_and_name(db_name, ingredient_name, see_many_results=False):
    result = await get_ingredient_id_and_name_accurate(db_name, ingredient_name, see_many_results=see_many_results)
    if result: return result

    result = await get_ingredient_id_and_name_approximate(db_name, ingredient_name, see_many_results=see_many_results)
    if result: return result

    return None

async def get_ingredient_id_and_name_by_type(db_name, ingredient_name, see_many_results=False):
    component_types = ['extract', 'oil', 'powder', 'wax', 'filtrate']

    component_type_suffixs = ['', 'of', 'from', 'solution', 'distilled', 'unsaponifiables']
    component_type_prefixs = [
        '', 'leaf', 'seed', 'fruit', 'root', 'flower', 'peel',
        'germ', 'bran', 'nut', 'bark', 'stem', 'bud', 'kernel', 'wood',
        'flowers', 'roots', 'seeds', 'essential ', 'nuts', 'juice', 'oil', 'pulp']
    component_type_rare_prefixs = [
        'roots essential', 'flower essential', 'seeds essential', 'leaf essential',
        'leaf/stem', 'flower/leaf', 'flower/leaf/stem', 'leef cell', 'sprout',
        'flower cell', 'leef cell culture', 'stem bark', 'nut seed ', 'fruit/seed']

    for component_type in component_types:
        if component_type in ingredient_name:
            # вида ' leaf extract'
            if ' ' + component_type in ingredient_name:
                for component_type_prefix in component_type_prefixs:
                    suffix = component_type_prefix + ' ' + component_type
                    if not suffix in ingredient_name:
                        continue
                    new_ingredient_name = ingredient_name[:ingredient_name.index(suffix)]

                    result = await get_ingredient_id_and_name(db_name, new_ingredient_name, see_many_results)
                    if result:
                        return result

            # вида 'extract of '
            if component_type + ' ' in ingredient_name:
                for component_type_suffix in component_type_suffixs:
                    prefix = component_type + ' ' + component_type_suffix
                    if not prefix in ingredient_name:
                        continue
                    new_ingredient_name = ingredient_name[:ingredient_name.index(prefix)]

                    result = await get_ingredient_id_and_name(db_name, new_ingredient_name, see_many_results)
                    if result:
                        return result

            # вида ' leef cell culture extract'
            if ' ' + component_type in ingredient_name:
                for component_type_rare_prefix in component_type_rare_prefixs:
                    suffix = component_type_rare_prefix + ' ' + component_type
                    if not suffix in ingredient_name:
                        continue
                    new_ingredient_name = ingredient_name[:ingredient_name.index(suffix)]

                    result = await get_ingredient_id_and_name(db_name, new_ingredient_name, see_many_results)
                    if result:
                        return result

    return None

async def get_ingredient_id_and_name_by_removing_brackets(db_name, ingredient_name, see_many_results=False):
    new_ingredient_names = []
    if '(' in ingredient_name:
        open_index = ingredient_name.index('(')
        len_name = len(ingredient_name)
        if ')' in ingredient_name:
            close_index = ingredient_name.index(')')
            if not open_index == 0:  # ...(
                if not close_index == len_name - 1:  # ...(...)...
                    new_ingredient_names.append(ingredient_name[:open_index - 1] +
                                                ingredient_name[close_index + 1:])
                    new_ingredient_names.append(ingredient_name[:open_index - 1])
                    new_ingredient_names.append(ingredient_name[open_index + 1:close_index])
                else:  # ...(...)
                    new_ingredient_names.append(ingredient_name[:open_index - 1])
            else:  # (...
                if not close_index == len_name - 1:  # (...)...
                    new_ingredient_names.append(ingredient_name[close_index + 2:])
                else:  # (...)
                    new_ingredient_names.append(ingredient_name[open_index + 1:close_index])
        else:  # ...(...
            if not open_index == 0:  # ...(
                new_ingredient_names.append(ingredient_name[:open_index - 1])
            else:  # ...(...
                new_ingredient_names.append(ingredient_name[1:])
    elif ')' in ingredient_name:  # ...)...
        close_index = ingredient_name.index(')')
        len_name = len(ingredient_name)
        if not close_index == 0:  # ...)...
            new_ingredient_names.append(ingredient_name[:close_index])
        else:  # )...
            new_ingredient_names.append(ingredient_name[1:])

    for new_ingredient_name in sorted(new_ingredient_names, key=len, reverse=True):
        result = await get_ingredient_id_and_name_by_type(db_name, ingredient_name, see_many_results)
        if result:
            return result

        result = await get_ingredient_id_and_name(db_name, new_ingredient_name, see_many_results)
        if result:
            return result
    
    return None

async def get_ingredient_id_and_name_by_name(db_name, ingredient_name, see_many_results=False):
    ingredient_name = ingredient_name.lower().strip()

    result = await get_ingredient_id_and_name(db_name, ingredient_name, see_many_results=see_many_results)
    if result:
        return result

    result = await get_ingredient_id_and_name_by_type(db_name, ingredient_name, see_many_results=see_many_results)
    if result:
        return result

    if '(' in ingredient_name or ')' in ingredient_name:
        result = await get_ingredient_id_and_name_by_removing_brackets(db_name, ingredient_name,
                                                                 see_many_results=see_many_results)
        if result:
            return result
    
    return None

async def get_ingredient_info_by_id(db_name, ingredient_id):
    async with aiosqlite.connect(db_name) as conn:
        cursor = await conn.execute("""
        SELECT i.description, i.sources, i.effect, 
            i.role, i.danger, i.not_for_skin_type, i.for_skin_type
        FROM ingredients i
        WHERE i.id = ? """, (ingredient_id,))

        result = await cursor.fetchone()
        await cursor.close()
    
    if result: return result

    return None

async def get_ingredients_dict(db_name, ingredients_str, is_sepated=False):
    if is_sepated:
        if ', ' in ingredients:
            ingredients = ingredients_str.replace(', ', '; ')
        else:
            ingredients = ingredients_str.replace(',', ';')
        ingredients = ingredients_str.split(';')
        ingredients_dict = {i: [] for i in range(len(ingredients))}
        is_recognized = [False] * len(ingredients)
        for i, ingredient_name in enumerate(ingredients):
            result = await get_ingredient_id_and_name_by_name(db_name, ingredient_name)
            if result:
                ingredients_dict[i] = [ingredient_name] + list(result)
                is_recognized[i] = True
            else:
                is_recognized[i] = False

    else:
        ingredients = ingredients_str.replace(';', ' ').replace(', ', ' ').replace('.', ',').split()
        ingredients_dict = {i: [] for i in range(len(ingredients))}
        is_recognized = [False] * len(ingredients)
        start = 0
        if ('aqua' in ingredients[0].lower().strip()
                or 'water' in ingredients[0].lower().strip()
                or 'eau' in ingredients[0].lower().strip()):
            result = await get_ingredient_id_and_name_by_name(db_name,
                                                        'water',
                                                        see_many_results=True)
            ingredients_dict[0] = [ingredients[0]] + list(result)
            is_recognized[0] = True
            start = 1
        two_words_ingredients = []
        for i in range(start, len(ingredients) - 1):
            two_words_ingredients.append(ingredients[i] + " " + ingredients[i + 1])
        for i, two_words_ingredient in enumerate(two_words_ingredients):
            result = await get_ingredient_id_and_name_by_name(db_name,
                                                        two_words_ingredient.lower().strip(),
                                                        see_many_results=True)
            if result is None:
                pass
            elif isinstance(result, tuple):
                ingredients_dict[i] = [two_words_ingredient] + list(result)
                is_recognized[i] = True
                is_recognized[i + 1] = True
            else:
                if len(result) < 4:
                    ingredients_dict[i] = [two_words_ingredient] + list(result[0])
                    is_recognized[i] = True
                    is_recognized[i + 1] = True

        if sum([1 for i in is_recognized if not i]) > 3:
            for i, ingredient in enumerate(ingredients):
                if i >= start:
                    if not is_recognized[i]:
                        result = await get_ingredient_id_and_name_by_name(db_name,
                                                                    ingredient.lower().strip(),
                                                                    see_many_results=True)
                        if result is None:
                            pass
                        elif isinstance(result, tuple):
                            ingredients_dict[i] = [ingredient] + list(result)
                            is_recognized[i] = True
                        else:
                            if len(result) < 4:
                                ingredients_dict[i] = [ingredient] + list(result[0])
                                is_recognized[i] = True

        if sum([1 for i in is_recognized if not i]) > 3:
            three_words_ingredients = []
            for i in range(start, len(ingredients) - 2):
                three_words_ingredients.append(ingredients[i] + " " + ingredients[i + 1] + " " + ingredients[i + 2])
            for i, three_words_ingredient in enumerate(three_words_ingredients):
                result = await get_ingredient_id_and_name_by_name(db_name,
                                                            three_words_ingredient.lower().strip(),
                                                            see_many_results=True)
                if result is None:
                    pass
                elif isinstance(result, tuple):
                    ingredients_dict[i] = [three_words_ingredient] + list(result)
                    is_recognized[i] = True
                    is_recognized[i + 1] = True
                else:
                    if len(result) < 4:
                        ingredients_dict[i] = [three_words_ingredient] + list(result[0])
                        is_recognized[i] = True
                        is_recognized[i + 1] = True

        if sum([1 for i in is_recognized if not i]) > len(is_recognized) // 2:
            four_words_ingredients = []
            for i in range(start, len(ingredients) - 3):
                four_words_ingredients.append(
                    ingredients[i] + " " + ingredients[i + 1] + " " + ingredients[i + 2] + " " + ingredients[i + 3])
            for i, four_words_ingredient in enumerate(four_words_ingredients):
                result = await get_ingredient_id_and_name_by_name(db_name,
                                                            four_words_ingredient.lower().strip(),
                                                            see_many_results=True)
                if result is None:
                    pass
                elif isinstance(result, tuple):
                    ingredients_dict[i] = [four_words_ingredient] + list(result)
                    is_recognized[i] = True
                    is_recognized[i + 1] = True
                else:
                    if len(result) < 4:
                        ingredients_dict[i] = [four_words_ingredient] + list(result[0])
                        is_recognized[i] = True
                        is_recognized[i + 1] = True

        if sum([1 for i in is_recognized if not i]) > 0:
            for i, ingredient in enumerate(ingredients):
                if not is_recognized[i]:
                    ingredients_dict[i] = [ingredient]

    return ingredients, is_recognized, ingredients_dict

async def get_ingredients_info(db_name, ingredients, is_recognized, ingredients_dict):
    # ingredients список строк - список исходных ингредиентов
    # is_recognized список из True/False для каждого исходного ингредиента
    # ingredients_dict = {i: [ingredient, idx, name, found_by], ...}

    # уже поискали в базе и есть результаты
    # получаем непосредственно данные из базы, а не просто айди

    result_dict = dict()
    recognized_names = []
    for i in ingredients_dict.keys():
        value = ingredients_dict[i]
        if len(value) > 1:
            ingredient, idx, name, found_by = value
        else:
            ingredient = value
        if is_recognized[i]:
            if not name in recognized_names:
                ingredient_info = await get_ingredient_info_by_id(db_name, idx)
                result_dict[i] = [ingredients[i], ingredient, name, found_by] + list(ingredient_info)
                recognized_names.append(name)
            elif name:
                j = 0
                for j in result_dict.keys():
                    if len(result_dict[j]) > 2 and name == result_dict[j][2]:
                        result_dict[i] = [ingredients[i], f'Смотри ингредиент под номером {j}']
                        break
        else:
            result_dict[i] = [ingredients[i], is_recognized[i]]
    return result_dict

async def analyze_ingredients(text=None):
    db_name = "ingredients.db"

    if not text: 
        text = await ocr_func()

    ingredients_str = await get_ingredients_str(text)
    ingredients, is_recognized, ingredients_dict = await get_ingredients_dict(db_name,
                                                                        ingredients_str,
                                                                        is_sepated=False)

    not_recommended = []
    dangerous = []
    c = 0
    ingredients_info = await get_ingredients_info(db_name, ingredients, is_recognized, ingredients_dict)

    total_msg = ""
    for i in ingredients_info.keys():
        if ingredients_info[i][1]:
            if len(ingredients_info[i]) > 2:
                c += 1
                if ingredients_info[i][8] == '':
                    continue
                else:
                    if 'запрещен' in ingredients_info[i][8].lower():
                        dangerous.append(ingredients_info[i][2])

                        total_msg += f"Опасен: {ingredients_info[i]}\n\n"
                    else:
                        not_recommended.append(ingredients_info[i][2])
                        total_msg += f"Применять с осторожностью: {ingredients_info[i]}\n\n"


    if len(dangerous) >= 1:
        conclusion = "Ваше средство опасно для кожи!"
    elif len(not_recommended) >= 1:
        conclusion = "Ваше средство может иметь индивидуальные противопоказания!"
    else:
        conclusion = "Ваше средство безопасно!"

    total_msg = await get_organized_text(total_msg)
    
    return (
        f"Найдено опасных для кожи ингредиентов: {len(dangerous)}!\n"
        f"Ингредиенты которые стоит использовать с осторожностью: {len(not_recommended)}!\n\n"
        f"{conclusion}\n\n"
        f"Ознакомиться с характеристиками ингредиентов можно в файле ниже:"
    ), total_msg