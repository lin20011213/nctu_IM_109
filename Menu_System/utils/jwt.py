import jwt
import datetime
from django.conf import settings
from django.http import HttpResponse
from functools import wraps

def generate_jwt(user):
    payload = {
        'id': user.id,
        'name': user.name,
        'account': user.account,
        'phone_number': user.phone_number,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=2),  # Token expires in 2 days
        'iat': datetime.datetime.now(datetime.UTC)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
    
def jwt_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')  # 从 Cookie 获取 token，或者从 request.headers.get('Authorization')
        if token:
            try:
                # 解码 JWT
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                request.user_info = decoded  # 将解码信息存储在 request 中
            except jwt.ExpiredSignatureError:
                return HttpResponse("Token has expired", status=401)
            except jwt.InvalidTokenError:
                return HttpResponse("Invalid Token", status=401)
        else:
            return HttpResponse("No token provided", status=401)
        
        return f(request, *args, **kwargs)
    return decorated_function