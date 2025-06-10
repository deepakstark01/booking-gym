# FitnessBooker API

A simple API for managing fitness class bookings.

---

## Endpoints & Example Usage
#####  get access of postman collection  
```https://deepakstark.postman.co/workspace/Deepak's~da683c4a-1ba5-4178-bad1-b0cc03990633/collection/25990075-e2a8662e-718f-4415-a4cd-b172c53bcc27?action=share&creator=25990075```
### 1. Get All Upcoming Fitness Classes

```bash
curl --location 'http://localhost:8000/api/v1/classes?timezone=Asia%2FKolkata' \
--header 'accept: application/json'
```

---

### 2. Book a Fitness Class

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

### 3. Get Bookings by Email

```bash
curl --location 'http://localhost:8000/api/v1/bookings?email=deepak%40rezonanz.io&timezone=Asia%2FKolkata' \
--header 'accept: application/json'
```

---

### 4. Get a Specific Class by ID

```bash
curl --location 'http://localhost:8000/api/v1/classes/1?timezone=Asia%2FKolkata' \
--header 'accept: application/json'
```

---

### 5. Cancel a Booking

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

## Notes

- Replace IDs and emails in the examples with your actual data.
- All endpoints return JSON responses.
- Timezone defaults to `Asia/Kolkata` if not specified.

---

## Project Structure

- `src/` - Application source code
- `test/` - Unit and integration tests
- `data/` - Mock/sample data (e.g., `classes.json`)

---

## Running Tests

```bash
pytest
```

---

