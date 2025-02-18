import datetime
from decimal import Decimal
import json
from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import transaction
from django.views import View
from django.db.models import Q

from warehouse.models import MaterialStock, ProductStock, WarehouseLocation
from .models import MaterialRequisition, ProductionMaterial, ProductionOrder, ProductionOrderItem, WarehousedProduct
from master_data.models import Material, ProductionLine, Recipe, RecipeMaterial  
from django.core.paginator import Paginator
from sales.models import SalesOrder,SalesOrderItem
from users.models import CustomUser
import logging

logger = logging.getLogger(__name__)

def production_order_list(request):
    """显示生产工单列表，支持分页和查询"""
    query = request.GET.get('q', '').strip() if 'q' in request.GET else None

    # 按查询条件过滤工单，并按计划开工时间倒序排列
    orders = ProductionOrder.objects.select_related('sales_order', 'production_line') \
        .order_by('-planned_start_time')

    if query:
        # 按工单编号、销售订单编号或产线名称进行查询
        orders = orders.filter(order_number__icontains=query) | \
                 orders.filter(sales_order__order_number__icontains=query)
    
    sales_orders = SalesOrder.objects.filter(status='pending')
    users = CustomUser.objects.all()
    production_lines = ProductionLine.objects.all()
 
    # 分页处理
    paginator = Paginator(orders, 10)  # 每页显示 10 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj.object_list,  # 当前页工单列表
        'page_obj': page_obj,  # 分页对象
        'paginator': paginator,  # 分页器
        'query': query,  # 搜索查询
        'sales_orders': sales_orders,
        'users': users,
        'production_lines': production_lines
    }
    return render(request, 'production/production_order_list.html', context)

def production_order_create(request):
    if request.method == 'POST':
        try:
            sales_order_id = request.POST.get('sales_order')
            production_line_id = request.POST.get('production_line')
            planned_start_time = request.POST.get('planned_start_time')
            planned_end_time = request.POST.get('planned_end_time')
            products = request.POST.getlist('product_ids[]')
            production_quantities = request.POST.getlist('production_quantities[]')
            remarks = request.POST.get('remarks', '')  # 获取备注信息
            status = 'pending'  # 默认状态为待处理

            logger.debug(f"Sales Order ID: {sales_order_id}, Production Line ID: {production_line_id}")
            
            # 获取相关对象
            sales_order = get_object_or_404(SalesOrder, pk=sales_order_id)
            production_line = get_object_or_404(ProductionLine, pk=production_line_id)

            sales_order_items = SalesOrderItem.objects.filter(order=sales_order)
            if not sales_order_items:
                return JsonResponse({'success': False, 'message': '该订单没有订单项，无法创建工单！'})
            # 时间格式转换
            planned_start_time_dt = datetime.datetime.strptime(planned_start_time, '%Y-%m-%d')
            planned_end_time_dt = datetime.datetime.strptime(planned_end_time, '%Y-%m-%d')

            # 判断开始时间是否早于结束时间
            if planned_start_time_dt > planned_end_time_dt:
                return JsonResponse({'success': False, 'message': '开始时间必须早于结束时间。'})
            
            with transaction.atomic():
                # 创建生产工单，负责人设置为当前用户
                order = ProductionOrder.objects.create(
                    sales_order=sales_order,
                    production_line=production_line,
                    planned_start_time=planned_start_time,
                    planned_end_time=planned_end_time,
                    responsible_person=request.user.username,  # 负责人为当前操作的用户
                    remarks=remarks,
                    status=status  # 设置默认状态
                )
                logger.info(f"Created production order: {order.order_number}")
            
            for product,quantity in zip(products,production_quantities):
                ProductionOrderItem.objects.create(
                    production_order=order,
                    product_id=product,
                    quantity=quantity
                )
            if sales_order.delivery_time < planned_end_time_dt.date():
                return JsonResponse({'success': True, 'message': '生产工单创建成功！', 'warning': 'warning:计划完成时间晚于订单交付时间！！！', 'order_number': order.order_number})
            return JsonResponse({'success': True, 'message': '生产工单创建成功！', 'order_number': order.order_number})
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                logger.error(f"Error creating production order: {e}")
                return JsonResponse({'success': False, 'message': "该销售订单订单已创建工单。"})
            logger.error(f"Error creating production order: {e}")
            return JsonResponse({'success': False, 'message': f"创建生产工单失败: {str(e)}"})

    return JsonResponse({'success': False, 'message': '无效请求'})

