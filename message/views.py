import json
from topic.models import Topic
from django.http import JsonResponse
from django.shortcuts import render
from tools.login_check import login_check
from message.models import Message
# Create your views here.


@login_check('POST')
def messages(request, topic_id):
    if request.method != 'POST':
        result = {'code': 401, 'error': 'please use POST'}
        return JsonResponse(result)
    # 发表留言/回复
    # 获取用户
    user = request.user
    json_str = request.body
    # loads -> python obj
    json_obj = json.loads(json_str)
    content = json_obj.get('content')
    if not content:
        result = {'code': 402, 'error': 'please give me content!'}
        return JsonResponse(result)
    parent_id = json_obj.get('parent_id', 0)

    try:
        topic = Topic.objects.get(id=topic_id)
    except:
        # topic被删除/当前topic_id不真实
        result = {'code': 403, 'error': 'no topic'}
        return JsonResponse(result)
    # 私有博客 只能博主留言
    if topic.limit == 'private':
        # 检查身份
        if user.username != topic.author.username:
            result = {'code': 404, 'error': 'please get out!'}
    # 创建留言数据
    Message.objects.create(content=content, publisher=user, topic=topic, parent_message=parent_id)
    return JsonResponse({'code': 200, 'data': {}})
