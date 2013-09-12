from django.dispatch import Signal

signup_complete = Signal(providing_args=["user",])
activation_complete = Signal(providing_args=["user",])
confirmation_complete = Signal(providing_args=["user","old_email"])
password_complete = Signal(providing_args=["user",])
