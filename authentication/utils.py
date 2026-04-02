import random
from django.core.mail import EmailMessage
from .models import OneTimePassword
from django.conf import settings

class Util:
    @staticmethod
    def send_generated_otp(user):
        otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        
        OneTimePassword.objects.update_or_create(
            user=user,
            defaults={'code': otp}
        )
        
        subject = "One time passcode for Email verification"
        email_body = f"Hi {user.first_name}, thanks for signing up. Please verify your email with the \n one time passcode: {otp}"
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # Using EmailMessage for more flexibility or send_mail for simplicity
        d_email = EmailMessage(
            subject=subject, body=email_body, from_email=from_email, to=[user.email]
        )
        d_email.send()
        
        print(f"OTP for {user.email}: {otp}") # Helpful for console logs
        return otp