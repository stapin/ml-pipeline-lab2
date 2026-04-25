import os
import oracledb
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class OracleDBManager:
    def __init__(self):
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "1521")
        self.service = os.getenv("DB_SERVICE", "FREEPDB1")
        self.dsn = f"{self.host}:{self.port}/{self.service}"

    def _get_connection(self):
        """Создает и возвращает новое соединение с БД."""
        return oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn
        )

    def init_database(self):
        """Инициализирует структуру БД (создает таблицы, если их нет)."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Изменили тип id на NUMBER и добавили IDENTITY для автогенерации
                    cursor.execute("""
                        BEGIN
                           EXECUTE IMMEDIATE 'CREATE TABLE predictions (
                               id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                               text_content CLOB,
                               rating NUMBER
                           )';
                        EXCEPTION
                           WHEN OTHERS THEN
                              IF SQLCODE != -955 THEN RAISE; END IF;
                        END;
                    """)
                    conn.commit()
                except oracledb.DatabaseError as e:
                    print(f"Ошибка при инициализации базы данных: {e}")

    def save_prediction(self, text_content: str, predicted_rating: float) -> int:
        """
        Сохраняет результаты и возвращает сгенерированный базой ID.
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                # Создаем специальную переменную для получения сгенерированного id из Oracle
                out_id = cursor.var(oracledb.NUMBER)
                
                # В INSERT мы больше не передаем id. 
                # Конструкция RETURNING INTO позволяет сразу получить созданный id.
                cursor.execute("""
                    INSERT INTO predictions (text_content, rating)
                    VALUES (:1, :2)
                    RETURNING id INTO :3
                """, [text_content, predicted_rating, out_id])
                
                conn.commit()
                
                # out_id.getvalue() возвращает список значений, берем первое и приводим к int
                return int(out_id.getvalue()[0])