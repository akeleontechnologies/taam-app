from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token


class ExpiringTokenAuthentication(TokenAuthentication):
    model = Token
    keyword = 'Bearer'

    def authenticate_credentials(self, key: str):
        try:
            token = self.model.objects.select_related("user").get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User is not active."))

        is_expired, token = ExpiringTokenAuthentication.validate_token_expiration(token)
        if is_expired:
            raise exceptions.AuthenticationFailed(_("User token has expired"))

        return token.user, token

    @staticmethod
    def validate_token_expiration(token: Token):
        is_expired = ExpiringTokenAuthentication.is_expired(token)
        if is_expired:
            token.delete()

        return is_expired, token

    @staticmethod
    def expires_in(token: Token) -> timedelta:
        time_elapsed = timezone.now() - token.created
        time_remaining = timedelta(
            seconds=settings.AUTHENTICATION_TOKEN_EXPIRES_AFTER_SECONDS - time_elapsed.total_seconds()
        )
        return time_remaining

    @staticmethod
    def is_expired(token: Token) -> bool:
        time_remaining = ExpiringTokenAuthentication.expires_in(token)
        return time_remaining < timedelta(seconds=0)
