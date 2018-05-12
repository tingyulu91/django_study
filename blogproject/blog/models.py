from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import markdown
from django.utils.html import strip_tags

class Category(models.Model):   # 分类表格
    """
    Django 要求模型必须继承models.Model类
    Category 只需要一个简单的分类名 name 就可以了
    CharField 指定了分类名 name 的数据类型，CharField 是字符型
    CharField 的 max_length 参数指定其最大长度，超过这个长度的分类名就不能被存入数据库
    当然 Django 还为我们提供了多种其它的数据类型，如日期时间类型 DateTimeField、 整数类型 IntegerField 等等。
    Django 内置的全部类型可查看文档：
    https://docs.djangoproject.com/en/1.10/ref/models/fields/#field-types
    """
    name = models.CharField(max_length=100)
    # id列 Django会自动创建

    def __str__(self):
        return self.name


class Tag(models.Model):   # 标签表格
    """
    标签 Tag 也比较简单，和 Category 一样。
    再次强调一定要继承 models.Model 类！
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):   # 文章表格
    # 文章标题
    title = models.CharField(max_length=70)

    # 文章正文， 我们使用了 TextField
    # 存储比较短的字符串可以使用 CharField, 但对于文章的正文来说可能会是一大段文本，因此使用 TextField 来存储大段文本。
    body = models.TextField()


    # 文章摘要， 可以没有文章摘要， 但默认情况下 CharField 要求我们必须存入数据，否则就会报错
    # 指定 CharField 的 blank=True 参数值后就可以允许空值了。
    excerpt = models.CharField(max_length=200, blank=True)

    #若果没有填写摘要，把文章内容的前54个字符作为摘要。（复写模型的save方法）
    def save(self,*args,**kwargs):
        # 如果没有填写摘要
        if not self.excerpt:
            # 首先实例化一个 Markdown 类，用于渲染 body 的文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 先将Markdown文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本body摘取前54个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:54]
        # 调用父类的save方法将数据保存到数据库中
        super(Post, self).save(*args,**kwargs)


    # 这两个列分别表示文章的创建时间和最后一次修改时间，存储时间的字段用 DateTimeField 类型
    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()



    # 这是分类与标签，分类与标签的模型我们已经定义在上面。
    # 我们在这里把文章对应的数据库表和分类、标签对应的数据库表关联了起来，但是关联形式稍微有点不同。
    # 我们规定一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以我们使用的是ForeignKey，即一对多的关联关系。
    # 而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，所以我们使用ManyToManyField，表明这是多对多的关联关系
    # 同时我们规定文章可以没有标签，因此为标签 tags 指定了 blank=True。
    # For explanations of ForeignKey and ManyToManyField, see https://docs.djangoproject.com/en/1.10/topics/db/models/#relationships
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)

    # 文章作者，这里 User 是从 django.contrib.auth.models 导入的。
    # django.contrib.auth 是Django 内置的应用，专门用于处理网站用户的注册、登录等流程。 User 是 Django 为我们已经写好的用户模型。
    # 这里我们通过 ForeignKey 把文章和 User 关联了起来。
    # 因为我们规定一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此这是一对多的关联关系，和 Category 类似。
    author = models.ForeignKey(User)

    #views字段记录阅读量
    views = models.PositiveIntegerField(default=0) #此字段类型的值只允许为正整数或0，这里我们设置初始化为0.

    def __str__(self):
        return self.title

    # 自定义 get_absolute_url 方法
    # 记得从 django.urls 中导入 reverse 函数
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})
        # blog:detail 表示blog应用下的name=detail的函数


    # Meta内部类，通过指定一些属性来规定这个类该有的一些特性
    class Meta:
        ordering = ['-created_time'] #ordering 属性用来指定文章排序方式。列表中可以有多个项。

    # 给模型自定义一个方法：一旦用户访问了某篇文章，这时views的值就+1
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])#更新数据库中views字段的值，保存到数据库
























