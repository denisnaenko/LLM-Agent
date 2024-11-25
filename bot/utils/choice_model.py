from sentence_transformers import util
from load_select_model import load_select_model

# Загрузка модели
model = load_select_model()

# Определение команд и их описаний
commands = {
    "scan_photo": "Отсканировать фото, картинку, фтографию состав продукта для получения ингредиентов в составе. Принимает `photo`.",
    "get_description_substances": "Расписать, сказать, рассказать, описание о содержании и составе, свойства вещества, входящего в состав продукта. Принимает `list_substances`.",
    "recomendation": "Подсказать, что лучше подойдёт плюсы и минусы вещества в составе продукта, которые помогут с моим типом кожи. Дать рекомендации. Принимает `name_skin_type`.",
    "find_skin_type": "Вызвать готовый опрос на определение типа кожи. Вызывает `survey`."
}

def select_command(query, model, commands):
    """Выбирает подходящую команду на основе запроса."""
    # Кодируем запрос и описания команд
    query_embedding = model.encode(query)
    command_embeddings = {cmd: model.encode(desc) for cmd, desc in commands.items()}

    # Вычисляем косинусное сходство между запросом и каждой командой
    similarities = {cmd: util.cos_sim(query_embedding, emb).item() for cmd, emb in command_embeddings.items()}

    # Находим команду с максимальным сходством
    best_command = max(similarities, key=similarities.get)

    return best_command, similarities[best_command]


"""Пример использования функции выбора команды."""
query = input("Введите запрос: ")
command, similarity_score = select_command(query, model, commands)
print(f"Выбранная команда: {command} (сходство: {similarity_score:.2f})")
