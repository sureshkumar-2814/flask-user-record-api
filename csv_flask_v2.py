from flask import Flask, request, jsonify, make_response, url_for, redirect
import csv
import hashlib
import datetime
import os
from threading import Thread

app = Flask(__name__)
file_path = 'users.csv'

def check_file_exists(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

try:
    check_file_exists(file_path)
except FileNotFoundError as e:
    print(e)
    exit(1)

#FORMAT CHECKS OF DATATYPES#
def is_valid_phone_number(phone_number):
    return phone_number.isdigit() and len(phone_number) == 10

def is_valid_date(date_string):
    try:
        datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_valid_height_weight(value):
    try:
        float_value = float(value)
        return float_value > 0
    except ValueError:
        return False

def hash_phone_number(phone_number):
    return hashlib.sha256(phone_number.encode()).hexdigest()

#READING AND WRITING A CSV FILE#
def read_csv(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        return list(csv_reader)

def write_csv(file_path, data):
    with open(file_path, mode='w', newline='') as file:
        fieldnames = ['name', 'phone', 'dob', 'height', 'weight']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def add_user(file_path, user):
    data = read_csv(file_path)
    user['phone'] = hash_phone_number(user['phone'])
    data.append(user)
    write_csv(file_path, data)

def remove_user_by_phone(file_path, phone_number):
    hashed_phone = hash_phone_number(phone_number)
    data = read_csv(file_path)
    data = [user for user in data if user['phone'] != hashed_phone]
    write_csv(file_path, data)

def get_user_by_phone(file_path, phone_number):
    hashed_phone = hash_phone_number(phone_number)
    data = read_csv(file_path)
    user = next((item for item in data if item['phone'] == hashed_phone), None)
    return user


#ENDPOINTS
@app.route('/users/encrypt_and_get/<phone>', methods=['GET'])
def encrypt_and_get_user(phone):
    if not is_valid_phone_number(phone):
        return make_response(jsonify({"error": "Invalid phone number. It must be numeric and 10 digits long."}), 400)
    
    hashed_phone = hash_phone_number(phone)

    # Redirect to the get_user endpoint with the encrypted phone number
    return redirect(url_for('get_user', encrypted_phone=hashed_phone))

@app.route('/users/<encrypted_phone>', methods=['GET'])
def get_user(encrypted_phone):
    data = read_csv(file_path)
    user = next((item for item in data if item['phone'] == encrypted_phone), None)
    if user:
        # Remove the hashed phone number before returning the user data
        user_data = {key: value for key, value in user.items() if key != 'phone'}
        return make_response(jsonify(user_data), 200)
    else:
        return make_response(jsonify({"error": "User not found"}), 404)


@app.route('/users', methods=['POST'])
def createRecord():
    user = request.json
    phone_number = user.get('phone')
    dob = user.get('dob')
    height = user.get('height')
    weight = user.get('weight')

    if not phone_number or not is_valid_phone_number(phone_number):
        return make_response(jsonify({"error": "Invalid phone number. It must be numeric and 10 digits long."}), 400)

    if not dob or not is_valid_date(dob):
        return make_response(jsonify({"error": "Invalid date of birth. It must be in the format YYYY-MM-DD."}), 400)

    if not height or not is_valid_height_weight(height):
        return make_response(jsonify({"error": "Invalid height. It must be a positive number."}), 400)

    if not weight or not is_valid_height_weight(weight):
        return make_response(jsonify({"error": "Invalid weight. It must be a positive number."}), 400)
    
    if get_user_by_phone(file_path, phone_number):
        return make_response(jsonify({"error": "A user with this phone number already exists."}), 400)

    add_user(file_path, user)
    return make_response(jsonify({"message": "User added successfully"}),201)

@app.route('/users/<phone>', methods=['DELETE'])
def deleteRecord(phone):
    if not is_valid_phone_number(phone):
        return make_response(jsonify({"error": "Invalid phone number. It must be numeric and 10 digits long."}), 400)
    user = get_user_by_phone(file_path, phone)
    if user:
        remove_user_by_phone(file_path, phone)
        return make_response(jsonify({"message": "User removed successfully"}),200)
    else:
        return make_response(jsonify({"error": "User not found"}), 404)

def run_app():
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    thread = Thread(target=run_app)
    thread.start()