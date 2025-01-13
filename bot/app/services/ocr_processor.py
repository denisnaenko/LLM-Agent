import easyocr

def ocr_func():
    image_path = r"cropped_images\cropped_object_1.jpg"
    reader = easyocr.Reader(['en'])  # Используйте ['ru','en'] для русского и английского
    results = reader.readtext(image_path)
    text = " ".join([result[1] for result in results])  # Собираем текст из разных областей
    return text
