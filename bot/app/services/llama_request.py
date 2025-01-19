import requests
import json
import httpx

async def query_llm(prompt):
    """
    Асинхронно отправляет запрос в локальный API Ollama и возвращает ответ модели построчно.
    """
    url = "http://localhost:11434/api/generate"
    payload = {"model": "llama3.2", "prompt": prompt}
    headers = {"Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()

                # Читаем данные построчно
                result = ""
                async for line in response.aiter_lines():
                    if line:    # Игнорируем пустые строки
                        data = json.loads(line)
                        result += data.get("response", "")
                return result
        
        except httpx.RequestError as e:
            return f"Ошибка запроса: {e}"
        except json.JSONDecodeError as e:
            return f"Ошибка декодирования JSON: {e}"