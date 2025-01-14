async def is_valid_ingredients_text(text):
    """
    Асинхронно проверяет корректность введенного текста состава.
    """

    # Проверка минимальной длины текста
    if len(text) < 10:
        return False, "⚠️ Текст слишком короткий. Убедитесь, что указали полный состав."

    # Преобразуем текст для анализа
    text_normalized = text.lower().replace("  ", " ")

    # Проверка наличия популярных ингредиентов
    popular_ingredients = ["aqua", "alcohol"]
    found_popular = [ingredient for ingredient in popular_ingredients if ingredient in text_normalized]
    if not found_popular:
        return False, (
            "⚠️ Не удалось обнаружить в составе ключевых ингредиентов для ухода за кожей "
            "(например, Aqua, Alcohol). Проверьте текст."
        )

    return True, "Текст состава выглядит корректным."
