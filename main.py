from flask import Flask, render_template, request, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth  import HTTPBasicAuth

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
auth = HTTPBasicAuth()
db = SQLAlchemy(app)
users = {
    "admin": "12345"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username


class SurveyResult(db.Model):
    __tablename__ = "survey_results"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(100))
    favorite_time = db.Column(db.String(100))
    favorite_genres = db.Column(db.Text)
    favorite_actor = db.Column(db.String(100))
    favorite_game = db.Column(db.String(100))


with app.app_context():
    db.create_all()

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

        result = SurveyResult(
            number=number,
            favorite_time=favorite_time,
            favorite_genres=favorite_genres_str,
            favorite_actor=favorite_actor,
            favorite_game=favorite_game
        )

        db.session.add(result)
        db.session.commit()




        return render_template('thankyou.html')
    return render_template('survey.html', username=number)

@app.route('/results')
@auth.login_required
def results():
    date = SurveyResult.query.all()
    return render_template('results.html', data=date)


if __name__ == '__main__':

    app.run(debug=True, port=5001)