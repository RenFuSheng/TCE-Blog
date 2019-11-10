import datetime
import json
import time
import hashlib
import jwt
from django.http import JsonResponse
from user.models import UserProfile
from django.shortcuts import render


# Create your views here.

def make_token(username, exp,now_login_time):
    # 生成token
    key = "1234567ab"
    now_t = time.time()
    payload = {'username': username,'login_time':str(now_login_time),'exp': int(now_t + exp)}
    return jwt.encode(payload, key, algorithm='HS256')


def tokens(request):
    if request.method != "POST":
        result = {'code': 20201, 'error': 'Please give me POST request!'}
        return JsonResponse(result)
    json_str = request.body
    if not json_str:
        result = {'code': 20202, 'error': 'Please give me data!'}
        return JsonResponse(result)
    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    if not username:
        result = {'code': 20203, 'error': 'Please give me username'}
        return JsonResponse(result)
    password = json_obj.get('password')
    if not password:
        result = {'code': 20205, 'error': 'Please give me password'}
        return JsonResponse(result)
    users = UserProfile.objects.filter(username=username)
    if not users:
        result = {'cede': 20208, 'error': 'The user is not existed！'}
        return JsonResponse(result)
    user = users[0]
    pm = hashlib.md5()
    pm.update(password.encode())
    password = pm.hexdigest()
    if user.password != password:
        result = {'code': 20209, 'error': 'The password is not True'}
        return JsonResponse(result)
    #将登录时间存入数据库中
    now_login_time = datetime.datetime.now()
    user.login_time = now_login_time
    user.save()
    # 生成token
    token = make_token(username, 3600 * 24,now_login_time)
    result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}

    return JsonResponse(result)
