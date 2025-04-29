import sqlite3
import json
from tabulate import tabulate

def clear_database(cursor):
    """Очищает все таблицы перед новым запросом."""
    cursor.execute("DELETE FROM salary_parser")
    cursor.execute("DELETE FROM vacancy_parser")
    cursor.execute("DELETE FROM company_parser")

def import_vacancies():
    conn = sqlite3.connect('vacancies.db')
    cursor = conn.cursor()

    # Очищаем старые данные
    clear_database(cursor)

    # Чтение данных из JSON (последний запрос)
    with open('results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Заполнение таблиц новыми данными
    for item in data:
        # Компания
        cursor.execute(
            "INSERT OR IGNORE INTO company_parser (name) VALUES (?)",
            (item['company'],)
        )
        cursor.execute(
            "SELECT id FROM company_parser WHERE name = ?",
            (item['company'],)
        )
        company_id = cursor.fetchone()[0]

        # Вакансия
        cursor.execute(
            "INSERT INTO vacancy_parser (title, company_id, link) VALUES (?, ?, ?)",
            (item['title'], company_id, item['link'])
        )
        vacancy_id = cursor.lastrowid

        # Зарплата
        cursor.execute(
            "INSERT INTO salary_parser (salary, vacancy_id) VALUES (?, ?)",
            (item['salary'], vacancy_id)
        )

    conn.commit()

    # Вывод результатов
    cursor.execute('''
        SELECT v.title, c.name, s.salary
        FROM vacancy_parser v
        JOIN company_parser c ON v.company_id = c.id
        JOIN salary_parser s ON v.id = s.vacancy_id
    ''')
    print(tabulate(cursor.fetchall(),
                   headers=["Вакансия", "Компания", "Зарплата"],
                   tablefmt="grid"))

    conn.close()

if __name__ == "__main__":
    import_vacancies()