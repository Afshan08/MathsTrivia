from datetime import datetime
import time
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, login_required, LoginManager, current_user, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql.expression import func
from score import GameManager
import plotly.express as px
from plotly.offline import plot
from collections import defaultdict


app = Flask(__name__)
app.config['SECRET_KEY'] = 'any-seceret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maths_game.db'
db = SQLAlchemy(app)
game_manager = GameManager()
login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_name = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(252))
    password = db.Column(db.String(100))


class Questions(db.Model):
    __tablename__ = 'Arthematics_Questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(252))
    answer = db.Column(db.Integer)


class UserData(db.Model):
    __tablename__ = "user_information"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("Arthematics_Questions.id"), nullable=False)
    user_answer = db.Column(db.String(50), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())

    user = db.relationship('Users', backref='attempts')
    question = db.relationship('Questions', backref='attempts')

def get_random_question():
    question = Questions.query.order_by(func.random()).first()
    print(question.question)
    return question

@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(user_id)

@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/game_page', methods=['GET', 'POST'])
@login_required
def game_page():
    if request.method == 'GET':
        # Initialize session and reset game_manager variables if necessary
        if 'start_time' not in session or game_manager.total_count >= 20:
            session.pop('start_time', None)
            session.pop('time_limit', None)

            game_manager.score = 0
            game_manager.total_count = 0
            session['start_time'] = time.time()
            session['time_limit'] = 30  # Reset timer
            session.modified = True

        question = get_random_question()

    else:  # POST request
        question_id = request.form.get('question_id')
        question = Questions.query.get(question_id)
        user_answer = request.form.get('answer')

        if user_answer is None or user_answer.strip() == "":
            game_manager.message = "Please enter an answer!"
            game_manager.correct = False
        else:
            try:
                user_answer = int(user_answer)
                game_manager.correct = user_answer == question.answer
                if game_manager.correct:
                    game_manager.message = "Correct! 🎉"
                    attempt = UserData(
                        user_id=current_user.id,
                        question_id=question_id,
                        user_answer=user_answer,
                        is_correct=game_manager.correct
                    )
                    print(attempt)
                    try:
                        db.session.add(attempt)
                        db.session.commit()
                    except Exception as e:
                        print(f"There was this problem: {e}")
                        return 'There was an error in the database'
                else:
                    game_manager.message = f"You need to practice a bit, The answer was {question.answer}"
                    attempt = UserData(
                        user_id=current_user.id,
                        question_id=question_id,
                        user_answer=user_answer,
                        is_correct=game_manager.correct
                    )
                    try:
                        db.session.add(attempt)
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print(f"The error was: {e}")
                        return "The response was not saved"
            except ValueError:
                game_manager.message = "Invalid input! Please enter a number."
                game_manager.correct = False

        # Update score and count
        game_manager.score_manager(game_manager.correct)

        # Reset game-specific session data if total count reaches 20
        if game_manager.total_count >= 20:
            # Instead of clearing the entire session, remove only game-related keys.
            session.pop('start_time', None)
            session.pop('time_limit', None)
            game_manager.score = 0
            game_manager.total_count = 0
            session.modified = True

        question = get_random_question()

    return render_template('practice_questions.html',
                           question=question.question,
                           question_id=question.id,
                           message=game_manager.message,
                           correct=game_manager.correct,
                           score=game_manager.score,
                           total_questions=game_manager.total_count,
                           )


