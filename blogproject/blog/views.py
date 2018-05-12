from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post, Category, Tag
import markdown
from comments.forms import CommentForm
from django.views.generic import ListView, DetailView
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.db.models import Q #Q对象用于包装查询表达式，为了提供复杂的查询逻辑

def search(request):
    q = request.GET.get('q') # 获取用户提交的搜索关键词。（see base.html相应的input的name属性值）
                             # 用户通过表单 get方法提交的数据Django为我们保存在request.GET里，是一个类似于字典的对象
    error_msg = ''

    if not q:
        error_msg = "请输入关键词"
        return render(request, 'blog/index.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q)) # 前缀i表示不分大小写
    return render(request, 'blog/index.html', {'error_msg':error_msg,
                                             'post_list': post_list})


# Create your views here.
"""
def index(request):  # request为Django封装好的HTTP请求 （是类HttpRequest的一个实例）
   # return HttpResponse('欢迎访问我的博客首页！') #返回一个HTTP响应
    #return render(request, 'blog/index.html', context={
     #   'title': '我的博客首页',
      #  'welcome': '欢迎访问我的博客首页'
   # }
    post_list = Post.objects.all()
    return render(request, 'blog/index.html', context={
        'post_list': post_list
    })
"""

##将index视图函数改写为类视图

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 2

    #实现分页
    def get_context_data(self, **kwargs):
        """
        在视图函数中将模板变量传递给模板是通过给render函数的context参数传递一个字典实现的，
        例如 render(request,'blog/index.html',context={'post_list':post_list}),
        这里传递了一个{'post_list': post_list}字典给模板。
        在类视图中，这个需要传递的模板变量字典是通过get_context_data获得的，
        所以我们复写该方法，以便我们能够自己再插入一些我们自定义的模板变量进去。

        """
        #首先获得父类生成的传递给模板的字典
        context = super().get_context_data(**kwargs)

        # 父类生成的字典中已有 paginator、 page_obj、 is_paginated 这三个模板变量，
        # paginator 是 Paginator的一个实例
        # page_obj 是 Page 的一个实例
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        # 例如如果规定每页10个数据，而本身只有5个数据，其实就用不着分页，此时 is_paginated=False
        # 关于什么是Paginator, Page 类在 Django Pagination http://zmrenwu.com/post/34/ 简单分页中已有详细说明。
        # 由于context是一个字典，所以调用get方法从中取出某个键对应的值
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        #调用自己写的 pagination_data 方法获得显示分页导航条需要的数据，见下方。
        pagination_data =self.pagination_data(paginator,page,is_paginated)

        #将分页导航条的模板变量更新到context中，注意pagination_data方法返回的也是一个字典
        context.update(pagination_data)

        # 将更新后的context返回，以便ListView使用这个字典中的模板变量去渲染模板
        # 注意此时 context字典中已有了显示分页导航所需的数据。
        return context

    def pagination_data(self,paginator,page,is_paginated):
        if not is_paginated:
            # 如果没有分页，则无需显示分页导航条，不用任何分页导航条数据，因此返回一个空的字典

            return {}

        # 当前页左边连续的页码号，初始值为空
        left = []

        # 当前页右边连续的页码号，初始值为空
        right = []

        # 标示第1页页码后是否需要显示省略号
        left_has_more = False

        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False

        # 标示是否需要显示第1页的页码号
        # 因为如果当前页左边的连续页码号中已经含有第1页的页码号，此时就无需再显示第1页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为False
        first = False

        # 标示是否需要显示最后一页的页码号。
        # 需要此指示变量的理由和上面相同
        last = False

        # 获得用户当前请求的页码号
        page_number = page.number

        # 获得分页后的总页数
        total_pages = paginator.num_pages

        # 获得整个分页页码列表，比如分了四页，那么就是【1，2，3，4】
        page_range = paginator.page_range

        if page_number == 1:
            # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此left=[] （已默认为空）
            # 此时只要获取当前页右边的连续页码号，
            # 比如分页页码列表是 【1，2，3，4】，那么获取的就是 right=[2,3]。
            # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            right=page_range[page_number:page_number+2]

            # 如果最右边的页码号比最后一页的页码号减去1还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其他页码，因此需要显示省略号，通过right_has_more来指示。
            if right[-1] < total_pages-1:
                right_has_more = True

            # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码，
            # 所以需要显示最后一页的页码号，通过last来指示
            if right[-1] < total_pages:
                last = True
        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此right=[] （已默认为空），
            # 此时只要获取当前页左边的连续页码号
            # 比如分页页码列表是【1，2，3，4】，那么获取的就是left=[2,3]
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码
            left = page_range[(page_number-3) if (page_number-3) > 0 else 0: page_number-1]

            # 如果最左边的页码号比第2页页码号还大，
            # 说明最左边的页码号和第1页的页码号之间还有其他页码，因此需要显示省略号，通过left_has_more来指示
            if left[0] > 2:
                left_has_more = True

            # 如果最左边的页码号比第1页的页码号大，说明当前左边的连续页码好重不包含第一页的页码，
            # 所以需要显示第一页的页码号，通过first来指示
            if left[0] > 1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第一页，则需要获取当前页左右两边的连续页码号，
            # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number-3) if (page_number-3)>0 else 0: page_number-1]
            right = page_range[page_number:page_number+2]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages-1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第一页和第一页后的省略号
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }
        return data





