from datetime import datetime, timedelta
import decimal
from django.db import transaction
from django.db.models import Sum
import json
import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

from finance.models import PaymentRecord, ReceiptRecord
from purchase.models import PurchaseOrder
from sales.models import SalesOrder

# 设置日志记录器
logger = logging.getLogger(__name__)

def finance_statistics(request):
    total_receivables = 0   # 应收
    total_payables = 0      # 应付
    total_receipts = 0      # 实收
    total_payments = 0      # 实付
    start_date = None
    end_date = None
    end_date_1 = None

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date_1 = request.POST.get('end_date')
        # 将 end_date 转换为日期对象，并加一天
        if end_date_1:
            end_date = datetime.strptime(end_date_1, "%Y-%m-%d") + timedelta(days=1)

        # 数据查询
        total_receipts = ReceiptRecord.objects.filter(created_at__range=[start_date, end_date]).aggregate(Sum('sales_order__paid_amount'))['sales_order__paid_amount__sum'] or 0
        total_receivables = ReceiptRecord.objects.filter(created_at__range=[start_date, end_date]).aggregate(Sum('sales_order__sales_amount'))['sales_order__sales_amount__sum'] or 0
        total_payments = PaymentRecord.objects.filter(created_at__range=[start_date, end_date]).aggregate(Sum('payment_amount'))['payment_amount__sum'] or 0
        total_payables = sum(record.purchase_order.total_price() for record in PaymentRecord.objects.filter(
            created_at__range=[start_date, end_date]
        ))

    return render(request, 'finance/statistics.html', {
        'total_receivables': total_receivables,
        'total_payables': total_payables,
        'total_receipts': total_receipts,
        'total_payments': total_payments,
        'start_date': start_date,
        'end_date': end_date_1,
    })

def payment_records(request):
    """显示付款记录列表，支持分页和查询"""
    query = request.GET.get('q', '').strip()

    # 获取所有付款记录，并按付款时间倒序排列
    records = PaymentRecord.objects.order_by('-created_at')
  
    if query:
        # 按付款编号、付款时间或其他相关字段进行查询
        records = records.filter(record_number__icontains=query) | \
                  records.filter(purchase_order__order_number__icontains=query)

    # 分页处理
    paginator = Paginator(records, 10)  # 每页显示 10 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 计算每个记录的 percentage
    for record in page_obj.object_list:
        if record.payment_amount > 0:  
            record.percentage = (record.payment_amount / record.purchase_order.total_price()) * 100
        else:
            record.percentage = 0  # 如果总金额为 0，设置为 0%

        record.remaining_percentage = 100 - record.percentage  # 计算未完成的百分比

    context = {
        'payment_records': page_obj.object_list,  # 当前页付款记录列表
        'page_obj': page_obj,  # 分页对象
        'paginator': paginator,  # 分页器
        'query': query,  # 搜索查询
    }
    return render(request, 'finance/payment_records.html', context)

def view_purchase_orders(request):
    """显示没有付款记录的采购订单列表"""
    purchase_orders = PurchaseOrder.objects.filter(paymentrecord__isnull=True)  # 直接过滤没有付款记录的订单
    
    orders_list = [{
            'id': order.id,
            'order_number': order.order_number,
            'supplier_name': order.supplier.name,  
            'status': order.status,
        } for order in purchase_orders]  # 将查询集转换为字典列表
    
    return JsonResponse({
        'success': True,
        'orders': orders_list,
    })


def payment_record_create(request):
    """创建付款记录"""
    if request.method == 'POST':
        try:
            # 从请求中提取数据
            purchase_order_id = request.POST.get('purchase_order')
            payment_amount = request.POST.get('payment_amount')

            logger.info(f"收到的采购订单ID: {purchase_order_id}, 付款金额: {payment_amount}")

            # 获取相关的采购订单
            order = get_object_or_404(PurchaseOrder, pk=purchase_order_id)

            with transaction.atomic():
                # 创建新的付款记录
                payment_record = PaymentRecord.objects.create(
                    purchase_order = order,
                    payment_amount = payment_amount
                )

                logger.info(f"Created payment record: {payment_record.record_number} for order: {order.order_number}")

            if decimal.Decimal(payment_amount) > order.total_price():
                return JsonResponse({'success': True, 'message': '付款记录创建成功！ 但付款金额高于总金额！！', 'payment_number': payment_record.record_number})
            else:
                return JsonResponse({'success': True, 'message': '付款记录创建成功！', 'payment_number': payment_record.record_number})

        except Exception as e:
            logger.error(f"Error creating payment record: {e}")
            return JsonResponse({'success': False, 'message': f"创建付款记录失败: {str(e)}"})

    return JsonResponse({'success': False, 'message': '无效请求'})

def delete_payment_record(request, id):
    """删除付款记录"""
    if request.method == 'DELETE':
        # 获取指定的付款记录
        payment_record = get_object_or_404(PaymentRecord, id=id)

        try:
            # 尝试删除记录
            payment_record.delete()
            logger.info(f"付款记录 {id} 删除成功")
            return JsonResponse({'success': True, 'message': '删除成功'})
        except Exception as e:
            logger.error(f"删除付款记录时出错: {e}")
            return JsonResponse({'success': False, 'message': '删除失败'})

    return JsonResponse({'success': False, 'message': '无效请求'}, status=400)

