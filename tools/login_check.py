from django.http import JsonResponse
from user.models import UserProfile
import jwt


KEY = '1234567'


# login_check('PUT', 'GET', 'POST')
def login_check(*methods):
    def _login_check(func):
        def wrapper(request, *args, **kwargs):
            # 通过request检查token
            # 校验不通过 return JsonResponse()
            # 查询user
            token = request.META.get('HTTP_AUTHORIZATION')
            if request.method not in methods:
                return func(request, *args, **kwargs)
            if not token:
                result = {'code': 107, 'error': 'please give me token'}
                return JsonResponse(result)
            try:
                res = jwt.decode(token, KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                # token过期
                result = {'code': 108, 'error': 'please login'}
                return JsonResponse(result)
            except Exception as e:
                result = {'code': 109, 'error': 'please login!'}
                return JsonResponse(result)
            username = res['username']
            try:
                user = UserProfile.objects.get(username=username)
            except:
                user = None
            if not user:
                result = {'code': 110, 'error': 'no user'}
                return JsonResponse(result)
            # 将查询成功的user赋值给request
            request.user = user
            return func(request, *args, **kwargs)
        return wrapper
    return _login_check


def get_user_by_request(request):
    """
    通过request尝试获取user
    :param request:
    :return: UserProfile obj or None
    """
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    try:
        res = jwt.decode(token, KEY)
    except:
        return None
    username = res['username']
    try:
        user = UserProfile.objects.get(username=username)
    except:
        return None
    return user