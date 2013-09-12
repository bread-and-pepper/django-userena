from django.dispatch import Signal

signup_complete = Signal(providing_args=["user",])
activation_complete = Signal(providing_args=["user",])
confirmation_complete = Signal(providing_args=["user","old_email"])
password_complete = Signal(providing_args=["user",])
email_change = Signal(providing_args=["user","prev_email","new_email"])
profile_change = Signal(providing_args=["user",])
account_signin = Signal(providing_args=["user",])
account_signout = Signal(providing_args=["user",])