def view_order(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)  # 获取指定 ID 的工单
    if order.status in ("completed", "material_collected"):
        return JsonResponse({'success': False, 'message': '已领料/已完成的工单无法更改！'})
    # 获取与该工单相关的所有生产项
    order_items = ProductionOrderItem.objects.filter(production_order=order)
    sales_order_items = SalesOrderItem.objects.filter(order=order.sales_order)

    # 创建一个字典来存储销售订单项，根据产品 ID 作为键
    sales_order_dict = {item.product.id: item for item in sales_order_items}

    # 将生产项数据格式化为字典列表
    order_items_data = [
        {
            'product_id': item.product.id,  # 产品 ID
            'product_name': item.product.name,  # 产品名
            'quantity': float(item.quantity),  # 数量
            'demand_quantity': float(sales_order_dict.get(item.product.id, {}).quantity)  # 获取需求数量
        }
        for item in order_items
    ]
    data = {
        'success': True,
        'order': {
            'order_number': order.order_number,
            'sales_order': order.sales_order.id,
            'production_line': order.production_line.id,
            'planned_start_time': order.planned_start_time.isoformat(),
            'planned_end_time': order.planned_end_time.isoformat(),
            'responsible_person': order.responsible_person,
            'remarks': order.remarks,  
            'order_items': order_items_data,  # 添加生产项
        },
    }
    return JsonResponse(data)

def production_order_edit(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)  # 获取要编辑的生产工单
    if request.method == 'POST':
        try:
            # 从 POST 请求中获取数据
            sales_order_id = request.POST.get('sales_order')
            production_line_id = request.POST.get('production_line')
            planned_start_time = request.POST.get('planned_start_time')
            planned_end_time = request.POST.get('planned_end_time')
            products = request.POST.getlist('product_ids[]')
            production_quantities = request.POST.getlist('production_quantities[]')
            remarks = request.POST.get('remarks', '')  # 获取备注信息            

            # 时间格式转换
            planned_start_time_dt = datetime.datetime.strptime(planned_start_time, '%Y-%m-%d')
            planned_end_time_dt = datetime.datetime.strptime(planned_end_time, '%Y-%m-%d')

            # 判断开始时间是否早于结束时间
            if planned_start_time_dt > planned_end_time_dt:
                return JsonResponse({'success': False, 'message': '开始时间必须早于结束时间。'})
            print(products)
            print(production_quantities)
            for product,quantity in zip(products,production_quantities):
                production_order_item = ProductionOrderItem.objects.filter(production_order=order,product_id=product).first()
                production_order_item.quantity = quantity
                production_order_item.save()

            # 更新生产工单的字段
            order.sales_order_id = sales_order_id  # 确保 sales_order_id 是有效的 ID
            order.production_line_id = production_line_id  # 确保 production_line_id 是有效的 ID
            order.planned_start_time = planned_start_time
            order.planned_end_time = planned_end_time
            order.remarks = remarks

            # 保存修改后的生产工单
            order.save()

            return JsonResponse({"success": True, "message": "生产订单更新成功"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"更新失败: {str(e)}"})

    return JsonResponse({"success": False, "message": "仅支持 POST 请求"})


def production_order_delete(request, pk):
    order = get_object_or_404(ProductionOrder, pk=pk)
    order.delete()
    return JsonResponse({"success": True, "message": "生产工单已成功删除。"})


