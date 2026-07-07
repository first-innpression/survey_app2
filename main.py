from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask_httpauth  import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()
users = {
    "admin": "12345"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS survey_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            favorite_time TEXT,
            favorite_genres TEXT,
            favorite_actor TEXT,
            favorite_game TEXT
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/submit', methods=['POST'])
def submit():
    number = request.form.get('number')
    if not number:
        return render_template('home.html', error="Пожалуйста, введите свой номер")
    if len(number) < 7:
        return render_template('home.html', error="Пожалуйста, введите корректный номер")
    for digit in number:
        if not digit.isdigit():
            return render_template('home.html', error="Пожалуйста, введите корректный номер")
    return redirect(url_for('survey', number=number))

@app.route('/survey', methods=['GET', 'POST'])

def survey():
    number = request.args.get('number')
    if request.method == 'POST':
        favorite_time = request.form.get("favorite_time")
        favorite_genres = request.form.getlist("favorite_genres")
        favorite_actor= request.form.get("favorite_actor")
        favorite_game = request.form.get("favorite_game")
        favorite_genres_str = ', '.join(favorite_genres)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO survey_results
            (username, favorite_time, favorite_genres, favorite_actor, favorite_game)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            number,favorite_time,favorite_genres_str,favorite_actor,favorite_game
        ))

        conn.commit()
        conn.close()





        return render_template('thankyou.html')
    return render_template('survey.html', username=number)

@app.route('/results')
@auth.login_required
def results():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM survey_results")
    data = cursor.fetchall()

    conn.close()

    return render_template('results.html', data=data)
init_db()
if __name__ == '__main__':

    app.run(debug=True, port=5001)