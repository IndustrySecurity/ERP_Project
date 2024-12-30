from django.db.models.signals import pre_save
from django.dispatch import receiver
from erp_project.middlewares import get_current_request
from .models import BaseModel  # 确保导入 BaseModel

@receiver(pre_save)
def set_user_fields(sender, instance, **kwargs):
    """
    自动设置 created_by 和 updated_by。
    """
    if not issubclass(sender, BaseModel):  # 仅处理继承自 BaseModel 的模型
        return

    request = get_current_request()
    if request and request.user.is_authenticated:
        if not instance.pk:  # 新建记录
            instance.created_by = request.user
        instance.updated_by = request.user  # 更新时总是设置
