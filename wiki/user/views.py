import json, hashlib
import time

import jwt
from django.http import JsonResponse

from wtoken.views import make_token
from .models import UserProfile
from django.shortcuts import render
from tools.logging_check import logging_check

# Create your views here.
@logging_check('PUT')
def users(request, username=None):
    if request.method == "GET":
        # 拿数据
        if username:
            # 拿具体用户数据
            users = UserProfile.objects.filter(username=username)
            if not users:
                return JsonResponse({'code': 208, 'error': 'The user is undefined!'})
            user = users[0]
            if request.GET.keys():
                # 有查询字符串
                data = {}
                for k in request.GET.keys():
                    if hasattr(user, k):
                        # 过滤字段
                        if k == 'password':
                            continue
                        v = getattr(user, k)
                        data[k] = v
                res = {'code': 200, 'username': username, 'data': data}
            else:
                # 无查询字符串
                res = {'code': 200, 'username': user.username,
                       'data': {'nickname': user.nickname, 'sign': user.sign,
                                'info': user.info,'avatar':str(user.avatar)}}

            return JsonResponse(res)
        else:
            all_users = UserProfile.objects.all()
            users_data = []
            for user in all_users:
                dic = {}
                dic['nickname'] = user.nickname
                dic['username'] = user.username
                dic['sign'] = user.sign
                dic['info'] = user.info
                users_data.append(dic)
            res = {'code': 200, 'data': users_data}
            return JsonResponse(res)

    elif request.method == "POST":
        # 创建用户
        json_str = request.body
        if not json_str:
            result = {'code': 10202, 'error': 'Please give me data~'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        username = json_obj.get('username')
        if not username:
            result = {'code': 10203, 'error': 'Please give me username~'}
            return JsonResponse(result)
        email = json_obj.get("email")
        if not email:
            result = {'code': 10204, 'error': 'Please give me email~'}
            return JsonResponse(result)
        password1 = json_obj.get("password_1")
        password2 = json_obj.get("password_2")
        if not password1 or not password2:
            result = {'code': 10205, 'error': 'Please input password~'}
            return JsonResponse(result)
        if password1 != password2:
            result = {'code': 10206, 'error': 'The password is error!'}
            return JsonResponse(result)
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 10207, 'error': 'The username is existed!'}
            return JsonResponse(result)
        # 生成散列密码
        pm = hashlib.md5()
        pm.update(password1.encode())
        password = pm.hexdigest()
        # 创建用户
        try:
            user = UserProfile.objects.create(username=username, email=email, password=password, nickname=username)
        except Exception as e:
            print('---create error---')
            print(e)
            result = {'code': 10208, 'error': 'The username is existed!!'}
            return JsonResponse(result)

        # 生成token
        token = make_token(username, 3600 * 24)
        result = {'code': 200, 'data': {'token': token.decode()}, 'username': username}

        return JsonResponse(result)

    elif request.method == "PUT":
        # 更新
        if not username:
            res = {'code':10108,'error':'Must be give me username!!'}
            return JsonResponse(res)
        json_str = request.body
        if not json_str:
            res = {'code':10202,'error':'please put data'}
            return JsonResponse(res)
        json_obj = json.loads(json_str)
        sign = json_obj.get('sign')
        info = json_obj.get('info')
        nickname = json_obj.get('nickname')
        #查询用户
        # users = UserProfile.objects.filter(username=username)
        # user = users[0]
        user = request.user
        #当前请求，token用户 修改自己的数据
        if user.username != username:
            result = {'code':20209,'error':'The username is error!'}
            return JsonResponse(result)
        to_update = False
        if user.nickname != nickname:
            to_update = True
        if user.info != info:
            to_update = True
        if user.sign != sign:
            to_update = True
        if to_update:
            #做更新
            user.sign,user.info,user.nickname = sign,info,nickname
            user.save()
        res = {'code':200,'username':username}
        return JsonResponse(res)

@logging_check('POST')
def users_avatar(request,username):
    #处理头像上传
    if request.method != 'POST':
        result = {'code':20210,'error':'Please use POST'}
        return JsonResponse(result)
    user = request.user
    if user.username != username:
        result = {'code':20209,'error':'The username is error!'}
        return JsonResponse(result)
    user.avatar = request.FILES['avatar']
    user.save()
    return JsonResponse({'code':200,'username':username})


