from ..models import Post, Category, Tag
from django import template
from django.db.models.aggregates import Count

register = template.Library()  #实例化一个template.Library类

@register.simple_tag    #注册这个函数为模板标签，这样就能通过{% get_recent_posts %}语法在模板中调用这个函数
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-created_time')[:num]
    # 获取数据库中前 num 篇文章


@register.simple_tag
def archives():
    return Post.objects.dates('created_time', 'month', order='DESC')
    #dates方法返回一个列表，列表中每一个元素为每一篇文章（Post)的创建时间，且是Python的date对象，精确到月份，降序排列。

@register.simple_tag
def get_categories():
    # Count 计算分类下的文章数，其接受的参数为需要计数的模型的名称
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
            # 返回数据库中全部Category的记录，同时统计返回的Category记录的集合中每条记录下的文章数（Count)
            # 模型参数名Post(通过ForeignKey关联的）
            # 过滤掉num_posts值小于1的分类

@register.simple_tag
def get_tags():
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

