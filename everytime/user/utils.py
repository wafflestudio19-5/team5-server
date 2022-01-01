import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp)) + six.text_type(user.school_email)


email_verification_token = EmailVerificationTokenGenerator()

def message(domain, uidb64, token, emailb64):
    return f"아래 링크를 클릭하면 학교 인증이 완료됩니다.\n\n학교인증 링크 : http://{domain}/user/verify/accepted/{uidb64}/{token}/{emailb64}/\n\n감사합니다."