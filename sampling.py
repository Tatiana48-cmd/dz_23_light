from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Vacancy, Region

engine = create_engine('sqlite:///vacancies.db')
Session = sessionmaker(bind=engine)
session = Session()

# Поиск вакансий в Калужской области с зарплатой от 100000
vacancies = session.query(Vacancy).join(Region).filter(
    Region.name == 'Калужская область',
    Vacancy.salary_from >= 100000
).all()

for vacancy in vacancies:
    print(f"{vacancy.title} (Зарплата: {vacancy.salary_from}-{vacancy.salary_to})")
    print(f"Удалённо: {'Да' if vacancy.is_remote else 'Нет'}\n")