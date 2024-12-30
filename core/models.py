from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

class BaseModel(models.Model):
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_created", verbose_name="创建人"
    )
    created_at = models.DateTimeField(null=True, blank=True, default=now, verbose_name="创建时间")
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_updated", verbose_name="更新人"
    )
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 指定为抽象模型，不会创建对应的数据库表
