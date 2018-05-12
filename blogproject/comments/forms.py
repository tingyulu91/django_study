from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta: # 内部类 Meta, 用来指定一些和表单相关的东西
        model = Comment  #表明这个表单对应的数据库模型是Comment类
        fields = ['name', 'email', 'url', 'text'] # 指定了表单需要显示的字段