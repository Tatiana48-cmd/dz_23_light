import requests
import json
import logging
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_hh_vacancies(specialization, region, salary_from=None, salary_to=None, remote=False):
    try:
        params = {
            "text": f"{specialization}",
            "area": get_region_id(region),
            "per_page": 50,
            "page": 0
        }

        if salary_from or salary_to:
            params["salary"] = salary_from if salary_from else salary_to
            params["only_with_salary"] = True

        if remote:
            params["schedule"] = "remote"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        response = requests.get("https://api.hh.ru/vacancies", params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        vacancies = []

        for item in data.get('items', []):
            salary = format_salary(item.get('salary'))
            schedule_remote = item.get('schedule', {}).get('id') == 'remote'
            vacancies.append({
                'title': item.get('name'),
                'company': item.get('employer', {}).get('name'),
                'salary': salary,
                'link': item.get('alternate_url'),
                'region': region,  # Добавляем регион из параметров
                'is_remote': schedule_remote  # Извлекаем из API
            })

        return vacancies

    except Exception as e:
        logger.error(f"Ошибка парсера: {e}")
        return []

def get_region_id(region_name):
    regions = {
        'москва': 1,
        'санкт-петербург': 2,
        'россия': 113
    }
    return regions.get(region_name.lower(), 1)


def format_salary(salary):
    if not salary:
        return "Не указана"
    from_s = salary.get('from')
    to_s = salary.get('to')
    currency = salary.get('currency', '').upper()
    parts = []
    if from_s:
        parts.append(f"от {from_s}")
    if to_s:
        parts.append(f"до {to_s}")
    return ' - '.join(parts) + f" {currency}" if parts else "Не указана"


def save_results_to_file(vacancies, filename='data/results.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(vacancies, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")


def load_results_from_file(filename='data/results.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []