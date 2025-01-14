import cv2
import numpy as np
from ultralytics import YOLO
import os
import asyncio

async def crop_object_async(image_path, 
                            class_to_crop="makeup-composition", 
                            output_dir="cropped_images", 
                            use_contour=False):
    """
    Асинхронная версия функции для обрезки объектов из изображения.
    """
    loop = asyncio.get_event_loop()

    # Асинхронный вызов для выполнения синхронной функции
    return await loop.run_in_executor(
        None,
        crop_object,
        image_path,
        class_to_crop,
        output_dir,
        use_contour
    )

def crop_object(image_path, 
                class_to_crop="makeup-composition", 
                output_dir="cropped_images", 
                use_contour=False):
    """
    Обрезает объекты из изображения на основе bounding box или контура, сохраняет обрезанные изображения
    и исходное изображение с bbox.

    Args:
        image_path (str): Путь к входному изображению.
        class_to_crop (str): Название класса объекта, который нужно обрезать.
        output_dir (str): Директория для сохранения обрезанных изображений.
        use_contour (bool): True для обрезки по контуру, False для обрезки по bounding box.

    Returns:
        str: Сообщение о результате обрезки.
    """
    # Создание директории для сохранения, если она не существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Загрузка модели YOLO
    model_path = r"models/trained_model.pt"
    model = YOLO(model_path)

    # Чтение изображения
    image = cv2.imread(image_path)
    if image is None:
        print(f"Ошибка: Не удалось загрузить изображение: {image_path}")
        return "Ошибка загрузки изображения."

    # Копия для рисования прямоугольников
    original_image_with_boxes = image.copy()

    # Запуск детекции
    results = model(image)

    cropped_image_paths = []
    object_count = 1

    # Проход по результатам детекции
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy().astype(int)
        confs = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        masks = result.masks  # Получаем маски, даже если обрезаем по bbox

        for i, (xyxy, conf, class_id) in enumerate(zip(boxes, confs, classes)):
            class_name = model.names[int(class_id)]

            # Проверка, соответствует ли класс нужному
            if class_name == class_to_crop:
                # Получаем координаты bounding box
                x_min, y_min, x_max, y_max = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])

                # Рисуем bounding box на оригинальном изображении
                cv2.rectangle(original_image_with_boxes, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                if use_contour:
                    # Обрезка по контуру
                    mask = masks[i].cpu().numpy().astype(np.uint8)
                    mask = cv2.resize(mask, (x_max - x_min, y_max - y_min), interpolation=cv2.INTER_NEAREST)

                    full_mask = np.zeros(image.shape[:2], dtype=np.uint8)
                    full_mask[y_min:y_max, x_min:x_max] = mask

                    contours, _ = cv2.findContours(full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if contours:
                        max_contour = max(contours, key=cv2.contourArea)
                        x, y, w, h = cv2.boundingRect(max_contour)
                        cropped_image = image[y:y + h, x:x + w].copy()
                else:
                    cropped_image = image[y_min:y_max, x_min:x_max].copy()

                # Сохранение обрезанного изображения
                output_path = os.path.join(output_dir, f"cropped_object_{object_count}.jpg")
                cv2.imwrite(output_path, cropped_image)
                cropped_image_paths.append(output_path)
                object_count += 1

    # Сохранение оригинального изображения с bbox
    original_output_path = os.path.join(output_dir, "original_image_with_boxes.jpg")
    cv2.imwrite(original_output_path, original_image_with_boxes)

    # Возврат результата
    if not cropped_image_paths:
        return False, (
            "❌ Не удалось распознать текст на фотографии.\n\n"
            "Возможно, текст слишком размытый, плохо освещённый или фотография сделана под углом. Попробуйте:\n\n"
            "• Сфотографируйте текст при хорошем освещении☀.\n\n"
            "• Убедитесь, что весь текст виден на фотографии📜.\n\n"
            "• Держите камеру прямо, чтобы избежать искажений🤳.\n\n"
        )
    
    return True, "✅ Фото успешно загружено! Приступаю к анализу...📝"
