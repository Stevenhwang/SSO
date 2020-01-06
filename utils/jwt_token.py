import jwt
import datetime
from settings import jwt_settings


class AuthToken:
    def __init__(self):
        self.token_secret = jwt_settings.get('SECRET')

    def encode_token(self, **kwargs):
        exp = kwargs.get('exp', jwt_settings.get('EXP'))
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=int(exp), seconds=10),
            'nbf': datetime.datetime.utcnow() - datetime.timedelta(seconds=10),
            'iat': datetime.datetime.utcnow(),
            'data': {
                'user_id': kwargs.get('user_id', ''),
                'username': kwargs.get('username', ''),
                'email': kwargs.get('email', ''),
                'is_super': kwargs.get('is_super', False)
            }
        }
        return jwt.encode(
            payload,
            self.token_secret,
            algorithm='HS256'
        )

    def decode_token(self, auth_token):
        try:
            payload = jwt.decode(auth_token, self.token_secret, algorithms=[
                'HS256'], leeway=datetime.timedelta(seconds=10))
            return payload['data']
        except Exception:
            return None
