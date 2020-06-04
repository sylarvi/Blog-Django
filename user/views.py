import json
import hashlib
from .models import *
from django.shortcuts import render
from django.http import JsonResponse
from btoken.views import make_token
from tools.login_check import login_check


# Create your views here.

@login_check('PUT')
def users(request, username=None):
    if request.method == 'GET':
        # 获取用户数据
        if username:
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                user = None
                if not user:
                    result = {'code': 208, 'error': 'no user'}
                    return JsonResponse(result)
            # 检查是否有查询字符串
            if request.GET.keys():
                # 查询指定字段
                data = {}
                for k in request.GET.keys():
                    if hasattr(user, k):
                        v = getattr(user, k)
                        if k == 'avatar':
                            data[k] = str(v)
                        else:
                            data[k] = v
                result = {'code': 200, 'username': username, 'data': data}
                return JsonResponse(result)
            else:
                # 全量查询,不包括密码与邮箱
                result = {'code': 200, 'username': username,
                          'data': {'info': user.info, 'sign': user.sign, 'avatar': str(user.avatar),
                                   'nickname': user.nickname}}
                return JsonResponse(result)
        else:
            return JsonResponse({'code': 200, 'error': 'test'})
    elif request.method == 'POST':
        # 创建用户数据
        # print(request.body)
        json_str = request.body
        if not json_str:
            result = {'code': 201, 'error': 'Data Is Null'}
            return JsonResponse(result)

        json_obj = json.loads(json_str)

        username = json_obj.get('username')
        if not username:
            result = {'code': 202, 'error': 'username is null'}
            return JsonResponse(result)
        email = json_obj.get('email')
        if not email:
            result = {'code': 203, 'error': 'email is null'}
            return JsonResponse(result)
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if not password_1 or not password_2:
            result = {'code': 204, 'error': 'password is null'}
            return JsonResponse(result)
        if password_1 != password_2:
            result = {'code': 205, 'error': 'password_1 is not same as password_2'}
            return JsonResponse(result)

        # 检查当前数据库是否有此用户
        user = UserProfile.objects.filter(username=username)
        if user:
            result = {'code': 206, 'error': 'your username is already existed!'}
            return JsonResponse(result)
        # 处理密码 md5/哈希/散列
        m = hashlib.md5()
        m.update(password_1.encode())
        # 个人签名/个人信息 可以为空
        sign = info = ''
        try:
            UserProfile.objects.create(
                username=username,
                nickname=username,
                password=m.hexdigest(),
                email=email,
                sign=sign,
                info=info
            )
        except Exception as e:
            result = {'code': 207, 'error': 'Server is busy, please try again'}
            return JsonResponse(result)

        # 生成token
        token = make_token(username)
        # 正常返回给前端
        result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
        return JsonResponse(result)
    elif request.method == 'PUT':
        # http://127.0.0.1:5000/<username>/change_info
        # 修改个人信息, 更新用户数据
        # 获取前端传来的token
        # META可拿取http协议原生头，META也是类字典对象，可使用字典相关方法
        # 特别注意 http头有可能被django重命名
        user = request.user
        json_str = request.body
        if not json_str:
            result = {'code': 209, 'error': 'please give me token'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        if 'sign' not in json_obj:
            result = {'code': 210, 'error': 'no sign'}
            return JsonResponse(result)
        if 'info' not in json_obj:
            result = {'code': 211, 'error': 'no info'}
            return JsonResponse(result)
        sign = json_obj.get('sign')
        info = json_obj.get('info')
        request.user.sign = sign
        request.user.info = info
        request.user.save()
        result = {'code': 200, 'username': request.user.username}
        return JsonResponse(result)

    else:
        raise


@login_check('POST')
def user_avatar(request, username=None):
    # 上传用户头像
    if request.method != 'POST':
        result = {'code': 212, 'error': 'I need post'}
        return JsonResponse(result)
    avatar = request.FILES.get('avatar')
    if not avatar:
        result = {'code': 213, 'error': 'I need avatar'}
        return JsonResponse(result)
    # TODO 判断url中的username是否跟token中的username一致，若不一致，则返回error
    request.user.avatar = avatar
    request.user.save()
    result = {'code': 200, 'username': request.user.username}
    return JsonResponse(result)
