from decimal import Decimal
import json
import logging
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseReceipt, PurchaseReturn
from django.core.paginator import Paginator
from warehouse.models import WarehouseLocation, MaterialStock
from master_data.models import Material, Supplier
from django.db.models import Q

logger = logging.getLogger(__name__)


def order_list(request):
    """显示采购订单列表，支持分页和查询"""
    query = request.GET.get('q', '').strip()

    # 按查询条件过滤订单，并按更新时间倒序排列
    orders = PurchaseOrder.objects.select_related('supplier') \
        .prefetch_related('purchaseorderitem_set__material') \
        .order_by('-updated_at')

    if query:
        orders = orders.filter(order_number__icontains=query) | orders.filter(supplier__name__icontains=query)

    # 分页处理
    paginator = Paginator(orders, 10)  # 每页显示 10 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj.object_list,  # 当前页订单列表
        'page_obj': page_obj,  # 分页对象
        'paginator': paginator,  # 分页器
        'query': query,  # 搜索查询
    }
    return render(request, 'purchase/order_list.html', context)


@csrf_exempt
def order_create(request):
    if request.method == 'POST':
        try:
            supplier_id = request.POST.get('supplier')
            materials = request.POST.getlist('materials[]')
            quantities = request.POST.getlist('quantities[]')

            logger.debug(f"Received supplier ID: {supplier_id}")
            logger.debug(f"Materials: {materials}, Quantities: {quantities}")

            supplier = get_object_or_404(Supplier, pk=supplier_id)
            with transaction.atomic():
                order = PurchaseOrder.objects.create(supplier=supplier)
                logger.info(f"Created order: {order.order_number}")

                if len(materials) != len(quantities):
                    raise ValueError("物料和数量不匹配")

                for material_id, quantity in zip(materials, quantities):
                    material = get_object_or_404(Material, pk=material_id)
                    logger.debug(f"Processing material: {material_id}, quantity: {quantity}")
                    PurchaseOrderItem.objects.create(
                        order=order,
                        material=material,
                        quantity=float(quantity),
                        unit_price=material.unit_price,
                    )
                logger.info(f"Order items created for order: {order.order_number}")

            return JsonResponse({'success': True, 'message': '订单创建成功！', 'order_number': order.order_number})
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return JsonResponse({'success': False, 'message': f"创建订单失败: {str(e)}"})

    return JsonResponse({'success': False, 'message': '无效请求'})

def order_view(request, pk):
    """查看采购订单"""
    order = get_object_or_404(PurchaseOrder, pk=pk)

    # 获取供应商和物料信息
    suppliers = Supplier.objects.all().values('id', 'name')
    materials = Material.objects.all().values('id', 'name', 'unit_price')

    # 获取订单的物料信息
    items = order.purchaseorderitem_set.all().values(
        'material__id', 'material__name', 'quantity', 'unit_price'
    )

    return JsonResponse({
        'success': True,
        'order': {
            'order_number': order.order_number,
            'supplier_id': order.supplier.id,
            'items': list(items),
        },
        'suppliers': list(suppliers),
        'materials': list(materials),
    })

def order_edit(request, pk):
    if request.method == "POST":
        try:
            # 获取订单对象
            order = get_object_or_404(PurchaseOrder, pk=pk)

            # 更新供应商
            supplier_id = request.POST.get("supplier")
            order.supplier = get_object_or_404(Supplier, id=supplier_id)
            order.save()

            # 清空旧的采购物料项
            order.purchaseorderitem_set.all().delete()

            # 获取物料相关数据
            material_ids = request.POST.getlist("materials[]")
            quantities = request.POST.getlist("quantities[]")
            unit_prices = request.POST.getlist("unit_prices[]")

            print("材料 ID: ", request.POST)

            # 检查长度是否一致
            if not (len(material_ids) == len(quantities) == len(unit_prices)):
                return JsonResponse({"success": False, "message": "物料数据不一致"})

            # 添加新的采购物料项
            for material_id, quantity, unit_price in zip(material_ids, quantities, unit_prices):
                material = get_object_or_404(Material, id=material_id)
                PurchaseOrderItem.objects.create(
                    order=order,
                    material=material,
                    quantity=quantity,
                    unit_price=unit_price,
                )

            return JsonResponse({"success": True, "message": "采购订单更新成功"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"更新失败: {str(e)}"})

    return JsonResponse({"success": False, "message": "仅支持 POST 请求"})



@csrf_exempt
def order_delete(request, pk):
    """删除采购订单"""
    order = get_object_or_404(PurchaseOrder, pk=pk)
    order.delete()
    return JsonResponse({'success': True, 'message': '订单删除成功'})


def receipt_list(request):
    """显示采购入库列表"""
    query = request.GET.get('q', '').strip()

    # 根据查询条件筛选入库记录
    if query:
        receipts = PurchaseReceipt.objects.select_related('order', 'order__supplier', 'location').filter(
            Q(receipt_number__icontains=query) |  # 入库单编号
            Q(order__order_number__icontains=query) |  # 订单编号
            Q(order__supplier__name__icontains=query)  # 供应商名称
        )
    else:
        # 如果没有查询条件，获取所有记录
        receipts = PurchaseReceipt.objects.select_related('order', 'order__supplier', 'location').all()

    # 分页处理
    paginator = Paginator(receipts, 10)  # 每页显示 10 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 获取相关数据：待处理订单和所有仓库位置
    orders = PurchaseOrder.objects.filter(status='pending')  # 只获取待处理状态的订单
    locations = WarehouseLocation.objects.all()  # 获取所有仓库位置

    context = {
        'receipts': page_obj.object_list,  # 当前页入库记录
        'page_obj': page_obj,             # 分页对象
        'query': query,                   # 搜索关键字
        'orders': orders,                 # 待处理订单
        'locations': locations,           # 仓库位置
    }

    return render(request, 'purchase/receipt_list.html', context)


