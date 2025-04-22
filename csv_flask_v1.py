from flask import Flask, request, jsonify
import csv
import hashlib
import datetime
from threading import Thread
import pandas as pd

app = Flask(__name__)
file_path = 'users.csv'
password_hash = 'helloworld'

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
        #csv_reader = csv.DictReader(file)
        csv_reader = pd.read_csv(file_path).to_dict()
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
    phone_number+=password_hash
    hashed_phone = hash_phone_number(phone_number)
    data = read_csv(file_path)
    data = [user for user in data if user['phone'] != hashed_phone]
    write_csv(file_path, data)

def get_user_by_encrypted_phone(file_path, encrypted_phone):
    data = read_csv(file_path)
    user = next((item for item in data if item['phone'] == encrypted_phone), None)
    return user


#ENDPOINTS
@app.route('/getRecord/<encrypt_phone>', methods=['GET'])
def getRecord(encrypt_phone):
    user = get_user_by_encrypted_phone(file_path, encrypt_phone)
    if user:
        user_data = {key: value for key, value in user.items() if key != 'phone'}
        return jsonify(user_data)
    else:
        return jsonify({"error": "User not found"})


@app.route('/createRecord', methods=['POST'])
def createRecord():
    user = request.json
    phone_number = user.get('phone')
    name = user.get('name')
    dob = user.get('dob')
    height = user.get('height')
    weight = user.get('weight')

    if not name:
        return jsonify({"error": "Name is mandatory."})

    if not phone_number or not is_valid_phone_number(phone_number):
        return jsonify({"error": "Invalid phone number. It must be numeric and 10 digits long."})

    if not dob or not is_valid_date(dob):
        return jsonify({"error": "Invalid date of birth. It must be in the format YYYY-MM-DD."})

    if not height or not is_valid_height_weight(height):
        return jsonify({"error": "Invalid height. It must be a positive number."})

    if not weight or not is_valid_height_weight(weight):
        return jsonify({"error": "Invalid weight. It must be a positive number."})

    add_user(file_path, user)
    return jsonify({"message": "User added successfully"})

@app.route('/deleteRecord/<phone>', methods=['POST'])
def deleteRecord(phone):
    if not is_valid_phone_number(phone):
        return jsonify({"error": "Invalid phone number. It must be numeric and 10 digits long."})
    user = get_user_by_encrypted_phone(file_path, hash_phone_number(phone))
    if user:
        remove_user_by_phone(file_path, phone)
        return jsonify({"message": "User removed successfully"})
    else:
        return jsonify({"error": "User not found"})

def run_app():
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    thread = Thread(target=run_app)
    thread.start()