"""
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk) # 当传入的pk对应的Post在数据库存在时，就返回对应的post,
                                          #  如果不存在，就个用户返回一个404错误，表明用户请求的文章不存在
    # 阅读量+1
    post.increase_views()

    post.body = markdown.markdown(post.body,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ])  # extra本身包含很多拓展，codehilite是语法高亮拓展，toc允许我们自动生成目录

    form = CommentForm()
    # 获取这篇 post 下的全部评论
    comment_list = post.comment_set.all()

    # 将文章、表单、以及文章下的评论列表作为模板变量传给 detail.html 模板，以便渲染相应数据
    context = {'post': post,
               'form': form,
               'comment_list': comment_list}

    return render(request, 'blog/detail.html', context = context)
"""

class PostDetailView(DetailView):
    #这些属性的含义和ListView 是一样的
    model = Post
    template_name ='blog/detail.html'
    context_object_name = 'post'

    def get(self,request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量+1
        # get方法返回的是一个HttpResponse实例
        # 之所以需要先调用父类的get方法，是因为只有当 get方法被调用后，
        # 才有 self.object属性，其值为Post模型实例，即被访问的文章 post
        response = super(PostDetailView,self).get(request,*args,**kwargs)

        #将文章阅读量+1
        #注意self.object的值就是被访问的文章 post
        self.object.increase_views()
        #视图必须返回一个HttpResponse对象
        return response

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对post的body值进行渲染
        post = super(PostDetailView, self).get_object(queryset=None)
        """post.body= markdown.markdown(post.body,
                                     extensions=[
                                         'markdown.extensions.extra',
                                         'markdown.extensions.codehilite', # 代码高亮拓展
                                         'markdown.extensions.toc', # 自动生成目录的拓展，
                                                                    # 这样在渲染Markdown文本时就可以在文中插入目录
                                     ])"""
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            #'markdown.extensions.toc',
            TocExtension(slugify=slugify),#处理标题的锚点值， slugify用于处理中文
        ])# 先实例化一个markdown.Markdown类
        post.body = md.convert(post.body) # 将post.body中的Markdown文本渲染成HTML文本。
                                          # 调用此方法后，md实例就多了一个toc属性，这个属性的值就是内容的目录
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):
        # 覆写 get_context_data的目的是因为除了将post传递给模板外 （DetailView已经帮我们完成），
        # 还要把评论表单、 post下的评论列表传递给模板
        context = super(PostDetailView,self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context








"""
def archives(request, year, month):
    post_list=Post.objects.filter(created_time__year = year,
                                  created_time__month = month)
    return render(request, 'blog/index.html', context={'post_list': post_list})
"""

##将Archives视图函数改写成类视图

class ArchivesView(IndexView):

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,
                                                               created_time__month=month
                                                            )


"""
def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category = cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
"""


##将Category视图函数改写为类视图


###class CategoryView(ListView):
   ### model = Post
    ###template_name = 'blog/index.html'
    ###context_object_name = 'post_list'



class CategoryView(IndexView):#此类中指定的属性值和IndexView中一样
    def get_queryset(self):  #覆写了父类的get_queryset方法（默认获取指定模型的全部列表数据）
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


class TagView(IndexView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)






