@transaction.atomic
def receipt_create(request):
    if request.method == 'POST':
        try:
            # 获取请求数据
            order_id = request.POST.get('order')
            location_id = request.POST.get('location')
            remarks = request.POST.get('remarks', '').strip()
            material_ids = request.POST.getlist('material_ids[]')
            received_quantities = request.POST.getlist('received_quantities[]')

            # 验证订单和仓库位置
            order = get_object_or_404(PurchaseOrder, id=order_id)
            location = get_object_or_404(WarehouseLocation, id=location_id)

            # 创建入库单
            receipt = PurchaseReceipt.objects.create(
                receipt_number=f"REC-{PurchaseReceipt.objects.count() + 1:06d}",
                order=order,
                location=location,
                remarks=remarks
            )

            # 验证物料项
            if len(material_ids) != len(received_quantities):
                raise ValueError("物料项与入库数量不一致")

            for material_id, received_quantity in zip(material_ids, received_quantities):
                material = get_object_or_404(Material, id=material_id)
                received_quantity = Decimal(received_quantity)  # 转换为 Decimal 类型

                # 验证入库数量
                order_item = get_object_or_404(PurchaseOrderItem, order=order, material=material)
                if received_quantity > order_item.quantity:
                    raise ValueError(f"物料 {material.name} 入库数量不能大于采购数量")

                # 更新库存
                material_stock, created = MaterialStock.objects.get_or_create(
                    material=material,
                    location=location,
                    defaults={'quantity': Decimal('0')}  # 初始化库存为 Decimal 类型
                )
                material_stock.quantity += received_quantity  # 加法运算
                material_stock.save()

            # 更新订单状态
            order.status = 'received'
            order.save()

            return JsonResponse({'success': True, 'message': '入库成功'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})


def get_order_items(request, order_id):
    """获取采购订单中的物料项"""
    order = get_object_or_404(PurchaseOrder, pk=order_id)
    items = order.purchaseorderitem_set.all()
    results = [
        {
            'material_number': item.material.material_number,
            'id': item.id,
            'material_id': item.material.id,
            'material_name': item.material.name,
            'quantity': float(item.quantity),
        }
        for item in items
    ]
    return JsonResponse({'success': True, 'items': results})


def return_list(request):
    """显示采购退库列表，支持分页"""
    query = request.GET.get('q', '').strip()
    # 根据查询条件筛选退库记录
    if query:
        returns = PurchaseReturn.objects.select_related('order', 'material', 'location').filter(
            Q(return_number__icontains=query) |  # 退库单编号，假设字段名为 return_number
            Q(order__order_number__icontains=query)  # 订单编号
        )
    else:
        # 没有查询条件时，获取所有记录
        returns = PurchaseReturn.objects.select_related('order', 'material', 'location').all()

    paginator = Paginator(returns, 10)  # 每页显示10条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    orders = PurchaseOrder.objects.all()
    locations = WarehouseLocation.objects.all()
    return render(request, 'purchase/return_list.html', {
        'returns': page_obj.object_list,
        'page_obj': page_obj,
        'orders': orders,
        'locations': locations,
        'query': query,
    })

def get_order_materials(request, order_id):
    """获取指定订单的采购物料"""
    order = get_object_or_404(PurchaseOrder, pk=order_id)
    items = order.purchaseorderitem_set.select_related('material').all()
    results = [{'material_id': item.material.id, 'material_name': item.material.name} for item in items]
        
    # 输出debug信息
    print(f"Order ID: {order_id}")
    print(f"Order: {order}")
    print(f"Items: {items}")
    print(f"Results: {results}")
        
    return JsonResponse({'results': results})


def get_material_stock(request):
    """获取物料在指定仓库的库存数量"""
    material_id = request.GET.get('material_id')
    location_id = request.GET.get('location_id')
    material = get_object_or_404(Material, pk=material_id)
    location = get_object_or_404(WarehouseLocation, pk=location_id)

    stock = MaterialStock.objects.filter(material=material, location=location).first()
    quantity = stock.quantity if stock else 0
    return JsonResponse({'quantity': quantity})

@csrf_exempt
@transaction.atomic
def return_create(request):
    """创建采购退库"""
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order')
            material_id = request.POST.get('material')
            quantity = Decimal(request.POST.get('quantity', 0))
            location_id = request.POST.get('location')
            remarks = request.POST.get('remarks', '').strip()

            order = get_object_or_404(PurchaseOrder, pk=order_id)
            material = get_object_or_404(Material, pk=material_id)
            location = get_object_or_404(WarehouseLocation, pk=location_id)

            # 检查库存是否充足
            stock = MaterialStock.objects.filter(material=material, location=location).first()
            if not stock or stock.quantity < quantity:
                return JsonResponse({'success': False, 'message': f"库存不足: {material.name}"})

            # 创建退库记录
            return_entry = PurchaseReturn.objects.create(
                return_number=f"RET-{PurchaseReturn.objects.count() + 1:06d}",
                order=order,
                material=material,
                quantity=quantity,
                location=location,
                remarks=remarks,
                # created_by=request.user,  # 添加创建人
            )

            # 更新库存
            stock.quantity -= quantity
            stock.save()

            return JsonResponse({'success': True, 'message': f"退库单 {return_entry.return_number} 已创建"})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"创建失败: {str(e)}"})

    return JsonResponse({'success': False, 'message': '无效请求'})


@csrf_exempt
def return_delete(request, pk):
    """删除采购退库"""
    return_record = get_object_or_404(PurchaseReturn, pk=pk)
    return_record.delete()
    return JsonResponse({'success': True, 'message': '退库记录删除成功'})
