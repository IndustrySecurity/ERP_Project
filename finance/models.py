from django.db import models
from common.base import BaseModel
from purchase.models import PurchaseOrder
from sales.models import SalesOrder  

class PaymentRecord(BaseModel):
    record_number = models.CharField(max_length=255, unique=True, verbose_name="付款记录编号")
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, verbose_name="采购订单")
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="付款金额")

    class Meta:
        verbose_name = "付款记录"
        verbose_name_plural = "付款记录列表"
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for {self.purchase_order} - {self.payment_amount}"
    
    def save(self, *args, **kwargs):
        # 确保 record_number 唯一
        if not self.pk and not self.record_number:  # 仅在新建时生成
            prefix = "AP"
            # 查询最新的订单编号后递增
            last_record = PaymentRecord.objects.order_by('-id').first()
            next_id = (last_record.id + 1) if last_record else 1
            self.record_number = f"{prefix}-{next_id:06d}"
        super().save(*args, **kwargs)

class ReceiptRecord(BaseModel):
    record_number = models.CharField(max_length=255, unique=True, verbose_name="收款记录编号")
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, verbose_name="销售订单")

    class Meta:
        verbose_name = "收款记录"
        verbose_name_plural = "收款记录列表"
        ordering = ['created_at']

    def __str__(self):
        return f"Receipt for {self.sales_order} - {self.receipt_amount}"

    def save(self, *args, **kwargs):
        # 确保 record_number 唯一
        if not self.pk and not self.record_number:  # 仅在新建时生成
            prefix = "AR"  # 收款记录编号前缀
            # 查询最新的编号并递增
            last_record = ReceiptRecord.objects.order_by('-id').first()
            next_id = (last_record.id + 1) if last_record else 1
            self.record_number = f"{prefix}-{next_id:06d}"
        super().save(*args, **kwargs)