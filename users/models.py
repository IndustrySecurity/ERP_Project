from django.contrib.auth.models import AbstractUser
from django.db import models
from common.base import BaseModel

# 菜单模型
class Menu(BaseModel):
    name = models.CharField(max_length=100, verbose_name="菜单名称")
    link = models.CharField(max_length=200, verbose_name="菜单链接")

    def __str__(self):
        return self.name

# 角色模型
class Role(BaseModel):
    name = models.CharField(max_length=100, verbose_name="角色名称")
    description = models.TextField(blank=True, verbose_name="描述")
    menus = models.ManyToManyField(Menu, blank=True, related_name="roles", verbose_name="关联菜单")
    all_menus = models.BooleanField(default=False, verbose_name="拥有所有菜单权限")

    def has_all_menus(self):
        return self.all_menus

    def __str__(self):
        return self.name

# 自定义用户模型
class CustomUser(AbstractUser, BaseModel):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=False, verbose_name="角色")
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name="电子邮件")
    first_name = models.CharField(max_length=30, blank=True, verbose_name="名字")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="姓氏")

    REQUIRED_FIELDS = ['role']  # 额外必填字段

    def __str__(self):
        return self.username
