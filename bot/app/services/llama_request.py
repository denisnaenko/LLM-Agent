import requests
import json

def query_llm(prompt):
    """
    Отправляет запрос в локальный API Ollama и возвращает ответ модели построчно.
    """
    url = "http://localhost:11434/api/generate"
    payload = {"model": "llama3.2", "prompt": prompt}
    headers = {"Content-Type": "application/json"}
    
    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()

            # Читаем данные построчно
            result = ""
            for line in response.iter_lines():
                if line:    # Игнорируем пустые строки
                    data = json.loads(line)
                    result += data.get("response", "")
            return result
        
    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {e}"
    except json.JSONDecodeError as e:
        return f"Ошибка декодирования JSON: {e}"