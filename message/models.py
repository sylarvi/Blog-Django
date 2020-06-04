from django.db import models
from topic.models import Topic
from user.models import UserProfile


# Create your models here.


class Message(models.Model):
    content = models.CharField(max_length=50, verbose_name='内容')
    created_time = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic)
    publisher = models.ForeignKey(UserProfile)
    parent_message = models.IntegerField(default=0)

    class Meta:
        db_table = 'message'
