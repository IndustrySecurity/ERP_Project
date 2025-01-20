from django.db import models
from common.base import BaseModel
from master_data.models import Product, Customer
from users.models import CustomUser
from warehouse.models import WarehouseLocation
from django.utils import timezone
from django.db.models import Max

class SalesOrder(BaseModel):
    order_number = models.CharField(max_length=20, unique=True, verbose_name="订单编号")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="客户")
    salesperson = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="销售员")
    contract_number = models.CharField(max_length=255, blank=True, verbose_name="客户合同号")
    delivery_time = models.DateField(blank=True, null=True, verbose_name="交付时间")
    sales_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="销售金额", default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="已付金额", default=0)
    remarks = models.TextField(blank=True, null=True, verbose_name="备注")
    status = models.CharField(
        max_length=50,
        choices=(('pending', '待处理'), ('shipped', '已出库'), ('returned', '已退库'), ('partial', '部分出库')),
        default='pending',
        verbose_name="订单状态"
    )

    def save(self, *args, **kwargs):
        # 在第一次保存时生成唯一编号
        if not self.pk:  # 检查是否是新建记录
            super().save(*args, **kwargs)  # 先保存以生成主键
            self.order_number = f"SO-{self.pk:06d}"  # 基于主键生成唯一编号
            self.save(update_fields=['order_number'])  # 更新 order_number
        else:
            super().save(*args, **kwargs)  # 普通更新直接保存

    def __str__(self):
        return self.order_number



class SalesOrderItem(BaseModel):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, verbose_name="销售订单")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")

    def __str__(self):
        return f"{self.product.name} - {self.order.order_number}"

class SalesDelivery(BaseModel):
    delivery_number = models.CharField(max_length=255, unique=True, verbose_name="出库单编号")
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, verbose_name="销售订单")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, verbose_name="仓库位置")
    date = models.DateField(auto_now_add=True, verbose_name="出库日期")
    remarks = models.TextField(blank=True, verbose_name="备注")

    def save(self, *args, **kwargs):
            if not self.delivery_number:
                # 确保编号唯一性
                while True:
                    new_number = f"DEL-{timezone.now().strftime('%Y%m%d%H%M%S')}-{self.pk or ''}"
                    if not SalesDelivery.objects.filter(delivery_number=new_number).exists():
                        self.delivery_number = new_number
                        break
            super().save(*args, **kwargs)


    def __str__(self):
        return self.delivery_number
    
class SalesDeliveryItem(BaseModel):
    delivery = models.ForeignKey(SalesDelivery, on_delete=models.CASCADE, verbose_name="销售出库")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="出库数量")

    def __str__(self):
        return f"{self.product.name} - {self.delivery.delivery_number}"


class SalesReturn(BaseModel):
    return_number = models.CharField(max_length=255, unique=True, verbose_name="退库单编号")
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, verbose_name="销售订单")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="退货产品")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="退货数量")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, verbose_name="仓库位置")
    date = models.DateField(auto_now_add=True, verbose_name="退货日期")
    remarks = models.TextField(blank=True, verbose_name="备注")

    def save(self, *args, **kwargs):
        if not self.return_number:  # 如果未设置退库编号
            # 获取同一订单中现有退库记录的最大编号
            last_return = SalesReturn.objects.filter(order=self.order).aggregate(Max('id'))['id__max'] or 0
            self.return_number = f"RET-{self.order.id}-{last_return + 1:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.return_number