def material_requisition_list(request):
    """ 领料单列表视图 """
    query = request.GET.get('q', '').strip()
    
    # 根据查询条件过滤领料单
    if query:
        requisitions = MaterialRequisition.objects.filter(production_order__order_number__icontains=query)
    else:
        requisitions = MaterialRequisition.objects.all()
    
    paginator = Paginator(requisitions, 10)  # 每页显示 10 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 获取所有生产工单
    production_orders = ProductionOrder.objects.filter(status="pending")
    users = CustomUser.objects.all()

    context = {
        'requisitions': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'production_orders': production_orders,  # 将生产工单数据传递给模板
        'users': users,
    }
    return render(request, 'production/material_requisition_list.html', context)

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import MaterialRequisition, ProductionOrder, ProductionMaterial, Material, SalesOrder

def get_materials(request,pk):
    if request.method == 'GET':
        production_order_id = pk

        if not production_order_id:
            return JsonResponse({'success': False, 'message': '请选择生产工单'})

        try:
            # 获取生产工单
            production_order = get_object_or_404(ProductionOrder, id=production_order_id)
            items = ProductionOrderItem.objects.filter(production_order=production_order)
            row_material_warehouse_location = WarehouseLocation.objects.filter(name = '原材料仓库').first()
            production_line_warehouse_location = WarehouseLocation.objects.filter(name = '产线仓库').first()
            # 初始化所需材料列表
            required_materials = []
            for item in items:
                # 获取产品配方
                product = item.product
                recipe = Recipe.objects.filter(product=product).first()
                
                if recipe:
                    recipematerials = RecipeMaterial.objects.filter(recipe=recipe)
                    
                    for material in recipematerials:  # 获取配方中的每种材料
                        material_id = material.material.id
                        material_name = material.material.name
                        material_quantity = material.quantity * item.quantity  # 根据销售订单项的数量计算所需的总数量
                        # 获取原材料仓库的库存
                        raw_material_stock = MaterialStock.objects.filter(material=material.material, location=row_material_warehouse_location).first()
                        if raw_material_stock is None:
                            raw_material_quantity = 0
                        else:
                            raw_material_quantity = raw_material_stock.quantity

                        # 获取产线仓库的库存
                        production_line_stock = MaterialStock.objects.filter(material=material.material, location=production_line_warehouse_location).first()
                        if production_line_stock is None:
                            production_line_quantity = 0
                        else:
                            production_line_quantity = production_line_stock.quantity    

                        # 查找是否已经存在该材料
                        existing_material = next((m for m in required_materials if m['material_id'] == material_id), None)
                        
                        if existing_material:
                            # 如果已存在，增加数量
                            existing_material['quantity'] += material_quantity
                        else:
                            # 否则，添加新材料
                            required_materials.append({
                                'material_id': material_id,
                                'material_name': material_name,
                                'quantity': material_quantity,
                                'raw_material_quantity': raw_material_quantity,
                                'production_line_quantity': production_line_quantity,
                            })
                else:
                    return JsonResponse({'success': False, 'message': f'产品"{product.name}"没有配方！请添加配方后重试。'})
            return JsonResponse({
                        'success': True,
                        'production_order_id': production_order.id,
                        'required_materials': required_materials,
                    })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'处理失败: {str(e)}'})  # 捕获其他异常并返回错误信息

    return JsonResponse({'success': False, 'message': '仅支持 GET 请求'})


def material_requisition_create(request):
    # 获取表单中的数据
    production_order_id = request.POST.get('production_order')
    user_id = request.POST.get('responsible_person')
    responsible_person = CustomUser.objects.filter(id=user_id).first()
    materials = request.POST.getlist('materials')  # 获取所有材料的 ID 列表
    quantities = request.POST.getlist('quantities')  # 获取所有材料的数量列表

    # 创建一个新的领料单
    materialrequisition = MaterialRequisition.objects.create(production_order_id=production_order_id, responsible_person = responsible_person)

    # 循环处理每种材料和数量
    for material_id, quantity in zip(materials, quantities):
        # 检查 material_id 是否是以 "MAT" 开头的字符串
        if isinstance(material_id, str) and material_id.startswith("MAT"):
            # 根据 material_number 查找
            material = Material.objects.filter(material_number=material_id).first()
        else:
            # 假设 material_id 是整数或其他类型的 id，直接按 id 查找
            material = Material.objects.filter(id=material_id).first()
    
        if material:
            # 创建与领料单关联的材料项
            ProductionMaterial.objects.create(materialrequisition=materialrequisition, material=material, quantity=quantity)
    
    production_order = ProductionOrder.objects.filter(id=production_order_id).first()
    production_order.status = 'material_collected'
    production_order.save()

    # 返回成功信息
    return JsonResponse({'success': True, 'message': '领料单已成功创建！'})

