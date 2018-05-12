from django.conf.urls import url
from . import views

app_name = 'blog' #视图函数命名空间， 告诉Django这个URL模块是属于blog应用的
urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^$', views.IndexView.as_view(), name='index'),  #as_view()方法把IndexView类转换成一个函数

    #url(r'^post/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    url(r'^post/(?P<pk>[0-9]+)/$',views.PostDetailView.as_view(), name='detail'),
    #url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.archives, name='archives'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.ArchivesView.as_view(), name='archives'),

    #url(r'^category/(?P<pk>[0-9]+)/$', views.category, name='category')
    url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='category'),

    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagView.as_view(), name='tag'),
]
# 三个参数：网址（相对路径），处理函数，处理函数的别名