@app.route('/practice', methods=['GET', 'POST'])
@login_required
def practice_questions():
    # Fetch incorrect attempts
    mistakes = UserData.query.filter_by(user_id=current_user.id, is_correct=False).all()
    mistakes_question_ids = list(set(attempt.question_id for attempt in mistakes))

    question = None
    message = None
    correct = False

    if mistakes_question_ids:
        # Fetch a random question from the user's mistakes
        question = db.session.query(Questions).filter(Questions.id.in_(mistakes_question_ids)).order_by(func.random()).first()

    if request.method == 'POST' and question:
        user_answer = request.form.get('answer')

        if user_answer is None or user_answer.strip() == "":
            message = "Please enter an answer!"
            correct = False
        else:
            try:
                user_answer = int(user_answer)
                correct = user_answer == question.answer

                if correct:
                    message = "Correct! 🎉"
                else:
                    message = f"Incorrect. The correct answer was {question.answer}."

                # Log the attempt
                attempt = UserData(
                    user_id=current_user.id,
                    question_id=question.id,
                    user_answer=user_answer,
                    is_correct=correct
                )

                try:
                    db.session.add(attempt)
                    db.session.commit()
                except Exception as e:
                    print(f"Database error: {e}")
                    return 'There was an error in the database'

            except ValueError:
                message = "Invalid input! Please enter a number."
                correct = False

        # Get another question after answering
        question = db.session.query(Questions).filter(Questions.id.in_(mistakes_question_ids)).order_by(func.random()).first()

    return render_template(
        'practice_questions.html',
        question=question.question if question else "No practice questions available!",
        question_id=question.id if question else None,
        message=message,
        correct=correct
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_data = request.form.get('user_name')
        password = request.form.get('password')
        print(user_data, password)
        user = Users.query.filter_by(user_name=user_data).first()

        if not user:
            flash('Sorry but the user does not exists try registering.')
            return redirect(url_for('register'))
        elif not check_password_hash(user.password, password):
            flash('Password is incorrect', 'error')
            return 'Your password is incorrect.'
        else:
            login_user(user)
            flash("Welcome Back", 'success')
            return redirect(url_for('home_page'))
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        user_name = request.form.get('user_name')
        email = request.form.get('email_address')
        password = request.form.get('password')
        print(f'The name is {name}, The email is {email} and the password is {password}.')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = Users(
            name=name,
            user_name=user_name,
            email=email,
            password=hashed_password,
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            flash('You were successfully registered', 'success')
            return redirect(url_for('home_page'))
        except Exception as e:
            db.session.rollback()
            print(f"the error was {e}")
            return 'An unkown error occurred'

    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    correct_answers = db.session.query(func.count(UserData.id)).filter_by(user_id=user_id, is_correct=True).scalar()
    the_id_for_wrong_question = mode_result(current_user.id)

    repeated_mistake = db.session.query(Questions.question).filter_by(id=the_id_for_wrong_question).scalar()
    answer_to_the_question = db.session.query(Questions.answer).filter_by(id=the_id_for_wrong_question).scalar()
    mistake = f"Question: {repeated_mistake}"
    answer = f"Answer: {answer_to_the_question}"
    print(repeated_mistake)

    user_data = UserData.query.filter_by(user_id=current_user.id).all()
    # plotting all the graphs
    correct = sum(ud.is_correct for ud in user_data)
    incorrect = len(user_data) - correct
    accuracy_for_html = round(correct / len(user_data) * 100, 2) if correct else 0

    fig = px.pie(
        names=["Correct", "Incorrect"],
        values=[correct, incorrect],
        title='Answer Accuracy',
    )
    pie_html = plot(fig, output_type='div')

    daily_correct = defaultdict(int)
    daily_total = defaultdict(int)

    for ud in user_data:
        date = ud.timestamp.date()
        daily_total[date] += 1
        if ud.is_correct:
            daily_correct[date] += 1
    dates = sorted(daily_total.keys())
    accuracy = [(daily_correct[date] / daily_total[date] * 100) for date in dates]
    figure_for_time_analysis = px.line(
        x=dates, y=accuracy,
        title="Daily Accuracy Trend",
        labels={'x': 'Dates', 'y': 'Accuracy (%)'}
    )
    line_chart_html = plot(figure_for_time_analysis, output_type='div')

    return render_template('dashboard.html',
                           score=correct_answers,
                           total=correct,
                           incorrect=incorrect,
                           accuracy=accuracy_for_html,
                           repeated_mistake=mistake,
                           answer=answer,
                           plot=pie_html,
                           accuracy_figure=line_chart_html)


def mode_result(user_id):
    mode_result = (
        db.session.query(UserData.question_id, func.count(UserData.question_id).label("frequency"))
        .filter_by(user_id=user_id, is_correct=False)  # Filter for specific user_id and incorrect answers
        .group_by(UserData.question_id)  # Group by question_id
        .order_by(func.count(UserData.question_id).desc())  # Sort by highest count
        .limit(1)  # Get the most frequent value
        .first()
        )

    return mode_result[0] if mode_result else None


def plot_wrong_answers(user_id):
    # Query the count of wrong answers per question for the given user
    data = (
        db.session.query(UserData.question_id, func.count(UserData.id).label("wrong_count"))
        .filter(UserData.user_id == user_id, UserData.is_correct == False)
        .group_by(UserData.question_id)
        .all()
    )

    if not data:
        print("No data found for the specified user.")
        return

    # Unzip the data into two lists: question_ids and counts
    question_ids, counts = zip(*data)

    # Plotting using matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(question_ids, counts, color='skyblue')
    plt.xlabel("Question ID")
    plt.ylabel("Number of Incorrect Answers")
    plt.title("Wrong Answers per Question")
    plt.xticks(question_ids)  # Ensures each question_id is labeled on the x-axis
    plt.show()



@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)

