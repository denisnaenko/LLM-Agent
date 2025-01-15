import sqlite3

DB_PATH = "db.sqlite3"

def get_user_data(tg_id):
    """
    Извлекает данные о коже пользователя из БД по tg_id.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверка наличия пользователя в БД
        query = """
        SELECT skin_type, features, risks FROM users WHERE tg_id = ?
        """
        cursor.execute(query, (tg_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            skin_type, features, risks = result

            # Преобразуем данные
            features = features.split(", ") if features else []
            risks = risks.split(", ") if risks else []

            return skin_type, features, risks
        else:
            return None, None, None
    except sqlite3.Error as e:
        print(f"Ошибка базы данны: {e}")
        return None