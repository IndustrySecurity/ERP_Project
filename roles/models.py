from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=50, verbose_name="菜单名称")
    url = models.CharField(max_length=100, blank=True, null=True, verbose_name="菜单链接")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="菜单图标")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "菜单"
        verbose_name_plural = "菜单"


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="角色名称")
    description = models.TextField(blank=True, null=True, verbose_name="角色描述")
    menus = models.ManyToManyField(Menu, blank=True, related_name="roles", verbose_name="可访问菜单")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"
