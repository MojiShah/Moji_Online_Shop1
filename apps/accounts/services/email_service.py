from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

def send_password_reset_email(user):

    # Generate secure reset token
    token = default_token_generator.make_token(user)

    # Encode user ID
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Build frontend reset URL
    reset_url = (
        f"{settings.PASSWORD_RESET_FRONTEND_URL}"
        f"?uid={uid}&token={token}"
    )

    subject = "Moji Online Shop - Password Reset"

    message = f"""
    Hello {user.first_name or 'User'},
    We received a request to reset your password.
    Use the following link to reset your password:

    {reset_url}

    This link expires in 30 minutes.
    If you did not request this change, you can ignore this email.
    Moji Online Shop
    """

    # send_mail(
    #     subject=subject,
    #     message=message,
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=[user.email],
    #     fail_silently=False,
    # )
    
    sent_count = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    # return True
    return sent_count == 1
