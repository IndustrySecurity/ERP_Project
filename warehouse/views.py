from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WarehouseLocation, MaterialStock, ProductStock, InventoryCheck, Transfer
from .forms import MaterialStockForm, ProductStockForm, InventoryCheckForm
from master_data.models import Material, Product
from decimal import Decimal
from django.db.models import Q
from django.core.paginator import Paginator
# 仓库位置管理
def warehouse_location_list(request):
    locations = WarehouseLocation.objects.all()
    return render(request, 'warehouse/warehouse_location_list.html', {'locations': locations})


def warehouse_location_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        location = WarehouseLocation.objects.create(name=name, description=description)
        return JsonResponse({'success': True, 'id': location.id, 'name': location.name, 'description': location.description})
    return JsonResponse({'success': False, 'message': '仅支持POST请求'})


# 原材料库存管理
def material_stock_list(request):
    """
    渲染原材料库存列表页面
    """
    query = request.GET.get('q', '').strip()
    stocks = MaterialStock.objects.select_related('material', 'location').all()
    if query:
        stocks = stocks.filter(
            material__name__icontains=query
        )

    paginator = Paginator(stocks, 10)  # 每页显示 10 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    materials = Material.objects.all()
    locations = WarehouseLocation.objects.all()
    return render(request, 'warehouse/material_stock_list.html', {
        'stocks': page_obj.object_list,
        'page_obj': page_obj,
        'materials': materials,
        'locations': locations,
    })



