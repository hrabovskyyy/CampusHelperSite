from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime, timedelta
import json
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = 'your_secret_key'  # Задайте секретний ключ для сесій
db = SQLAlchemy(app)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(256), nullable=False)  # Додано поле для ПІБ
    group = db.Column(db.String(50), nullable=False)  # Додано поле для групи

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime)
    buttons = db.Column(db.String(256), nullable=True)

# Створення бази даних в контексті додатку
with app.app_context():
    db.create_all()



@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return jsonify(success=False, message='Please log in')

    user_id = session['user_id']

    if request.method == 'POST':
        user_message = request.json.get('message')

        if user_message:
            chat_history = ChatHistory(user_id=user_id, message=user_message)
            db.session.add(chat_history)

            if user_message.lower() == "/start":
                bot_response = "Привіт! Я ваш Campus Helper. Виберіть одну з опцій нижче:"
                buttons = [
                    {"label": "Опція 1", "action": "option1"},
                    {"label": "Опція 2", "action": "option2"},
                    {"label": "Опція 3", "action": "option3"}
                ]
                chat_history.buttons = json.dumps(buttons)
                db.session.commit()
                return jsonify({'response': bot_response, 'buttons': buttons})
            else:
                bot_response = "Ваше повідомлення: " + user_message
                db.session.commit()
                return jsonify({'response': bot_response})

        return jsonify({'response': "Повідомлення не розпізнано"})

    elif request.method == 'GET':
        history = ChatHistory.query.filter_by(user_id=user_id).all()
        now = datetime.now()  # Get the current date and time
        return render_template('chat.html', messages=history, now=now, json=json)  # Pass now to the template

@app.route('/button_click', methods=['POST'])
def button_click():
    button_action = request.json.get('action')
    user_id = session['user_id']
    chat_history = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.timestamp.desc()).first()
    chat_history.message = f"Button {button_action} clicked"
    db.session.commit()
    return jsonify({'response': f"Button {button_action} clicked"})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        session.permanent = True  # Зробити сесію постійною
        app.permanent_session_lifetime = timedelta(minutes=5)  # Час дії сесії 5 хвилин
        session['user_id'] = user.id
        return jsonify(success=True)
    return jsonify(success=False, message='Неправильне ім\'я користувача або пароль')


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify(success=False, message='Це ім\'я користувача вже зайняте')

    # Ensure full_name and group are included
    new_user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        full_name=data['full_name'],  # Add full_name
        group=data['group']            # Add group
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(success=True)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)