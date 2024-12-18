from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["cattle_farm"]
users_collection = db["users"]
animals_collection = db["animals"]

# User registration and login
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Hash the password for security
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_data = {
            'username': username,
            'password': hashed_password
        }
        users_collection.insert_one(user_data)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Successful login, redirect to dashboard or other pages
            return redirect(url_for('dashboard'))
        else:
            # Incorrect username or password
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

# Dashboard for individual animal
@app.route('/dashboard/<animal_id>')
def dashboard(animal_id):
    animal_data = animals_collection.find_one({"animal_id": animal_id})
    return render_template('dashboard.html', animal=animal_data)

# Form to add new animal data
@app.route('/add_animal', methods=['GET', 'POST'])
def add_animal(datetime=None):
    if request.method == 'POST':
        animal_id = request.form['animal_id']
        breed = request.form['breed']
        birth_date_str = request.form['birth_date']
        weight = float(request.form['weight'])
        food_consumption = float(request.form['food_consumption'])
        milk_production = float(request.form['milk_production'])
        health_status = request.form['health_status']
        user_id = request.form['user_id']

        # Validate input data (example: basic validation)
        if not animal_id or not breed or not birth_date_str:
            return render_template('add_animal.html', error='Please fill in required fields')

        # Convert birth_date to ISO 8601 format
        try:
            birth_date_obj = datetime.strptime(birth_date_str, '%Y-%m-%d')
            birth_date_iso = birth_date_obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            return render_template('add_animal.html', error='Invalid birth date format')

        # Insert the data into the MongoDB collection
        result = animals_collection.insert_one({
            'animal_id': animal_id,
            'breed': breed,
            'birth_date': birth_date_iso,
            'weight': weight,
            'food_consumption': food_consumption,
            'milk_production': milk_production,
            'health_status': health_status,
            'user_id': user_id
        })

        if result.acknowledged:
            return redirect(url_for('dashboard'))
        else:
            return render_template('add_animal.html', error='Error inserting animal data')

    return render_template('add_animal.html')

# ... (other routes for editing, deleting, and visualizing data)

if __name__ == '__main__':
    app.run(debug=True)