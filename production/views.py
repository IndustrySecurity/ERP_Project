import datetime
from decimal import Decimal
import json
from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import transaction
from django.views import View
from .models import MaterialRequisition, ProductionMaterial, ProductionOrder
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
            remarks = request.POST.get('remarks', '')  # 获取备注信息
            status = 'pending'  # 默认状态为待处理

            logger.debug(f"Sales Order ID: {sales_order_id}, Production Line ID: {production_line_id}")

            # 获取相关对象
            sales_order = get_object_or_404(SalesOrder, pk=sales_order_id)
            production_line = get_object_or_404(ProductionLine, pk=production_line_id)

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

            # 更新生产工单的字段
            order.sales_order_id = sales_order_id  # 确保 sales_order_id 是有效的 ID
            order.production_line_id = production_line_id  # 确保 production_line_id 是有效的 ID
            order.planned_start_time = planned_start_time
            order.planned_end_time = planned_end_time

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
    production_orders = ProductionOrder.objects.all()
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
            sales_order = production_order.sales_order.id
            items = SalesOrderItem.objects.filter(order_id=sales_order)
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
                                'quantity': material_quantity
                            })
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
        # 查找材料对象
        material = Material.objects.get(id=material_id)
        # 创建与领料单关联的材料项
        ProductionMaterial.objects.create(materialrequisition=materialrequisition, material=material, quantity=quantity)
    
    # 返回成功信息
    return JsonResponse({'success': True, 'message': '领料单已成功创建！'})
