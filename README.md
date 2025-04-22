# flask-user-record-api
API to manage (create, fetch and delete user data) a CSV database using mobile number, which is encrypted by SHA-256 algorithm.

---

## Features

- Create user record with validation (name, phone, DOB, height, weight)
- Hashes phone numbers using SHA-256
- Stores all data in a `CSV` file
- Retrieve records by encrypted phone
- Delete records using phone number + internal password key

---

## Tech Stack

- `Flask` – RESTful API framework  
- `pandas` – Reading structured CSV data  
- `hashlib` – Phone number encryption  
- `datetime` – DOB format validation  
- `threading` – Optional threading control  
- `csv` – CSV file I/O  

---

## API Endpoints

### `POST /createRecord`
Creates a new user record.

#### Sample JSON Body:
```json
{
  "name": "John Doe",
  "phone": "9876543210",
  "dob": "1990-01-01",
  "height": "175",
  "weight": "70"
}

### `GET /getRecord/<hashed_phone>`
Returns user record by encrypted phone (without showing phone number).

### `POST /deleteRecord/<phone>`
Deletes a user record by matching a hashed phone number (salted with internal password).

### `Data Validations`
Phone number: 10 digits, numeric only

DOB: Format YYYY-MM-DD

Height/Weight: Must be numeric and positive

### `Security Note`
Phone numbers are hashed using SHA-256 + a simple internal salt. While not industry-grade encryption, this prevents plain-text storage in the CSV.


##### version 2.0 changes #####
- Error Handling
- Endpoints handle changed (as a better practice)
- Delete user data method changed (POST to DELETE)
- Create user data: Duplicates of mobile number not allowed
- Checks for CSV file in folder
- Get user data: /users/encrypt_and_get/<phone>


#### OTHER POSSIBLE SCOPE ####
- Better CSV file handling - searching for data in an efficient way, queuing, cache handling etc.
- UI/HTML for Get User data, where user can input data and that will get encrypted in the backend.
- Microservices to split into different servies (user management, validation, hashing etc)

Made by [Suresh Kumar] — learning REST APIs by solving real-world use cases.