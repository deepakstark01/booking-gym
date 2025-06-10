

1. Get all upcoming fitness classes

curl -X GET "http://localhost:8000/api/v1/classes?timezone=Asia/Kolkata" -H "accept: application/json"


2. Book a fitness class
curl -X POST "http://localhost:8000/api/v1/book" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 1,
    "client_name": "Deepak",
    "client_email": "deepak@rezonanz.io"
  }'


3. Get booking status by email
curl -X POST "http://localhost:8000/api/v1/book" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 1,
    "client_name": "John Doe",
    "client_email": "john@example.com"
  }'



4. Get bookings by email
curl -X GET "http://localhost:8000/api/v1/bookings?email=john@example.com&timezone=Asia/Kolkata" -H "accept: application/json"

5. Get a specific class by ID
curl -X GET "http://localhost:8000/api/v1/classes/1?timezone=Asia/Kolkata" -H "accept: application/json"