from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.utils.translation import gettext_lazy as _
from .models import DeviceToken
from .services import update_device_last_used


class DeviceJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that validates device tokens
    """
    
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        
        # Get device ID from token
        device_id = validated_token.get('device_id')
        if not device_id:
            raise InvalidToken(_('Token does not contain device information'))
        
        # Validate device token
        try:
            device_token = DeviceToken.objects.get(
                id=device_id,
                is_active=True
            )
            
            # Check if device token is expired
            if device_token.is_expired():
                raise InvalidToken(_('Device token has expired'))
            
            # Update last used timestamp
            update_device_last_used(device_id)
            
        except DeviceToken.DoesNotExist:
            raise InvalidToken(_('Device token not found or inactive'))
        
        return self.get_user(validated_token), validated_token

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in self.auth_token_classes:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append({
                    'token_class': AuthToken.__name__,
                    'token_type': AuthToken.token_type,
                    'message': e.args[0],
                })

        raise InvalidToken({
            'detail': _('Given token not valid for any token type'),
            'messages': messages,
        }) 