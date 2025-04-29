from flask import Flask, render_template, request, redirect, url_for, flash
from parser_hh import parse_hh_vacancies, save_results_to_file, load_results_from_file
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        try:
            specialization = request.form['specialization']
            region = request.form['region']
            salary_from = request.form.get('salary_from')
            salary_to = request.form.get('salary_to')
            remote = 'remote' in request.form

            vacancies = parse_hh_vacancies(
                specialization=specialization,
                region=region,
                salary_from=salary_from,
                salary_to=salary_to,
                remote=remote
            )

            save_results_to_file(vacancies)

            if vacancies:
                flash(f"Найдено {len(vacancies)} вакансий", 'success')
            else:
                flash("Вакансий не найдено. Попробуйте изменить параметры поиска", 'warning')

            return redirect(url_for('results'))

        except Exception as e:
            flash(f"Ошибка при поиске: {str(e)}", 'error')
            return redirect(url_for('form'))

    return render_template('form.html')


@app.route('/results')
def results():
    vacancies = load_results_from_file()
    return render_template('results.html', vacancies=vacancies)


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)