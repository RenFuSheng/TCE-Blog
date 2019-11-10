import json

from django.http import JsonResponse
from django.shortcuts import render

from message.models import Message
from tools.logging_check import logging_check, get_user_by_request
# Create your views here.
from topic.models import Topic
from user.models import UserProfile
import html


@logging_check('POST','DELETE')
def topics(request,username):
    if request.method == 'POST':
        user = request.user
        if username != user.username:
            result = {'code': 20213, 'error': 'The username is error'}
            return JsonResponse(result)
        json_str = request.body
        if not json_str:
            result = {'code':20212,'error':'Please give data'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        title = json_obj.get('title')
        #注意xss攻击
        title = html.escape(title)
        category = json_obj.get('category')
        if category not in ['tec','no-tec']:
            result = {'code':20213,'error':'Thanks your category is error!!'}
            return JsonResponse(result)
        limit = json_obj.get('limit')
        if limit not in ['private','public']:
            result = {'code':20214,'error':'Thanks your limit is error!!'}
            return JsonResponse(result)
        #带样式的文章内容
        content = json_obj.get('content')
        #纯文本的文章内容 - 用于做文章简介的切片
        content_text = json_obj.get('content_text')
        introduce = content_text[:30]
        #创建topic
        try:
            Topic.objects.create(title=title,category=category,
                                 limit=limit,introduce = introduce,content=content,author=user)
        except Exception as e:
            print(e)
        return JsonResponse({'code':200,'username':user.username})

    if request.method == 'GET':
        #获取用户文章数据
        #/v1/topics/xiaoyaoguai - xiaoyaoguai 的所有文章
        #/v1/topics/xiaoyaoguai?category=tec 查看具体种类
        #/v1/topics/xiaoyaoguai?t_id
        #1.访问当前博客的访问者 visitor
        #2.当前被访问的博客的博主 author
        #获取用户具体分类的数据
        users = UserProfile.objects.filter(username=username)
        if not users:
            result = {'code':'20215','error':'The user is not existed!'}
            return JsonResponse(result)
        #当前被访问的博客博主
        user = users[0]
        #访问者
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username

        t_id = request.GET.get('t_id')
        if t_id:
            t_id = int(t_id)
            #获取指定文章的详情页
            is_self = False
            if username == visitor_username:
                #博主本人访问自己的博客
                #生成标记为True 为博主访问自己，False为陌生访客访问博主
                is_self = True
                try:
                    user_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    print('--get t_id error--')
                    print(e)
                    res = {'code':20410,'error':'No topic'}
                    return JsonResponse(res)
            else:
                #非博主访问当前博客
                try:
                    user_topic = Topic.objects.get(id=t_id,limit='public')
                except Exception as e:
                    res = {'code':20411,'error':'NO topic visitoe!'}
                    return JsonResponse(res)
            #生成具体返回值
            res = make_topic_res(user,user_topic,is_self)
            return JsonResponse(res)


        else:
            #列表页的需求
            category = request.GET.get('category')
            if category in ['tec','no-tec']:
                #按种类筛选
                if username == visitor_username:
                    #博主访问自己的博客
                    user_topics = Topic.objects.filter(author_id=username,category=category).order_by('-created_time')
                else:
                    #陌生访客访问他人博客，只返回公开权限的
                   user_topics = Topic.objects.filter(author_id=username,category=category,limit='public').order_by('-created_time')
            else:
                #全量不分种类筛选
                if username == visitor_username:
                    #博主访问自己的博客
                    user_topics = Topic.objects.filter(author_id=username).order_by('-created_time')
                else:
                    #陌生访客访问他人博客，只返回公开权限的
                    user_topics = Topic.objects.filter(author_id=username,limit='public').order_by('-created_time')
            res = make_topics_res(user,user_topics)
            return JsonResponse(res)

    if request.method == 'DELETE':
        #删除博客文章,真删除
        #请求中携带查询字符串 ?topic_id =3
        #响应 {'code':200}
        user = request.user
        if user.username != username:
            res = {'code': 20404, 'error': 'Thanks username is error'}
            return JsonResponse(res)
        #获取查询字符串
        topic_id = request.GET.get('topic_id')
        if not topic_id:
            res = {'code':20406,'error':'Must be give me topic_id!'}
            return JsonResponse(res)
        topic_id = int(topic_id)
        topics = Topic.objects.filter(id=topic_id)
        if not topics:
            res = {'code':20405,'error':'Topic is not exist!'}
            return JsonResponse(res)
        topic = topics[0]
        topic.delete()
        return JsonResponse({'code':200})


def make_topics_res(user,user_topics):
    #生成文章列表返回值
    res = {'code':200,'data':{}}
    res['data']['nickname'] = user.username
    res['data']['topics'] =[]
    for topic in user_topics:
        dic = {}
        dic['id'] = topic.id
        dic['title'] = topic.title
        dic['introduce'] = topic.introduce
        dic['category'] = topic.category
        dic['created_time'] =topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
        dic['author'] = user.nickname
        res['data']['topics'].append(dic)
    return res

def make_topic_res(user,user_topic,is_self):
    res = {'code': 200, 'data': {}}
    #获取上一篇文章的id和title
    if is_self:
        #博主自己访问
        #next_topic 大于当前文章id的第一个
        # 获取下一篇文章的id 和title
        next_topic = Topic.objects.filter(id__gt=user_topic.id, author=user.username).first()
        last_topic = Topic.objects.filter(id__lt=user_topic.id, author=user.username).last()

    else:
        #访客访问
        next_topic = Topic.objects.filter(id__gt=user_topic.id, author=user.username,limit='public').first()
        last_topic = Topic.objects.filter(id__lt=user_topic.id, author=user.username,limit='public').last()

    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None

    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title
    else:
        last_id = None
        last_title = None


    res['data']['next_id'] = next_id
    res['data']['next_title'] = next_title
    res['data']['last_id'] = last_id
    res['data']['last_title'] = last_title
    res['data']['title'] = user_topic.title
    res['data']['nickname'] = user.nickname
    res['data']['content'] = user_topic.content
    res['data']['introduce'] = user_topic.introduce
    res['data']['category'] = user_topic.category
    res['data']['created_time'] = user_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    res['data']['author'] = user.username
    #获取所有留言
    messages = Message.objects.filter(topic_id=user_topic.id).order_by('-created_time')
    m_count = 0
    #留言专属容器
    msg_list = []
    #回复专属容器
    reply_home = {}
    for message in messages:
        m_count += 1
        if message.parent_message:
            #回复
            reply_home.setdefault(message.parent_message,[])
            reply_home[message.parent_message].append({'msg_id':message.id,'content':message.content,
                                                       'publisher':message.publisher.nickname,
                                                       'publisher_avatar':str(message.publisher.avatar),
                                                       'created_time':message.created_time.strftime('%Y-%m-%d %H:%M:%S')})
        else:
            #留言
            msg_list.append({'id':message.id,'content':message.content,
                             'publisher':message.publisher.nickname,
                             'publisher_avatar':str(message.publisher.avatar),
                             'created_time':message.created_time.strftime('%Y-%m-%d %H:%M:%S'),'reply':[]})
    #关联 留言及回复
    for m in msg_list:
        if m['id'] in reply_home:
            m['reply'] = reply_home[m['id']]
    # 留言
    res['data']['messages'] = msg_list
    res['data']['messages_count'] = m_count
    return res



