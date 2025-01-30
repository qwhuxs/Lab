import json
import re
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  

USERS_FILE = 'users.json'

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class JSONManager:
    @staticmethod
    def load_data(file_path, default_data):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.error(f"Помилка з файлом {file_path}. Використано значення за замовчуванням.")
            return default_data
        except Exception as e:
            logging.error(f"Невідома помилка при читанні файлу {file_path}: {e}")
            return default_data

    @staticmethod
    def save_data(file_path, data):
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            logging.error(f"Помилка запису в файл {file_path}: {e}")
            flash('Помилка збереження даних. Спробуйте ще раз.', 'error')

class UserManager:
    @staticmethod
    def load_users():
        users = JSONManager.load_data(USERS_FILE, {})
        return users if isinstance(users, dict) else {}

    @staticmethod
    def save_users(users):
        JSONManager.save_data(USERS_FILE, users)

    @staticmethod
    def register_user(username, password):
        users = UserManager.load_users()
        if username in users:
            return False  
        users[username] = {"password": password, "role": "user"}
        UserManager.save_users(users)
        return True

    @staticmethod
    def authenticate_user(username, password):
        users = UserManager.load_users()
        return username in users and users[username]['password'] == password

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if UserManager.register_user(username, password):
            flash('Реєстрація успішна!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Користувач вже існує!', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
