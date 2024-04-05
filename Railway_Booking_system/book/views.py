from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .models import trains, Booking
from django.contrib.auth import get_user_model
from django.db import models
from django.db import transaction
from django.db import transaction, IntegrityError


User = get_user_model()


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def user_registration(request):
    """
    API endpoint that allows user registration with a unique username and email.
    Returns a JSON response indicating the success or failure of the registration.
    """
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")
    print(username, password, email)
    if not username or not password or not email:
        return JsonResponse(
            {"error": "Username, password, and email are required"}, status=400
        )

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already taken"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email address already registered"}, status=400)
    User.objects.create_user(username=username, password=password, email=email)
    return JsonResponse({"message": "Registration successful."})


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    """
    API endpoint that allows user login and returns a token upon successful authentication.
    Returns a JSON response with the token or an error message for invalid credentials.
    """
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({"token": token.key})
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=400)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    API endpoint that allows user logout and deletes the authentication token.
    Requires token-based authentication.
    """
    logout(request)
    request.auth.delete()
    return JsonResponse({"message": "Logout successful"})


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_seat(request):
    """
    Endpoint for users to book seats on a particular train.

    Args:
        request: Request object containing train_number, user_id, and seat_count in the data.

    Returns:
        JSON response indicating success or failure of the booking operation.

    Raises:
        HTTP 400 Bad Request: If train_number, user_id, or seat_count is missing.
        HTTP 404 Not Found: If the specified train or user does not exist.
        HTTP 409 Conflict: If a concurrent booking operation failed due to race conditions.
    """
    
    train_number = request.data.get("train_number")
    user_id = request.data.get("user_id")
    seat_count = request.data.get("seat_count")

    if not train_number or not user_id or not seat_count:
        return JsonResponse(
            {"error": "train_number, user_id, and seat_count are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        with transaction.atomic():
            train = trains.objects.select_for_update().get(train_number=train_number)
            user = User.objects.get(id=user_id)

            booked_seats = (
                Booking.objects.filter(train=train).aggregate(
                    total_booked_seats=models.Sum("seat_count")
                )["total_booked_seats"]
                or 0
            )
            available_seats = train.total_seats - booked_seats

            if seat_count > available_seats:
                return JsonResponse(
                    {
                        "error": f"Not enough available seats. Only {available_seats} seats are left"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            booking = Booking.objects.create(
                user=user, train=train, seat_count=seat_count
            )
            return JsonResponse(
                {"message": "Seats booked successfully."},
                status=status.HTTP_201_CREATED,
            )

    except trains.DoesNotExist:
        return JsonResponse(
            {"error": "Train does not exist."}, status=status.HTTP_404_NOT_FOUND
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND
        )

    except IntegrityError:
        return JsonResponse(
            {"error": "Failed to book seat(s) due to concurrent booking."},
            status=status.HTTP_409_CONFLICT,
        )


@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_seat_availability(request):
    source = request.data.get("source")
    destination = request.data.get("destination")
    if not source or not destination:
        return JsonResponse(
            {"error": "Source and destination are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    _trains = trains.objects.filter(source=source, destination=destination)
    if not _trains:
        return JsonResponse(
            {"error": f"No Trains are available between {source} and {destination}"},
            status=status.HTTP_404_NOT_FOUND,
        )
    response_data = []
    for train in _trains:
        total_seats = train.total_seats
        booked_seats = Booking.objects.filter(train=train).aggregate(
            total_booked_seats=models.Sum("seat_count")
        )["total_booked_seats"]
        print("booked_seats", booked_seats)
        if booked_seats is None:
            booked_seats = 0
        available_seats = total_seats - booked_seats
        response_data.append(
            {
                "train_id": train.id,
                "train_number": train.train_number,
                "source": train.source,
                "destination": train.destination,
                "total_seats": total_seats,
                "available_seats": available_seats,
            }
        )
    return JsonResponse(response_data, safe=False, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_booking_details(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND
        )

    bookings = Booking.objects.filter(user=user)
    data = []
    for booking in bookings:
        booking_data = {
            "booking_id": booking.id,
            "train_id": booking.train_id,
            "seat_count": booking.seat_count,
            "Booking_datetime": booking.create_time,
        }
        data.append(booking_data)

    return JsonResponse(data, status=status.HTTP_200_OK, safe=False)


@csrf_exempt
@api_view(["POST"])
def add_train(request):
    if request.user.is_superuser:
        train_number = request.data.get("train_number")
        source = request.data.get("source")
        destination = request.data.get("destination")
        total_seats = request.data.get("total_seats")

        if not source or not destination or not total_seats or not train_number:
            return JsonResponse(
                {
                    "error": "Source, destination, train_number, and total seats are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            total_seats = int(total_seats)
        except ValueError:
            return JsonResponse(
                {"error": "Total seats must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        train = trains.objects.create(
            train_number=train_number,
            source=source,
            destination=destination,
            total_seats=total_seats,
        )
        if train:
            return JsonResponse(
                {"message": "Train added successfully."}, status=status.HTTP_201_CREATED
            )
        else:
            return JsonResponse(
                {"error": "Failed to add train."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        return JsonResponse(
            {"error": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )
