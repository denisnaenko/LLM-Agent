'''
Функция по персональным реком.
Основана на работе GPT с заданным заранее промтом.

Version: gpt-4o-mini

'''
import aiohttp

# Промт для гпт-чата
INSTRUCTION = '''
Ты — эксперт в области косметики. Пользователь ищет рекомендации по косметическим средствам на основе своего типа кожи, особенностей и возможных рисков. Учитывай, что пользователь уже знает свой тип кожи, поэтому он передаётся напрямую.

На основе переданных данных:
1. Подбери пять косметических марок, подходящих для указанного типа кожи.
2. Для каждой марки предложи:
   - 1 гель/пенку/умывалку.
   - 1 тоник или средство схожей структуры.
   - 1 крем или бальзам.
3. Укажи, для каких особенностей или рисков подходят средства.

Ответ должен быть в формате:

Вот рекомендации по косметическим маркам, которые могут вам подойти:

1. Марка 21 Название марки
   - Написать тип средства - Название - Краткое описание средства
   - Написать тип средства - Название - Краткое описание средства
   - Написать тип средства  - Название - Краткое описание средства
   - Для какого типа кожи или проблем подходит: Краткое описание для какого типа кожи или проблем подходит
   - Оценка пользователей - 5 звезд

2. Марка 2: Название марки
   - Написать тип средства - Название - Краткое описание средства
   - Написать тип средства - Название - Краткое описание средства
   - Написать тип средства  - Название - Краткое описание средства
   - Для какого типа кожи или проблем подходит: Краткое описание для какого типа кожи или проблем подходит
   - Оценка пользователей - 5 звезд

3. Марка 3: Название марки
   - Написать тип средства  - Название - Краткое описание средства
   - Написать тип средства  - Название - Краткое описание средства
   - Написать тип средства  - Название - Краткое описание средства
   - Для какого типа кожи или проблем подходит: Краткое описание для какого типа кожи или проблем подходит
   - Оценка пользователей - 5 звезд

4. Марка 4: Название марки
   - Написать тип средства - Название - Краткое описание средства
   - Написать тип средства - Название - Краткое описание средства
   - Написать тип средства  - Название - Краткое описание средства
   - Для какого типа кожи или проблем подходит: Краткое описание для какого типа кожи или проблем подходит
   - Оценка пользователей - 5 звезд

5. Марка 5: Название марки
   - Написать тип средства - Название - Краткое описание средства
   - Написать тип средства - Название - Краткое описание средства
   - Написать тип средства - Название - Краткое описание средства
   - Для какого типа кожи или проблем подходит: Краткое описание для какого типа кожи или проблем подходит
   - Оценка пользователей - 5 звезд
   
Обязательно учитывай только указанный тип кожи и особенности, переданные пользователем. Если есть риски, старайся подбирать гипоаллергенные или специализированные средства.
В конце обязательно должна быть приписка о консультации со специалистом.
'''

GPT_version = "gpt-4o-mini"
TOKENS_LIMIT = 4096

async def exception_handler(exception_code, api_key='', ex=''):
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"Code: {exception_code}, API Key: {api_key}, Exception: {ex}\n")

async def create_message(skin_type, features, risks):
    """
    Формирует сообщение для модели на основе данных пользователя.
    """

    features = ", ".join(features) or "нет особенностей"
    risks = ", ".join(risks) or "без рисков"

    user_context = (
        f"Тип кожи: {skin_type}.\n"
        f"Особенности: {features}.\n"
        f"Риски: {risks}.\n"
    )

    return [
        {"role": "user", "content": INSTRUCTION + "\n" + user_context}
    ]

async def get_result_message(skin_type, features, risks):
    message = await create_message(skin_type, features, risks)
    chat_response = ""

    for _ in range(1, 4):  # Ограничиваем количество попыток
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url="https://api.gpt4-all.xyz/v1/chat/completions",
                    json={
                        "model": GPT_version,
                        "messages": message,
                        "stream": False,
                    },
                    
                    headers={
                        "Authorization": f"Bearer g4a-EhTFKK7CwY19FZIr4JZvCsV1A8kJfklzjbe",
                        "Content-Type": "application/json",
                    }
                ) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        chat_response = response_json['choices'][0]['message']['content']
                        break
                    else:
                        await exception_handler(
                            exception_code="error3",
                            ex=f"HTTP {response.status}: {await response.text()}"
                        )
                        return "error3"

        except Exception as ex:
            await exception_handler(exception_code="error3", ex=ex)
            return "error3"

    chat_response = chat_response.replace("*", "").replace("#", "")
    return chat_response