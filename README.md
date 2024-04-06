# Train Booking System API

This is a RESTful API for a train booking system. It provides endpoints for user registration, login, booking seats on trains, fetching seat availability, and getting booking details. The API is built using Django and Django Rest Framework.

## Installation

1. Clone the repository:
```python
https://github.com/adarshkumar5776/railway_booking_system
```

2. Install the required dependencies:
```python
pip install -r requirements.txt
```

3. Run migrations to set up the database:
```python
python manage.py makemigrations
python manage.py migrate
```

4. Start the development server:
```python
python manage.py runserver
```

5. Access the API at `http://localhost:8000/`.

## Database

PostgreSQL is used with the following configuration:

```python
'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'RailwayBookingSystem',
        'USER': 'postgres',
        'PASSWORD':'1234',
        'HOST':'localhost' 
    }
```

## Endpoints

### User Registration

- **URL:** `/user/register/`
- **Method:** `POST`
- **Description:** Register a new user with a unique username and email.
- **Parameters:**
- `username` (string): User's username.
- `password` (string): User's password.
- `email` (string): User's email address.

### User Login

- **URL:** `/user/login/`
- **Method:** `POST`
- **Description:** Login an existing user and receive an authentication token.
- **Parameters:**
- `username` (string): User's username.
- `password` (string): User's password.
- **Authorization:** None

### User Logout

- **URL:** `/user/logout/`
- **Method:** `POST`
- **Description:** Logout the authenticated user and delete the authentication token.
- **Authorization:** Token-based authentication required.

### Add Train

- **URL:** `/add_train/`
- **Method:** `POST`
- **Description:** Add a new train with a unique train number, source, destination, and total seats.
- **Parameters:**
- `train_number` (integer): Train number (unique).
- `source` (string): Source station.
- `destination` (string): Destination station.
- `total_seats` (integer): Total number of seats on the train.
- **Authorization:** Superuser authentication required.

### Book Seat

- **URL:** `/user/book_seat/`
- **Method:** `POST`
- **Description:** Book seats on a particular train.
- **Parameters:**
- `train_number` (integer): Train number.
- `user_id` (integer): User's ID.
- `seat_count` (integer): Number of seats to book.
- **Authorization:** Token-based authentication required.

### Get Seat Availability

- **URL:** `/user/get_seat_availability/`
- **Method:** `GET`
- **Description:** Fetch seat availability for trains between specified source and destination.
- **Parameters:**
- `source` (string): Source station.
- `destination` (string): Destination station.
- **Authorization:** Token-based authentication required.

### Get Booking Details

- **URL:** `/user/get_booking_details/<int:id>/`
- **Method:** `GET`
- **Description:** Fetch booking details for a specific user.
- **Parameters:**
- `id` (integer): User's ID.
- **Authorization:** Token-based authentication required.

## Authentication

- **Token Authentication:** Authentication is required for most endpoints using a token-based authentication system. Users must login to obtain a token, which should be included in the `Authorization` header of subsequent requests.
- **CSRF Token:** CSRF tokens are required for certain endpoints to prevent CSRF attacks. Ensure that the CSRF token is included in the request headers.

## Error Handling

- Errors are returned as JSON objects with appropriate status codes and error messages.
- Common error responses include:
- `400 Bad Request`: Invalid request parameters.
- `401 Unauthorized`: Unauthorized access.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Resource not found.
- `409 Conflict`: Concurrent booking operation failed.
- Detailed error messages provide guidance on how to resolve issues.

### Models

#### Train Model

The `Train` model represents a train in the system. It includes the following fields:

- `train_number`: An integer field representing the unique number assigned to the train.
- `source`: A character field indicating the origin station of the train journey.
- `destination`: A character field indicating the destination station of the train journey.
- `total_seats`: An integer field representing the total number of seats available on the train.
- `create_time`: A DateTime field automatically capturing the date and time when the train record was created.
- `update_time`: A DateTime field automatically capturing the date and time when the train record was last updated.

This model is used to manage information about trains, including their identification, origin, destination, total available seats, and timestamps for creation and updates.

#### Booking Model

The `Booking` model represents a booking made by a user for a specific train in the system. It includes the following fields:

- `user`: A foreign key field linking to the `User` model, representing the user who made the booking.
- `train`: A foreign key field linking to the `Train` model, representing the train for which the booking is made.
- `seat_count`: An integer field representing the number of seats booked by the user for the train.
- `create_time`: A DateTime field automatically capturing the date and time when the booking record was created.
- `update_time`: A DateTime field automatically capturing the date and time when the booking record was last updated.

This model is used to manage information about bookings made by users, including details such as the user who made the booking, the train for which the booking is made, the number of seats booked, and timestamps for creation and updates.


### Note on Race Condition Handling

The `book_seat` function employs database transactions and row-level locking to address the race condition issue. Here's how it works:

```python
# In the book_seat function
try:
    with transaction.atomic():
        # Use select_for_update() to acquire a row-level lock
        train = trains.objects.select_for_update().get(train_number=train_number)

        # Critical section of code where seats are booked
        # ...

except IntegrityError:
    # Handle the case where a concurrent booking operation fails due to row-level lock
    # Return an appropriate error response indicating the failure


