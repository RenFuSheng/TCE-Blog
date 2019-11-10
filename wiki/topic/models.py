from django.db import models

# Create your models here.
from user.models import UserProfile


class Topic(models.Model):
    title = models.CharField(max_length=50,verbose_name='文章主题')
    #tec技术类文章 or no-tec 非技术类文章
    category = models.CharField(max_length=20,verbose_name='博客分类')
    #public 公开博客 or private 私有博客
    limit = models.CharField(max_length=10,verbose_name='文章权限')
    introduce = models.CharField(max_length=90,verbose_name='博客简介')
    content = models.TextField(verbose_name='博客内容')
    created_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    author = models.ForeignKey(UserProfile)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'topic'
        verbose_name = '文章'
        verbose_name_plural = verbose_name
