from django import forms
from .models import Role

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('name', 'description', 'menus')
        labels = {
            'name': '角色名称',
            'description': '角色描述',
            'menus': '可访问菜单',
        }
        help_texts = {
            'name': '角色名称必须唯一且不超过50个字符。',
            'menus': '请选择该角色可以访问的菜单项。',
        }
        error_messages = {
            'name': {
                'required': '角色名称是必填项。',
                'unique': '该角色名称已被使用。',
                'max_length': '角色名称不能超过50个字符。',
            },
            'menus': {
                'required': '请选择至少一个菜单。',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