def view_payment_record(request, id):
    """查看付款记录"""
    # 获取指定的付款记录
    payment_record = get_object_or_404(PaymentRecord, id=id)
    
    # 返回付款记录的详细信息
    data = {
        'success': True,
        'record': {
            'id': payment_record.id,
            'purchase_order': {
                'id': payment_record.purchase_order.id,
                'number': payment_record.purchase_order.order_number,
                'total_price': payment_record.purchase_order.total_price(),  
            },
            'payment_amount': payment_record.payment_amount,
        }
    }
    return JsonResponse(data)

def edit_payment_record(request, id):
    """编辑付款记录"""
    if request.method == 'POST':
        # 获取并解析请求数据
        amount = request.POST.get('payment_amount')
        
        # 获取付款记录
        payment_record = get_object_or_404(PaymentRecord, id=id)

        # 更新字段
        payment_record.payment_amount += decimal.Decimal(amount)

        try:
            # 保存更新
            payment_record.save()
            logger.info(f"付款记录 {id} 更新成功")
            if payment_record.payment_amount > payment_record.purchase_order.total_price():
                return JsonResponse({'success': True, 'message': '更新成功，注意付款总金额大于应付金额！！'})
            else:
                return JsonResponse({'success': True, 'message': '更新成功'})
        except Exception as e:
            logger.error(f"更新付款记录时出错: {e}")
            return JsonResponse({'success': False, 'message': '更新失败'})

    return JsonResponse({'success': False, 'message': '无效请求'}, status=400)


def receipt_records(request):
    """显示收款记录列表，支持分页和查询"""
    query = request.GET.get('q', '').strip()
    records = ReceiptRecord.objects.order_by('-created_at')

    if query:
        records = records.filter(record_number__icontains=query) | \
                  records.filter(sales_order__order_number__icontains=query)

    # 分页处理
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 计算每个记录的百分比
    for record in page_obj.object_list:
        if record.sales_order.paid_amount > 0:
            record.percentage = (record.sales_order.paid_amount / record.sales_order.sales_amount) * 100
        else:
            record.percentage = 0.00

        record.remaining_percentage = 100 - record.percentage  # 计算未完成的百分比

    context = {
        'receipt_records': page_obj.object_list,  
        'page_obj': page_obj,
        'paginator': paginator,
        'query': query,
    }
    return render(request, 'finance/receipt_records.html', context)

def view_sales_orders(request):
    """显示没有收款记录的销售订单列表"""
    sales_orders = SalesOrder.objects.filter(receiptrecord__isnull=True)
    
    orders_list = [{
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': order.customer.name,
            'sales_amount': order.sales_amount,
            'status': order.status,
        } for order in sales_orders]
    
    return JsonResponse({'success': True, 'orders': orders_list})

def receipt_record_create(request):
    """创建收款记录"""
    if request.method == 'POST':
        try:
            sales_order_id = request.POST.get('sales_order')

            order = get_object_or_404(SalesOrder, pk=sales_order_id)
            order.paid_amount = request.POST.get('received_amount')
            order.save()
            receipt_record = ReceiptRecord.objects.create(
                sales_order=order
            )

            if decimal.Decimal(order.paid_amount) > decimal.Decimal(order.sales_amount):
                return JsonResponse({'success': True, 'message': '收款记录创建成功！注意已收金额大于销售额！！！', 'record_number': receipt_record.record_number})
            else:
                return JsonResponse({'success': True, 'message': '收款记录创建成功！', 'record_number': receipt_record.record_number})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"创建收款记录失败: {str(e)}"})

    return JsonResponse({'success': False, 'message': '无效请求'})

def delete_receipt_record(request, id):
    """删除收款记录"""
    if request.method == 'DELETE':
        receipt_record = get_object_or_404(ReceiptRecord, id=id)

        # 获取相关的销售订单
        sales_order = receipt_record.sales_order

        try:
            # 清零销售订单的已收金额并保存
            sales_order.paid_amount = 0  # set paid_amount to zero
            sales_order.save()

            receipt_record.delete()
            return JsonResponse({'success': True, 'message': '删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': '删除失败'})

    return JsonResponse({'success': False, 'message': '无效请求'}, status=400)

def view_receipt_record(request, id):
    """查看收款记录"""
    receipt_record = get_object_or_404(ReceiptRecord, id=id)
    
    data = {
        'success': True,
        'record': {
            'id': receipt_record.id,
            'sales_order': {
                'id': receipt_record.sales_order.id,
                'number': receipt_record.sales_order.order_number,
                'paid_amount': receipt_record.sales_order.paid_amount,
                'sales_amount': receipt_record.sales_order.sales_amount,
            },
        }
    }
    return JsonResponse(data)

def edit_receipt_record(request, id):
    """编辑收款记录"""
    if request.method == 'POST':
        payment_amount = request.POST.get('payment_amount')

        receipt_record = get_object_or_404(ReceiptRecord, id=id)
        order = receipt_record.sales_order
        order.paid_amount += decimal.Decimal(payment_amount)

        try:
            order.save()
            return JsonResponse({'success': True, 'message': '更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': '更新失败'})

    return JsonResponse({'success': False, 'message': '无效请求'}, status=400)
