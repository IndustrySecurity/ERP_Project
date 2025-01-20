from django.db import models
from common.base import BaseModel
from master_data.models import Material, ProductionLine  
from sales.models import SalesOrder
from users.models import CustomUser
    
class ProductionOrder(models.Model):
    order_number = models.CharField(max_length=100, unique=True, verbose_name="工单编号")
    planned_start_time = models.DateTimeField(verbose_name="计划开工时间")
    planned_end_time = models.DateTimeField(verbose_name="计划完工时间")
    responsible_person = models.CharField(max_length=50, verbose_name="负责人")
    sales_order = models.ForeignKey(SalesOrder, unique=True, on_delete=models.CASCADE, verbose_name="销售订单")  # 外键，关联销售订单
    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, verbose_name="产线")  # 外键，关联产线
    remarks = models.TextField(blank=True, null=True, verbose_name="备注")  # 备注字段
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('material_collected', '已领料'),  # 代表已领料状态
        ('completed', '已完成'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")  # 状态字段

    class Meta:
        verbose_name = "生产工单"
        verbose_name_plural = "生产工单列表"
        ordering = ['planned_start_time']  # 默认按计划开工时间排序

    def save(self, *args, **kwargs):
        # 在第一次保存时生成唯一编号
        if not self.pk:  # 检查是否是新建记录
            super().save(*args, **kwargs)  # 先保存以生成主键
            self.order_number = f"PO-{self.pk:06d}"  # 基于主键生成唯一编号
            self.save(update_fields=['order_number'])  # 更新 order_number
        else:
            super().save(*args, **kwargs)  # 普通更新直接保存

    def __str__(self):
        return f"{self.order_number} - {self.responsible_person} - {self.planned_start_time}"
    
class MaterialRequisition(models.Model):
    materialrequisition_number = models.CharField(max_length=100, unique=True, verbose_name="领料单编号")
    production_order = models.OneToOneField(ProductionOrder, on_delete=models.CASCADE, verbose_name="生产工单")
    responsible_person = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default="", verbose_name="负责人")

    def save(self, *args, **kwargs):
        # 在第一次保存时生成唯一编号
        if not self.pk:  # 检查是否是新建记录
            super().save(*args, **kwargs)  # 先保存以生成主键
            self.materialrequisition_number = f"MR-{self.pk:06d}"  # 基于主键生成唯一编号
            self.save(update_fields=['materialrequisition_number'])  # 更新 materialrequisition_number
        else:
            super().save(*args, **kwargs)  # 普通更新直接保存

    def __str__(self):
        return f'领料单: {self.materialrequisition_number} - 生产工单: {self.production_order.order_number} - 负责人: {self.responsible_person.username}'

    class Meta:
        verbose_name = '领料单'
        verbose_name_plural = '领料单'


class ProductionMaterial(BaseModel):
    materialrequisition = models.ForeignKey(MaterialRequisition, on_delete=models.CASCADE, verbose_name="领料单")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="原材料")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")

    def __str__(self):
        return f"{self.material.name} in {self.recipe.product.name}"
    