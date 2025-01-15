'''
Функция для оформления вывода сообщения по составу ингредиента.
Основана на работе GPT с заданным заранее промтом.

Version: gpt-4o-mini
'''

import aiohttp

# Промт для гпт-чата
INSTRUCTION = '''
На основе предоставленных данных выведи структурированную информацию в удобном для чтения формате. Раздели текст на блоки с заголовками и подзаголовками. Используй списки, чтобы выделить ключевые моменты, и четко разделяй разделы. Пример вывода для каждого элемента должен быть следующим:

Название: [Название ингредиента]

Синонимы:
 • [Синоним 1]
 • [Синоним 2]

Описание:
[Описание ингредиента]

Ссылки:
 • [Ссылка 1]
 • [Ссылка 2]

Действие:
 • [Эффект 1]
 • [Эффект 2]

Применение:
 • [Применение 1]
 • [Применение 2]

Предостережения:
 • [Предостережение 1]
 • [Предостережение 2]

Отформатируй вывод так, чтобы он был визуально приятным и легко читался.”
'''

GPT_version = "gpt-4o-mini"
TOKENS_LIMIT = 4096

async def exception_handler(exception_code, api_key='', ex=''):
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"Code: {exception_code}, API Key: {api_key}, Exception: {ex}\n")

async def create_message(text):
    """
    Формирует сообщение для модели на основе данных пользователя.
    """
    
    return [
        {"role": "user", "content": INSTRUCTION + "\n" + text}
    ]

async def get_organized_text(text):
    message = await create_message(text)
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
                        "Authorization": f"Bearer g4a-ewhuBdIZH5grJIcE4gA9UusWSFELslIqJTL",
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
