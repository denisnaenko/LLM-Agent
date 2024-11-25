from typing import List, Literal
from langchain_core.tools import tool

def scan_photo(edit_prompt: bool = False) -> List[str]:
    """Сканировать фото для считывания ингредиентов для ухода за кожей. При необходимости предложить пользователю редактировать считанные ингредиенты."""
    ingredients = ["глицерин", "гиалуроновая кислота", "масло ши"]

    if edit_prompt:
        print("Считанный состав: ", ingredients)
        user_input = input("Хотите отредактировать список (да/нет)? ")
        if user_input.lower() == "да":
            edited_ingredients = input("Введите отредактированный состав: ").split(", ")
            return edited_ingredients

    return ingredients

def write_substances(ingredients: List[str] = []) -> List[str]:
    """Ввести ингредиенты вручную для ухода за кожей."""
    if not ingredients:
        ingredients = input("Введите список ингредиентов, разделённых запятыми: ").split(", ")
    return ingredients

@tool
def input_substances(input_option: str = "photo_scan", edit_prompt: bool = False) -> List[str]:
    """
    Метод для выбора ввода ингредиентов ухода за кожей.
    Если input_option = 'photo_scan', используются ингредиенты со сканирования.
    Если input_option = 'write_substances', используется ручной ввод.
    """

    if input_option == "photo_scan":
        ingredients = scan_photo(edit_prompt=edit_prompt)

        # Проверка на редактирование списка после сканирования
        if edit_prompt:
            print("Считанный состав: ", ingredients)
            user_input = input("Хотите отредактировать список (да/нет)? ")
            if user_input.lower() == "да":
                ingredients = write_substances(ingredients=ingredients)

    elif input_option == "write_substances":
        ingredients = write_substances()

    return ingredients


@tool
def describe_ingredients(ingredients: List[str]) -> dict:
    """Вернуть описания предоставленных ингредиентов для ухода за кожей."""
    ingredient_descriptions = {
        "глицерин": "Глицерин увлажняет и смягчает кожу.",
        "гиалуроновая кислота": "Гиалуроновая кислота помогает удерживать влагу.",
        "масло ши": "Масло ши питает и защищает кожу."
    }
    descriptions = {ingredient: ingredient_descriptions.get(ingredient, "Нет описания.")
                    for ingredient in ingredients}
    return descriptions


@tool
def recommend_product(skin_type: Literal["сухая", "жирная", "нормальная", "чувствительная"]) -> str:
    """Предоставить рекомендацию по продукту для ухода за кожей в зависимости от типа кожи пользователя."""
    recommendations = {
        "сухая": "Увлажняющий крем с гиалуроновой кислотой для удержания влаги.",
        "жирная": "Легкий гель-крем для контроля блеска и увлажнения.",
        "нормальная": "Универсальный увлажнитель для поддержания баланса кожи.",
        "чувствительная": "Успокаивающий крем с минимальным количеством ингредиентов."
    }
    return recommendations.get(skin_type, "Нет рекомендаций для этого типа кожи.")


@tool
def determine_skin_type() -> str:
    """Определить тип кожи пользователя на основе ввода или смоделированной анкеты."""
    skin_types = ["сухая", "жирная", "нормальная", "чувствительная"]
    return skin_types[0]  # По умолчанию "сухая" для этого примера; замените на фактическую логику


def get_tools():
    tools = [scan_photo, describe_ingredients, recommend_product, determine_skin_type]
    return tools