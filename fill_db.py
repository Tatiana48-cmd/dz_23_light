import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Region, Vacancy
import re

def extract_salary(salary_str):
    """Извлекает числовые значения из строки зарплаты."""
    if not salary_str or salary_str == "Не указана":
        return None, None

    # Пример строки: "от 800 - до 1400 EUR" -> (800, 1400)
    from_match = re.search(r'от (\d+)', salary_str)
    to_match = re.search(r'до (\d+)', salary_str)

    salary_from = int(from_match.group(1)) if from_match else None
    salary_to = int(to_match.group(1)) if to_match else None

    return salary_from, salary_to

# Загрузка данных
try:
    with open('data/results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Данные из results.json успешно загружены. Всего вакансий: {len(data)}")
except Exception as e:
    print(f"Ошибка при загрузке файла results.json: {e}")
    exit()

# Подключение к БД
engine = create_engine('sqlite:///vacancies.db')
Session = sessionmaker(bind=engine)
session = Session()

# Добавление регионов (уникальные значения)
regions = {vacancy['region'] for vacancy in data if 'region' in vacancy}
print(f"Найдены регионы для добавления: {regions}")

for region_name in regions:
    if not session.query(Region).filter_by(name=region_name).first():
        session.add(Region(name=region_name))
        print(f"Добавлен регион: {region_name}")
    else:
        print(f"Регион уже существует: {region_name}")

session.commit()

# Добавление вакансий
added_count = 0
for vacancy in data:
    try:
        if 'title' not in vacancy or 'region' not in vacancy:
            print(f"Пропущена вакансия из-за отсутствия обязательных полей: {vacancy}")
            continue

        region = session.query(Region).filter_by(name=vacancy['region']).first()
        if not region:
            print(f"Регион '{vacancy['region']}' не найден в БД. Пропуск вакансии.")
            continue

        salary_from, salary_to = extract_salary(vacancy.get('salary'))
        is_remote = vacancy.get('is_remote', False)

        new_vacancy = Vacancy(
            title=vacancy['title'],
            salary_from=salary_from,
            salary_to=salary_to,
            is_remote=is_remote,
            region_id=region.id
        )
        session.add(new_vacancy)
        added_count += 1
        print(f"Добавлена вакансия: {vacancy['title']}")
    except Exception as e:
        print(f"Ошибка при добавлении вакансии {vacancy.get('title')}: {e}")

session.commit()
print(f"Данные успешно добавлены в БД. Добавлено вакансий: {added_count}/{len(data)}")