def view_requisition(request, pk):
    # 尝试获取领料单
    try:
        requisition = MaterialRequisition.objects.get(id=pk)
        # 获取领料单的基本信息
        data = {
            'success': True,
            'requisition': {
                'materialrequisition_number': requisition.materialrequisition_number,
                'production_order': {
                    'id': requisition.production_order.id,
                    'order_number': requisition.production_order.order_number,
                },
                'responsible_person': {
                    'id': requisition.responsible_person.id,
                    'username': requisition.responsible_person.username,
                },
                'productionmaterial_set': [],
                'created_at': ProductionMaterial.objects.filter(materialrequisition=requisition).first().created_at,
                'remarks': requisition.production_order.remarks,
            }
        }
        row_material_warehouse_location = WarehouseLocation.objects.filter(name = '原材料仓库').first()
        production_line_warehouse_location = WarehouseLocation.objects.filter(name = '产线仓库').first()
        # 获取领料项
        for item in ProductionMaterial.objects.filter(materialrequisition=requisition):
            # 获取原材料仓库的库存
            raw_material_stock = MaterialStock.objects.filter(material=item.material, location=row_material_warehouse_location).first()
            if raw_material_stock is None:
                raw_material_quantity = 0
            else:
                raw_material_quantity = raw_material_stock.quantity

            # 获取产线仓库的库存
            production_line_stock = MaterialStock.objects.filter(material=item.material, location=production_line_warehouse_location).first()
            if production_line_stock is None:
                production_line_quantity = 0
            else:
                production_line_quantity = production_line_stock.quantity  

            data['requisition']['productionmaterial_set'].append({
                'material': {
                    'id': item.material.id,
                    'name': item.material.name,
                },
                'quantity': item.quantity,
                'raw_material_quantity': raw_material_quantity,
                'production_line_quantity': production_line_quantity,
            })

        # 如果显示配方材料，可以在此添加
        # data['requisition']['recipe_materials'] = get_recipe_materials(requisition)
        
    except MaterialRequisition.DoesNotExist:
        return JsonResponse({'success': False, 'message': '领料单不存在或已被删除！'})

    # 返回领料单详情
    return JsonResponse(data)
            
def material_requisition_delete(request, pk):
    if request.user.is_authenticated:
        # 获取要删除的领料单
        requisition = get_object_or_404(MaterialRequisition, pk=pk)

        # 生产工单状态设置为pending
        productionorder = ProductionOrder.objects.filter(id=requisition.production_order.id).first()
        if(productionorder.status=="completed"):
            return JsonResponse({"success": False, "message": "生产已入库，无法删除！"})
        productionorder.status = 'pending'
        productionorder.save()

        # 删除材料项
        ProductionMaterial.objects.filter(materialrequisition=requisition).delete()
        # 删除领料单
        requisition.delete()

        # 返回成功响应
        return JsonResponse({"success": True, "message": "领料单删除成功！"})
    else:
        return JsonResponse({"success": False, "message": "未授权访问。"}, status=403)
    
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import WarehousingReceipt, Product, CustomUser, WarehouseLocation

