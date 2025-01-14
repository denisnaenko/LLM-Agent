import easyocr
import asyncio
import os
import glob

async def ocr_func():
    """
    Выполняет OCR-анализ изображения.

    Returns:
        str: Распознанный текст из изображения.
    """

    image_path="cropped_images/cropped_object_1.jpg"
    folder_path="cropped_images"

    reader = easyocr.Reader(['en', 'ru'], gpu=False)  # Используем ['ru', 'en'] для русского и английского
    loop = asyncio.get_event_loop()

    try:
        # Выполняем OCR
        results = await loop.run_in_executor(None, reader.readtext, image_path)
        text = " ".join([result[1] for result in results])  # Собираем текст из результатов
        return text
    finally:
        # Удаляем все файлы из указанной папки
        files = glob.glob(os.path.join(folder_path, '*'))
        for file in files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Не удалось удалить файл {file}: {e}")