@csrf_exempt
def material_stock_create(request):
    """
    创建原材料库存
    """
    if request.method == 'POST':
        material_id = request.POST.get('material')
        location_id = request.POST.get('location')
        quantity = request.POST.get('quantity')

        if not material_id or not location_id or not quantity:
            return JsonResponse({'success': False, 'errors': '所有字段均为必填项'})

        try:
            material = get_object_or_404(Material, pk=material_id)
            location = get_object_or_404(WarehouseLocation, pk=location_id)
            quantity = Decimal(quantity)  # 转换为 Decimal

            stock, created = MaterialStock.objects.get_or_create(
                material=material,
                location=location,
                defaults={'quantity': quantity}
            )
            if not created:
                stock.quantity += quantity  # Decimal 类型运算
                stock.save()

            return JsonResponse({'success': True, 'message': '原材料库存添加成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'errors': str(e)})

    return JsonResponse({'success': False, 'message': '仅支持POST请求'})



@csrf_exempt
def material_stock_delete(request, pk):
    """
    删除原材料库存
    """
    stock = get_object_or_404(MaterialStock, pk=pk)
    if request.method == 'DELETE':
        stock.delete()
        return JsonResponse({'success': True, 'message': '原材料库存删除成功'})
    return JsonResponse({'success': False, 'message': '仅支持DELETE请求'})


@csrf_exempt
def material_stock_edit(request, pk):
    """
    编辑原材料库存
    """
    stock = get_object_or_404(MaterialStock, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'material_id': stock.material.id,
            'location_id': stock.location.id,
            'quantity': float(stock.quantity),
        })
    elif request.method == 'POST':
        quantity = request.POST.get('quantity')
        try:
            if not quantity:
                return JsonResponse({'success': False, 'errors': '库存数量为必填项'})
            stock.quantity = Decimal(quantity)
            stock.save()
            return JsonResponse({'success': True, 'message': '原材料库存更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'errors': str(e)})

    return JsonResponse({'success': False, 'message': '无效的请求'})


# 产品库存管理
def product_stock_list(request):
    """
    渲染成品库存列表页面，并支持所有字段的全文检索。
    """
    query = request.GET.get('q', '').strip()
    stocks = ProductStock.objects.select_related('product', 'location')

    # 全字段全文检索
    if query:
        stocks = stocks.filter(
            Q(product__name__icontains=query) |  # 产品名称
            Q(product__product_code__icontains=query) |  # 产品编号
            Q(product__category__name__icontains=query) |  # 产品类别
            Q(product__material__icontains=query) |  # 容器材质
            Q(product__capacity__icontains=query) |  # 规格
            Q(product__technology__icontains=query) |  # 香型
            Q(product__color__icontains=query) |  # 颜色
            Q(product__remark__icontains=query) |  # 备注
            Q(location__name__icontains=query)  # 仓库位置
        )

    paginator = Paginator(stocks, 10)  # 每页显示 10 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    products = Product.objects.all()
    locations = WarehouseLocation.objects.all()
    return render(request, 'warehouse/product_stock_list.html', {
        'stocks': page_obj.object_list,
        'page_obj': page_obj,
        'products': products,
        'locations': locations,
        'query': query,  # 用于模板中搜索框回显
    })



@csrf_exempt
def product_stock_create(request):
    """
    创建成品库存
    """
    if request.method == 'POST':
        product_id = request.POST.get('product')
        location_id = request.POST.get('location')
        quantity = request.POST.get('quantity')

        if not product_id or not location_id or not quantity:
            return JsonResponse({'success': False, 'errors': '所有字段均为必填项'})

        try:
            product = get_object_or_404(Product, pk=product_id)
            location = get_object_or_404(WarehouseLocation, pk=location_id)
            quantity = Decimal(quantity)  # 使用 Decimal 类型

            stock, created = ProductStock.objects.get_or_create(
                product=product,
                location=location,
                defaults={'quantity': quantity}
            )
            if not created:
                stock.quantity += quantity
                stock.save()

            return JsonResponse({'success': True, 'message': '成品库存添加成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'errors': str(e)})

    return JsonResponse({'success': False, 'message': '仅支持POST请求'})


@csrf_exempt
def product_stock_delete(request, pk):
    """
    删除成品库存
    """
    stock = get_object_or_404(ProductStock, pk=pk)
    if request.method == 'DELETE':
        stock.delete()
        return JsonResponse({'success': True, 'message': '成品库存删除成功'})
    return JsonResponse({'success': False, 'message': '仅支持DELETE请求'})


@csrf_exempt
def product_stock_edit(request, pk):
    """
    编辑或获取成品库存
    """
    stock = get_object_or_404(ProductStock, pk=pk)

    if request.method == 'GET':
        # 返回当前库存信息
        return JsonResponse({
            'success': True,
            'product_id': stock.product.id,
            'location_id': stock.location.id,
            'quantity': stock.quantity,
            'message': '库存信息获取成功',
        })

    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        try:
            if not quantity:
                return JsonResponse({'success': False, 'errors': '库存数量为必填项'})
            stock.quantity = float(quantity)
            stock.save()
            return JsonResponse({'success': True, 'message': '成品库存更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'errors': str(e)})

    return JsonResponse({'success': False, 'message': '仅支持GET和POST请求'})



# 库存盘点管理
def inventory_check_list(request):
    query = request.GET.get('q', '').strip()
    records = InventoryCheck.objects.select_related('location')

    if query:
        records = records.filter(
            location__name__icontains=query  # 搜索仓库名称
        ) | records.filter(
            item__icontains=query  # 搜索盘点项目
        ) | records.filter(
            remarks__icontains=query  # 搜索备注
        )

    paginator = Paginator(records, 10)  # 每页 10 条
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    locations = WarehouseLocation.objects.all()
    return render(request, 'warehouse/inventory_check_list.html', {
        'locations': locations,
        'records': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,  # 保留搜索关键字
    })


@csrf_exempt
def inventory_check_create(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        location_id = request.POST.get('location')
        item_id = request.POST.get('item')
        after_quantity = Decimal(request.POST.get('after_quantity', 0))
        remarks = request.POST.get('remarks', '')

        location = get_object_or_404(WarehouseLocation, pk=location_id)

        if category == 'material':
            material_stock = get_object_or_404(MaterialStock, material_id=item_id, location=location)
            before_quantity = Decimal(material_stock.quantity)
            material_stock.quantity = after_quantity
            material_stock.save()

            inventory_check = InventoryCheck.objects.create(
                location=location,
                before_quantity=before_quantity,
                after_quantity=after_quantity,
                variance=after_quantity - before_quantity,
                remarks=remarks,
                category='material',
                item=material_stock.material.name,  # 保存具体名称
                #created_by=request.user  # 保存创建人
            )
            inventory_check.material_stock.set([material_stock])  # 设置 ManyToMany 关系
        elif category == 'product':
            product_stock = get_object_or_404(ProductStock, product_id=item_id, location=location)
            before_quantity = Decimal(product_stock.quantity)
            product_stock.quantity = after_quantity
            product_stock.save()

            inventory_check = InventoryCheck.objects.create(
                location=location,
                before_quantity=before_quantity,
                after_quantity=after_quantity,
                variance=after_quantity - before_quantity,
                remarks=remarks,
                category='product',
                item=product_stock.product.name,  # 保存具体名称
                #created_by=request.user  # 保存创建人
            )
            inventory_check.product_stock.set([product_stock])  # 设置 ManyToMany 关系

        return JsonResponse({'success': True, 'message': '盘点记录已保存'})

    return JsonResponse({'success': False, 'message': '请求无效'})



@csrf_exempt
def inventory_transfer_create(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        from_location_id = request.POST.get('from_location')
        to_location_id = request.POST.get('to_location')
        item_id = request.POST.get('item')
        quantity = Decimal(request.POST.get('quantity', 0))
        remarks = request.POST.get('remarks', '')

        try:
            from_location = get_object_or_404(WarehouseLocation, pk=from_location_id)
            to_location = get_object_or_404(WarehouseLocation, pk=to_location_id)

            if category == 'material':
                # 获取源库存
                from_stock = get_object_or_404(MaterialStock, material_id=item_id, location=from_location)

                # 获取目标库存或创建新记录
                to_stock, created = MaterialStock.objects.get_or_create(
                    material_id=item_id,
                    location=to_location,
                    defaults={'quantity': Decimal(0)}
                )
            elif category == 'product':
                from_stock = get_object_or_404(ProductStock, product_id=item_id, location=from_location)
                to_stock, created = ProductStock.objects.get_or_create(
                    product_id=item_id,
                    location=to_location,
                    defaults={'quantity': Decimal(0)}
                )
            else:
                return JsonResponse({'success': False, 'message': '无效的类别'})

            # 检查库存是否足够
            if from_stock.quantity < quantity:
                return JsonResponse({'success': False, 'message': '库存不足'})

            # 更新库存数量
            from_stock.quantity -= quantity
            from_stock.save()

            to_stock.quantity += quantity
            to_stock.save()

            # 记录调拨操作
            Transfer.objects.create(
                from_location=from_location,
                to_location=to_location,
                category=category,
                item=from_stock.material.name if category == 'material' else from_stock.product.name,
                quantity=quantity,
                remarks=remarks,
            )

            return JsonResponse({'success': True, 'message': '调拨成功'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'调拨失败: {str(e)}'})

    return JsonResponse({'success': False, 'message': '请求无效'})



def get_items(request):
    category = request.GET.get('category')
    location_id = request.GET.get('location')

    if not location_id or not category:
        return JsonResponse({'results': []})  # 返回空数组

    location = get_object_or_404(WarehouseLocation, pk=location_id)

    if category == 'material':
        items = MaterialStock.objects.filter(location=location).select_related('material')
        results = [{'id': item.material.id, 'name': item.material.name} for item in items]
    elif category == 'product':
        items = ProductStock.objects.filter(location=location).select_related('product')
        results = [{'id': item.product.id, 'name': item.product.name} for item in items]
    else:
        results = []

    return JsonResponse({'results': results})  # 确保返回结果是数组

def get_quantity(request):
    category = request.GET.get('category')
    location_id = request.GET.get('location')
    item_id = request.GET.get('item')

    location = get_object_or_404(WarehouseLocation, pk=location_id)

    if category == 'material':
        stock = get_object_or_404(MaterialStock, material_id=item_id, location=location)
    elif category == 'product':
        stock = get_object_or_404(ProductStock, product_id=item_id, location=location)
    else:
        return JsonResponse({'quantity': 0})

    return JsonResponse({'quantity': stock.quantity})

def get_stock_quantity(request, location_id, product_id):
    """获取仓库中指定产品的库存数量"""
    try:
        product_stock = get_object_or_404(ProductStock, location_id=location_id, product_id=product_id)
        return JsonResponse({'stock_quantity': float(product_stock.quantity)})
    except ProductStock.DoesNotExist:
        return JsonResponse({'stock_quantity': 0})