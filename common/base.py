from django.db import models
from django.conf import settings  # 引入 settings

class BaseModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 使用 AUTH_USER_MODEL
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
        verbose_name="创建人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 使用 AUTH_USER_MODEL
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
        verbose_name="更新人",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True
