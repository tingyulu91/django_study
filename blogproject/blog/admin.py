from django.contrib import admin
from .models import Post, Category, Tag

# Register your models here.
# 定制 Admin 后台
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']
# 在 Admin 后台注册模型
admin.site.register(Post, PostAdmin) #把新增的 PostAdmin 也注册进来
admin.site.register(Category)
admin.site.register(Tag)
