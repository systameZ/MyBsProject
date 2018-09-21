from django import template

#这个标签直接使用会报错未注册
#在settings文件的template设置内的OPTIONS中添加以下内容即可
#'libraries': {
#                'mytag': 'user_more.templates.mytag',
#           }
register=template.Library()

@register.filter(name='add_class')
def add_class(in_tag,in_class):
    return in_tag.as_widget(attrs={'class':in_class,'required':'required'})