import json
import time
import hashlib
from user.models import *
from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.


def tokens(request):
    if not request.method == 'POST':
        result = {'code': 101, 'error': 'Request Method Error'}
        return JsonResponse(result)

    # 前段地址：http://127.0.0.1:5000/login
    # 获取前段传来的数据,生成token
    # 获取数据-校验密码-生成token
    json_str = request.body
    if not json_str:
        result = {'code': 102, 'error': 'Content error'}
        return JsonResponse(result)

    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    password = json_obj.get('password')
    if not username:
        result = {'code': 103, 'error': 'username error'}
        return JsonResponse(result)
    if not password:
        result = {'code': 104, 'error': 'password error'}
        return JsonResponse(result)

    # 如果用户名及密码都有值，校验数据库是否有该用户
    user = UserProfile.objects.filter(username=username)
    if not user:
        result = {'code': 105, 'error': 'username or password is wrong'}
        return JsonResponse(result)
    # 校验密码是否一致
    user = user[0]
    m = hashlib.md5()
    m.update(password.encode())
    if m.hexdigest() != user.password:
        result = {'code': 106, 'error': 'username or password is wrong'}
        return JsonResponse(result)

    # 生成token
    token = make_token(username)
    result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
    return JsonResponse(result)


def make_token(username, exp=24 * 3600):
    import jwt
    key = '1234567'
    now = time.time()
    payload = {'username': username, 'exp': int(now + exp)}
    return jwt.encode(payload, key, algorithm='HS256')
