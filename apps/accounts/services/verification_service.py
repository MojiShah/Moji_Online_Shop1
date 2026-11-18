
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):

    # A separate cryptographic namespace for email verification
    key_salt = "apps.accounts.tokens.EmailVerificationTokenGenerator"

    def _make_hash_value(self, user, timestamp):

        return (
            super()._make_hash_value(user, timestamp)
            + str(user.is_email_verified)
        )


email_verification_token = EmailVerificationTokenGenerator()


def send_verification_email(user):

    # Generate email verification token
    token = email_verification_token.make_token(user)

    # Encode UUID user ID
    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    # Build verification URL
    verification_url = (
        f"{settings.EMAIL_VERIFICATION_FRONTEND_URL}"
        f"?uid={uid}&token={token}"
    )

    subject = "Moji Online Shop - Verify Your Email"

    message = f"""
                Hello {user.first_name or 'User'},
                Thank you for registering with Moji Online Shop.
                Please verify your email address using the link below:
                {verification_url}
                This link expires in 30 minutes.
                If you did not create this account, you can ignore this email.
                Moji Online Shop
                """

    sent_count = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return sent_count == 1
