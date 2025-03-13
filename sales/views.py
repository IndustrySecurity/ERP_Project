from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SalesOrder, SalesOrderItem, SalesDelivery, SalesReturn, SalesDeliveryItem
from warehouse.models import ProductStock, WarehouseLocation
from master_data.models import Product, Customer, ProductCategory, Material, MaterialCategory
from users.models import CustomUser
from django.core.paginator import Paginator
from django.db.models import Q
import logging
import re
from decimal import Decimal
from django.db.models import Sum
from django.utils.timezone import localtime
from django.db import transaction

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

def order_list(request):
    customers = Customer.objects.all()
    users = CustomUser.objects.all()
    products = Product.objects.all()
    product_categories = ProductCategory.objects.all()
    materials = Material.objects.all()
    material_categories = MaterialCategory.objects.all()

    query = request.GET.get('q', '').strip()
    orders = SalesOrder.objects.all()

    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(created_by__username__icontains=query)
        )

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for order in orders:
        order.created_at_local = localtime(order.created_at)
        order.updated_at_local = localtime(order.updated_at)

    return render(request, 'sales/order_list.html', {
        'orders': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'customers': customers,
        'users': users,
        'products': products,
        'product_categories': product_categories,
        'materials': materials,
        'material_categories': material_categories,
    })



@csrf_exempt
def order_create(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(Customer, pk=customer_id)

        # 创建销售订单
        order = SalesOrder.objects.create(
            customer=customer,
            contract_number=request.POST.get('contract_number'),
            delivery_time=request.POST.get('delivery_time'),
            sales_amount=request.POST.get('sales_amount', 0),
            paid_amount=request.POST.get('paid_amount', 0),
            salesperson_id=request.POST.get('salesperson')
        )

        # 获取订单项数据
        items = request.POST.dict()  # 获取所有数据
        grouped_items = {}

        for key, value in items.items():
            if key.startswith('items['):  # 只处理 items[...] 开头的键
                match = re.match(r'items\[(\d+)\]\[(\w+)\]', key)
                if match:
                    index, field = match.groups()
                    grouped_items.setdefault(index, {})[field] = value

        logging.debug(f"Grouped items: {grouped_items}")

        # 保存订单项到数据库
        for _, item_data in grouped_items.items():
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity')
            unit_price = item_data.get('unit_price')

            # 校验数据
            if product_id and quantity and unit_price:
                SalesOrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=unit_price
                )

        # 重定向到订单列表页面
        return redirect('sales:order_list')
    return redirect('sales:order_list')



