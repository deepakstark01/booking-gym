---

# 🏋️‍♂️ FitnessBooker API

A simple and effective API for managing fitness class bookings.

> Easily retrieve, book, view, and cancel fitness classes via clean RESTful endpoints.
> Deployed on [Render](https://booking-gym.onrender.com)

---

## 🌐 Base API URL

```
https://booking-gym.onrender.com/api/v1
```

To use in **Asia/Kolkata** timezone:

```
https://booking-gym.onrender.com/api/v1/classes?timezone=Asia/Kolkata
```

---

## 📬 Postman Collection

Explore and test all API endpoints interactively:

👉 [Open Postman Collection](https://deepakstark.postman.co/workspace/Deepak's~da683c4a-1ba5-4178-bad1-b0cc03990633/collection/25990075-e2a8662e-718f-4415-a4cd-b172c53bcc27?action=share&creator=25990075)

---

## 📘 API Endpoints

### 1. 🔍 Get All Upcoming Fitness Classes

```bash
GET /api/v1/classes?timezone=Asia/Kolkata
```

**Example:**

```bash
curl --location 'http://localhost:8000/api/v1/classes?timezone=Asia%2FKolkata' \
--header 'accept: application/json'
```

---

### 2. 📝 Book a Fitness Class

```bash
POST /api/v1/book
```

**Request Body:**

```json
{
  "class_id": 2,
  "client_name": "Deepak",
  "client_email": "deepak@rezonanz.io"
}
```

**Example:**

```bash
curl --location 'http://localhost:8000/api/v1/book' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
    "class_id": 2,
    "client_name": "Deepak",
    "client_email": "deepak@rezonanz.io"
}'
```

---

### 3. 📋 View Bookings by Email

```bash
GET /api/v1/bookings?email={your_email}&timezone=Asia/Kolkata
```

**Example:**

```bash
curl --location 'http://localhost:8000/api/v1/bookings?email=deepak%40rezonanz.io&timezone=Asia%2FKolkata' \
--header 'accept: application/json'
```

---

### 4. 📅 Get a Specific Class by ID

```bash
GET /api/v1/classes/{id}?timezone=Asia/Kolkata
```

**Example:**

```bash
curl --location 'http://localhost:8000/api/v1/classes/1?timezone=Asia%2FKolkata' \
--header 'accept: application/json'
```

---

### 5. ❌ Cancel a Booking

```bash
POST /api/v1/cancel
```

**Request Body:**

```json
{
  "booking_id": 3,
  "class_id": 1,
  "client_name": "Deepak",
  "client_email": "deepak@rezonanz.io"
}
```

**Example:**

```bash
curl --location 'http://localhost:8000/api/v1/cancel' \
--header 'Content-Type: application/json' \
--data-raw '{
    "booking_id": 3,
    "class_id": 1,
    "client_name": "Deepak",
    "client_email": "deepak@rezonanz.io"
}'
```

---

## ⚙️ Project Structure

```
src/        # Application source code
test/       # Unit and integration tests
data/       # Mock/sample data (e.g., classes.json)
```

---
## install 

``` 
pip install -r requirements.txt

```
---
## 🧪 Running Tests

To run tests using `pytest`:

```bash
pytest
```

---
## Run API

``` 
python main.py

```
---

## 🔖 Notes

* All responses are in **JSON** format.
* Timezone defaults to `Asia/Kolkata` if not provided.
* Replace `class_id`, `booking_id`, and email with actual values during real usage.

---

## 👨‍💻 Author

Developed by **Deepak**
📧 [rohit45deepak@gmail.com(mailto:rohit45deepak@gmail.com)

---
