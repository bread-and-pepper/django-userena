from django.dispatch import Signal

signup_complete = Signal(providing_args=["user",])
activation_complete = Signal(providing_args=["user",])
confirmation_complete = Signal(providing_args=["user",])
password_complete = Signal(providing_args=["user",])