def product_warehousing_list(request):
    """显示产品入库列表，支持分页和查询"""
    query = request.GET.get('q', '').strip() if 'q' in request.GET else None

    # 按查询条件过滤入库记录，并按入库单编号的倒序排列
    receipts = WarehousingReceipt.objects.select_related('productionorder', 'location', 'created_by') \
        .order_by('-receipt_number')

    if query:
        # 按入库单编号、工单编号、仓库名称、备注进行查询
        receipts = receipts.filter(receipt_number__icontains=query) | \
                   receipts.filter(productionorder__order_number__icontains=query) | \
                   receipts.filter(location__name__icontains=query) | \
                   receipts.filter(remarks__icontains=query)

    # 获取所有仓库位置和用户的列表
    locations = WarehouseLocation.objects.all()
    users = CustomUser.objects.all()
    production_orders = ProductionOrder.objects.filter(status="material_collected")

    # 分页处理
    paginator = Paginator(receipts, 10)  # 每页显示 10 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'receipts': page_obj.object_list,  # 当前页入库记录列表
        'page_obj': page_obj,  # 分页对象
        'paginator': paginator,  # 分页器
        'query': query,  # 搜索查询
        'locations': locations,  # 所有仓库位置
        'users': users,  # 所有用户
        'production_orders': production_orders, # 工单
    }
    return render(request, 'production/product_warehousing_list.html', context)

def get_sales_order_products(request, pk):

    # 获取指定的工单对象，如果不存在则返回 404
    sales_order = get_object_or_404(SalesOrder, pk=pk)

    # 获取与工单关联的产品
    salesorderitems = SalesOrderItem.objects.filter(order=sales_order)
    
    product_data = []
    for salesorderitem in salesorderitems:
        product_data.append({
            'id': salesorderitem.product.id,
            'name': salesorderitem.product.name,
            'expected_quantity': salesorderitem.quantity,  # 预期数量
            'actual_quantity': salesorderitem.quantity,  # 实际数量
        })
    response_data = {
        'success': True,
        'items': product_data
    }
    
    return JsonResponse(response_data)

def get_products(request, pk):

    # 获取指定的工单对象，如果不存在则返回 404
    production_order = get_object_or_404(ProductionOrder, pk=pk)

    # 获取与工单关联的产品
    salesorderitems = SalesOrderItem.objects.filter(order=production_order.sales_order)
    
    product_data = []
    for salesorderitem in salesorderitems:
        productionorderitem = ProductionOrderItem.objects.filter(production_order=production_order,product=salesorderitem.product).first()
        product_data.append({
            'id': salesorderitem.product.id,
            'name': salesorderitem.product.name,
            'sales_order_quantity': salesorderitem.quantity,  # 销售订单数量
            'production_order_quantity': productionorderitem.quantity,   # 工单数量
            'actual_quantity': salesorderitem.quantity,  # 实际数量
        })
    response_data = {
        'success': True,
        'items': product_data
    }
    
    return JsonResponse(response_data)

