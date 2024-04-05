from django.urls import path,include
from . import views

urlpatterns = [
    path('user/register/', views.user_registration, name='user_registration'),
    path('user/login/', views.user_login, name='user_login'),
    path('user/logout/', views.user_logout, name='user_logout'),
    path('add_train/', views.add_train, name='add_train'),
    path('user/book_seat/', views.book_seat, name='book_seat'),
    path('user/get_seat_availability/', views.get_seat_availability, name='get_seat_availability'),
    path('user/get_booking_details/<int:id>', views.get_booking_details, name='get_booking_details')

]