@csrf_exempt
def order_delete(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(SalesOrder, pk=order_id)
        order.delete()
        return JsonResponse({'success': True, 'message': '订单已删除'})
    return JsonResponse({'success': False, 'message': '无效请求'})

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SalesOrder, SalesOrderItem

@csrf_exempt
def order_edit(request, order_id):
    if request.method == 'GET':
        # 获取订单详情
        order = get_object_or_404(SalesOrder, pk=order_id)
        items = order.salesorderitem_set.all()

        return JsonResponse({
            'success': True,
            'customer_id': order.customer.id,
            'salesperson_id': order.salesperson.id,
            'contract_number': order.contract_number,
            'delivery_time': order.delivery_time.strftime('%Y-%m-%d'),
            'sales_amount': str(order.sales_amount),
            'remarks': order.remarks,
            'items': [
                {
                    'id': item.id,
                    'product_id': item.product.id,
                    'quantity': str(item.quantity),
                    'unit_price': str(item.unit_price)
                }
                for item in items
            ]
        })

    elif request.method == 'POST':
        # 解析并保存订单的基本信息
        order = get_object_or_404(SalesOrder, pk=order_id)
        order.customer_id = request.POST.get('customer')
        order.salesperson_id = request.POST.get('salesperson')
        order.contract_number = request.POST.get('contract_number')
        order.delivery_time = request.POST.get('delivery_time')
        order.sales_amount = request.POST.get('sales_amount')
        order.remarks = request.POST.get('remarks', '')
        order.save()

        # 更新订单项
        # 删除旧的订单项
        order.salesorderitem_set.all().delete()

        # 解析新的订单项
        items = []
        for key, value in request.POST.items():
            if key.startswith('items[') and key.endswith(']'):
                parts = key.split('][')
                index = parts[0][6:]
                field = parts[1][:-1]
                if len(items) <= int(index):
                    items.append({})
                items[int(index)][field] = value

        # 保存新的订单项
        for item in items:
            SalesOrderItem.objects.create(
                order=order,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            )

        # 返回订单列表页面
        return redirect('sales:order_list')






def delivery_list(request):
    deliveries = SalesDelivery.objects.select_related('order', 'location', 'created_by', 'updated_by').all()
    # 筛选状态为 'pending' 或 'partial' 的订单
    orders = SalesOrder.objects.filter(status__in=['pending', 'partial'])
    locations = WarehouseLocation.objects.all()

    query = request.GET.get('q', '').strip()
    if query:
        # 根据出库单编号、订单编号或备注进行筛选
        deliveries = deliveries.filter(
            Q(delivery_number__icontains=query) |     
            Q(order__order_number__icontains=query) |  
            Q(remarks__icontains=query)                   
        )
    
    paginator = Paginator(deliveries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'sales/delivery_list.html', {
        'deliveries': page_obj.object_list,
        'page_obj': page_obj,
        'orders': orders,
        'locations': locations,
    })


@csrf_exempt
def delivery_create(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                order_id = request.POST.get('order')
                location_id = request.POST.get('location')
                remarks = request.POST.get('remarks', '')

                order = get_object_or_404(SalesOrder, pk=order_id)
                location = get_object_or_404(WarehouseLocation, pk=location_id)

                # 创建出库单
                delivery = SalesDelivery.objects.create(order=order, location=location, remarks=remarks)

                # 更新库存并记录出库项
                items = request.POST.dict()

                # 计算已有的出库数量
                total_outgoing = sum(item['quantity'] for item in SalesDeliveryItem.objects.filter(delivery__order=order).values('quantity'))

                total_order = 0
                print(items)
                for key, value in items.items():
                    if key.startswith('items') and '[quantity]' in key:
                        product_id = int(key.split('[')[1].split(']')[0])
                        quantity = Decimal(value)
                        
                        # 获取订单项和计算总订单数量
                        order_item = SalesOrderItem.objects.get(order=order, product_id=product_id)
                        total_order += order_item.quantity
                        
                        # 检查库存
                        try:
                            stock = ProductStock.objects.get(location=location, product_id=product_id)
                            if stock.quantity < quantity:
                                return JsonResponse({'success': False, 'message': f'库存不足，产品ID {product_id}'})
                        except ProductStock.DoesNotExist:
                            return JsonResponse({'success': False, 'message': f'库存记录未找到，产品ID {product_id}'})

                        # 减少库存并保存
                        stock.quantity -= quantity
                        stock.save()

                        # 创建出库记录
                        SalesDeliveryItem.objects.create(
                            delivery=delivery,
                            product_id=product_id,
                            quantity=quantity
                        )

                        total_outgoing += quantity

                # 更新销售订单状态
                if total_outgoing >= total_order:
                    order.status = 'shipped'  # 全部出库
                else:
                    order.status = 'partial'  # 部分出库
                order.save()
                if total_outgoing > total_order:
                    return JsonResponse({'success': True, 'message': '出库创建成功!注意总出库产品数量大于订单项！！'})
                else:
                    return JsonResponse({'success': True, 'message': '出库创建成功'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': '仅支持POST请求'})



def get_stock_quantity(request, location_id, product_id):
    """获取仓库中产品的库存数量"""
    try:
        product_stock = ProductStock.objects.get(location_id=location_id, product_id=product_id)
        return JsonResponse({'stock_quantity': float(product_stock.quantity)})
    except ProductStock.DoesNotExist:
        return JsonResponse({'stock_quantity': 0})




def get_order_items(request, order_id):
    """获取销售订单的产品信息"""
    order = get_object_or_404(SalesOrder, pk=order_id)
    items = order.salesorderitem_set.select_related('product').all()
    
    results = []

    # 遍历订单项并填充结果
    for item in items:
        # 获取产品ID和产品名称
        product_id = item.product.id
        product_name = item.product.name
        quantity = item.quantity
        
        # 计算该产品的已出库数量
        outgoing_items = SalesDeliveryItem.objects.filter(delivery__order=order, product_id=product_id).aggregate(total=Sum('quantity'))
        outgoing_quantity = outgoing_items['total'] if outgoing_items['total'] else 0  # 若没有出库，则为0

        results.append({
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
            'outgoing_quantity': outgoing_quantity  # 添加已出库数量
        })

    return JsonResponse({'results': results})


def return_list(request):
    """显示销售退库列表"""
    query = request.GET.get('q', '').strip()
    returns = SalesReturn.objects.select_related('order', 'product', 'location', 'created_by').all()

    # 搜索功能
    if query:
        returns = returns.filter(
            Q(return_number__icontains=query) |
            Q(order__order_number__icontains=query) |
            Q(product__name__icontains=query) |
            Q(remarks__icontains=query)
        )

    paginator = Paginator(returns, 10)  # 每页显示10条记录
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 初始化订单和仓库位置数据
    orders = SalesOrder.objects.all()
    locations = WarehouseLocation.objects.all()

    return render(request, 'sales/return_list.html', {
        'returns': page_obj.object_list,
        'page_obj': page_obj,
        'orders': orders,
        'locations': locations,
    })



def get_order_products(request, order_id):
    """获取销售订单的产品信息"""
    order = get_object_or_404(SalesOrder, pk=order_id)
    items = order.salesorderitem_set.select_related('product').all()
    results = [{'product_id': item.product.id, 'product_name': item.product.name, 'quantity': item.quantity} for item in items]
    return JsonResponse({'success': True,'results': results})


@csrf_exempt
def return_create(request):
    """创建销售退库"""
    if request.method == 'POST':
        try:
            logger.debug("收到 POST 请求: %s", request.POST)

            order_id = request.POST.get('order')
            location_id = request.POST.get('location')
            product_ids = request.POST.getlist('product_ids[]')
            quantities = request.POST.getlist('quantities[]')
            remarks = request.POST.get('remarks', '')

            # 检查必填参数
            if not order_id or not location_id or not product_ids or not quantities:
                logger.error("缺少必填参数: order_id=%s, location_id=%s, product_ids=%s, quantities=%s", order_id, location_id, product_ids, quantities)
                return JsonResponse({'success': False, 'message': '缺少必填参数'})

            order = get_object_or_404(SalesOrder, pk=order_id)
            location = get_object_or_404(WarehouseLocation, pk=location_id)
            logger.debug("订单和仓库位置获取成功: order_id=%s, location_id=%s", order.id, location.id)

            for product_id, quantity in zip(product_ids, quantities):
                product = get_object_or_404(Product, pk=product_id)
                quantity = Decimal(quantity)
                logger.debug("处理产品: product_id=%s, quantity=%s", product.id, quantity)

                # 检查或创建库存记录
                product_stock, created = ProductStock.objects.get_or_create(
                    product=product,
                    location=location,
                    defaults={'quantity': 0}
                )
                if created:
                    logger.info("创建新的库存记录: product_stock_id=%s, initial_quantity=0", product_stock.id)
                else:
                    logger.debug("库存记录已存在: product_stock_id=%s, current_quantity=%s", product_stock.id, product_stock.quantity)

                # 更新库存
                product_stock.quantity += quantity
                product_stock.save()
                logger.debug("库存更新成功: product_stock_id=%s, new_quantity=%s", product_stock.id, product_stock.quantity)

                # 创建退库记录
                return_record = SalesReturn.objects.create(
                    order=order,
                    product=product,
                    location=location,
                    quantity=quantity,
                    remarks=remarks,
                    created_by=request.user,  # 需要确保用户登录
                )
                logger.debug("退库记录创建成功: return_id=%s, return_number=%s", return_record.id, return_record.return_number)

            return JsonResponse({'success': True, 'message': '退库创建成功'})

        except Exception as e:
            logger.exception("退库创建失败")
            return JsonResponse({'success': False, 'message': f'发生错误: {str(e)}'})

    logger.warning("非 POST 请求")
    return JsonResponse({'success': False, 'message': 'Invalid request'})




def order_details(request, order_id):
    order = get_object_or_404(SalesOrder, pk=order_id)
    items = order.salesorderitem_set.select_related('product').all()

    # 获取每个产品的配方详情
    detailed_items = []
    for item in items:
        product = item.product
        recipe = product.recipe if hasattr(product, 'recipe') else None
        materials = []
        if recipe:
            materials = [
                {
                    'material_name': rm.material.name,
                    'material_category': rm.material.category.name if rm.material.category else '无',
                    'quantity': float(rm.quantity),
                }
                for rm in recipe.recipematerial_set.select_related('material')
            ]
        detailed_items.append({
            'product_name': product.name,
            'quantity': float(item.quantity),
            'unit_price': float(item.unit_price),
            'recipe': materials,
        })

    response_data = {
        'order_number': order.order_number,
        'customer_name': order.customer.name,
        'salesperson_name': order.salesperson.username if order.salesperson else '无',
        'delivery_time': order.delivery_time.strftime('%Y-%m-%d'),
        'sales_amount': float(order.sales_amount),
        'remarks': order.remarks,
        'items': detailed_items,
    }

    return JsonResponse({'success': True, 'order': response_data})