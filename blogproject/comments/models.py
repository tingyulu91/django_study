from django.db import models

# Create your models here.

class Comment(models.Model):
    name = models.CharField(max_length=100)  # 评论用户的名字
    email = models.EmailField(max_length=255) # 邮箱
    url = models.URLField(blank=True) # 个人网站
    text = models.TextField() # 内容
    created_time = models.DateTimeField(auto_now_add=True) # 评论时间，
    # auto_now_add： 当评论数据保存到数据库时，自动把created_time的值指定为当前时间

    post = models.ForeignKey('blog.Post') # 这个评论是关联到某篇文章（Post)的

    def __str__(self):
        return self.text[:20]