def product_receipt_create(request):
    """处理产品入库单创建"""
    if request.method == 'POST':
        production_order_id = request.POST.get('production_order')
        productionorder = ProductionOrder.objects.filter(id=production_order_id).first()
        location_id = request.POST.get('location')
        location = WarehouseLocation.objects.filter(id=location_id).first()
        remarks = request.POST.get('remarks')
        product_ids = request.POST.getlist('product_ids[]')
        expected_quantities = request.POST.getlist('expected_quantities[]')
        actual_quantities = request.POST.getlist('actual_quantities[]')
        #判断产线仓库材料是否足够
        insufficientmaterial = []

        items = ProductionOrderItem.objects.filter(production_order=productionorder)

        # 初始化所需材料列表
        required_materials = []
        # 将 product_ids 和 actual_quantities 创建成字典
        product_quantity_mapping = {
            product_id: Decimal(quantity) 
            for product_id, quantity in zip(product_ids, actual_quantities)
        }
        for item in items:
            # 判断产品 ID 是否在传入的 product_ids 中，并且获取对应的实际数量
            actual_quantity = product_quantity_mapping.get(str(item.product.id), 0)
            # 获取产品配方
            product = item.product
            recipe = Recipe.objects.filter(product=product).first()
            
            if recipe:
                recipematerials = RecipeMaterial.objects.filter(recipe=recipe)
                
                for material in recipematerials:  # 获取配方中的每种材料
                    material_id = material.material.id
                    material_name = material.material.name
                    material_quantity = material.quantity * actual_quantity  # 计算所需的总数量

                    # 查找是否已经存在该材料
                    existing_material = next((m for m in required_materials if m['material_id'] == material_id), None)
                    
                    if existing_material:
                        # 如果已存在，增加数量
                        existing_material['quantity'] += material_quantity
                    else:
                        # 否则，添加新材料
                        required_materials.append({
                            'material_id': material_id,
                            'material_name': material_name,
                            'quantity': material_quantity,
                        })
        
        productionline_warehouse = WarehouseLocation.objects.filter(name='产线仓库').first()
        for item in required_materials:
            materialstoct = MaterialStock.objects.filter(material_id=item['material_id'], location=productionline_warehouse).first()
            if materialstoct is None:
                MaterialStock.objects.create(material_id=item['material_id'], location=productionline_warehouse, quantity=-Decimal(item['quantity']))
                if -Decimal(item['quantity'])<0:
                    insufficientmaterial.append(item['material_name'])
            else:
                materialstoct.quantity-=Decimal(item['quantity'])
                if(materialstoct.quantity<0):
                    insufficientmaterial.append(item['material_name'])
                materialstoct.save()

        for product_id, actual_quantity in zip(product_ids, actual_quantities):
            # 获取产品的库存记录
            product = Product.objects.filter(id=product_id).first()
            product_stock = ProductStock.objects.filter(product=product,location=location).first()
            # 检查产品库存是否存在
            if product_stock is None:
                # 如果库存不存在，可以根据需求选择创建新的库存记录
                ProductStock.objects.create(
                    product=product,
                    location=location,  # 或者指定默认仓库位置
                    quantity=actual_quantity
                )               
            else:
                # 更新库存数量
                new_quantity = Decimal(product_stock.quantity) + Decimal(actual_quantity)
                product_stock.quantity = new_quantity
                product_stock.save()  # 保存更新

        # 创建新的入库单记录
        receipt = WarehousingReceipt(
            productionorder_id=production_order_id,
            location_id=location_id,
            remarks=remarks,
            created_by=request.user
        )

        receipt.save()  # 保存入库单以生成 receipt_number

        # 创建与入库单关联的物料记录
        for product_id, expected_quantity, actual_quantity in zip(product_ids, expected_quantities, actual_quantities):
            WarehousedProduct.objects.create(
                warehousingreceipt=receipt,
                product_id=product_id,
                expected_quantity=expected_quantity, 
                actual_quantity=actual_quantity
            )

        # 置工单状态为已完成
        productionorder.status = 'completed'
        productionorder.save()

        if insufficientmaterial:
            # 将材料名称连接成字符串，并显示在消息中
            material_names = ", ".join(insufficientmaterial)  # 将列表转换为逗号分隔的字符串
            return JsonResponse({'success': True, 'message': f'入库单创建成功！但是以下材料在产线仓库中数量不足：{material_names}，注意及时调拨！'})
        else:
            return JsonResponse({'success': True, 'message': '入库单创建成功！'})
    
    return JsonResponse({'success': False, 'message': '无效的请求'})


def production_plan(request):
    return render(request, 'production/production_plan.html', {})

def get_production_plans(request):
    # 获取所有生产工单
    production_orders = ProductionOrder.objects.filter(
        Q(status="pending") | Q(status="material_collected")
    )

    # 格式化数据以供甘特图使用
    tasks = []
    for order in production_orders:
        tasks.append({
            'id': order.id,
            'text': order.order_number,
            'start_date': order.planned_start_time.strftime('%Y-%m-%d'),
            'duration': (order.planned_end_time - order.planned_start_time).days,
            'production_line': order.production_line.name,
            'status': order.status,
        })
    
    return JsonResponse(tasks, safe=False)  # 返回JSON响应，safe=False允许返回非字典对象