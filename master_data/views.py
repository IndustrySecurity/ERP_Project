from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Max, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Material, Product, Recipe, Supplier, Customer, RecipeMaterial, MaterialCategory, ProductCategory, ProductionLine
from .forms import MaterialForm, ProductForm, RecipeForm, SupplierForm, CustomerForm, ProductionLineForm
from django.template.loader import render_to_string
from django.db.utils import IntegrityError
from datetime import datetime

def material_list(request):
    """
    原材料管理视图，支持分页、搜索以及类别和供应商的选择框初始化。
    """
    # 搜索功能
    query = request.GET.get('q', '').strip()  # 获取搜索关键字并去除多余空格
    if query:
        materials = Material.objects.filter(
            Q(name__icontains=query) |  # 按原材料名称检索
            Q(material_number__icontains=query) |  # 按料号检索
            Q(category__name__icontains=query)  # 按分类名称检索
        ).order_by('material_number')  # 添加排序
    else:
        materials = Material.objects.all().order_by('material_number')  # 添加排序

    # 分页功能
    paginator = Paginator(materials, 30)  # 每页显示30条数据
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 获取类别和供应商信息
    categories = MaterialCategory.objects.all()
    suppliers = Supplier.objects.all()

    # 上下文数据
    context = {
        'materials': page_obj.object_list,  # 当前页的数据
        'page_obj': page_obj,              # 分页对象
        'paginator': paginator,            # 分页器
        'categories': categories,          # 类别选择框数据
        'suppliers': suppliers,            # 供应商选择框数据
        'query': query                     # 搜索关键字（用于模板回显）
    }

    return render(request, 'master_data/material_list.html', context)

def material_list_ajax(request):
    """
    AJAX 请求，获取原材料列表，支持多字段检索。
    """
    query = request.GET.get('search', '').strip()  # 搜索关键字
    supplier_id = request.GET.get('supplier')  # 供应商过滤条件

    # 初始查询集
    materials = Material.objects.all()

    # 搜索功能扩展
    if query:
        materials = materials.filter(
            Q(name__icontains=query) |  # 按名称检索
            Q(material_number__icontains=query) |  # 按料号检索
            Q(category__name__icontains=query)  # 按分类名称检索
        )

    # 按供应商过滤
    if supplier_id:
        materials = materials.filter(supplier_id=supplier_id)

    # 构建返回数据
    results = [
        {
            'id': material.id,
            'material_number': material.material_number,
            'name': material.name,
            'category': material.category.name if material.category else '无',
            'supplier': material.supplier.name if material.supplier else '无',
            'unit_price': str(material.unit_price),
            'capacity': material.capacity,
            'color': material.color,
            'technology': material.technology,
            'remark': material.remark,
        }
        for material in materials
    ]

    return JsonResponse({'materials': results})


def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            try:
                # 检查是否需要创建新类别
                new_category_name = request.POST.get('new_category', '').strip()
                if new_category_name:
                    category, _ = MaterialCategory.objects.get_or_create(name=new_category_name)
                    form.instance.category = category

                # 尝试保存，如果material_number重复则生成新的
                try:
                    form.save()
                except IntegrityError:
                    # 如果material_number重复，生成新的
                    today = datetime.now().strftime('%Y%m%d')
                    last_material = Material.objects.filter(material_number__startswith=today).order_by('-material_number').first()
                    
                    if last_material:
                        # 获取最后6位数字并加1
                        last_number = int(last_material.material_number[-6:])
                        new_number = last_number + 1
                    else:
                        new_number = 1
                    
                    # 生成新的料号，格式：YYYYMMDD-XXXXXX
                    form.instance.material_number = f"{today}-{new_number:06d}"
                    form.save()

                return JsonResponse({'success': True, 'message': '原材料创建成功'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'创建失败: {str(e)}'})
        else:
            return JsonResponse({'success': False, 'message': form.errors.as_json()})
    return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})

# Get material details
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return JsonResponse({
        'id': material.id,
        'name': material.name,
        'category': material.category.id if material.category else '',
        'supplier': material.supplier.id if material.supplier else '',
        'unit_price': material.unit_price,
    })

def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'GET':
        categories = MaterialCategory.objects.all().values('id', 'name')
        suppliers = Supplier.objects.all().values('id', 'name')
        return JsonResponse({
            'success': True,
            'material': {
                'name': material.name,
                'category': material.category.id if material.category else '',
                'supplier': material.supplier.id if material.supplier else '',
                'unit_price': str(material.unit_price),
                'capacity': material.capacity,
                'color': material.color,
                'customer_supply': material.customer_supply,
                'technology': material.technology,
                'remark': material.remark,
            },
            'categories': list(categories),
            'suppliers': list(suppliers),
        })
    elif request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': '原材料更新成功'})
        return JsonResponse({'success': False, 'message': form.errors})
    return JsonResponse({'success': False, 'message': '仅支持 GET 或 POST 请求'})

# Delete material
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    material.delete()
    return JsonResponse({'success': True, 'message': '原材料删除成功'})

def product_list(request):
    query = request.GET.get('q', '').strip()  # 搜索关键字
    # 扩展搜索范围
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(product_code__icontains=query) |  # 按产品编号搜索
            Q(category__name__icontains=query)  # 按产品类别搜索
        )
    else:
        products = Product.objects.all()

    paginator = Paginator(products, 30)  # 每页显示 30 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    categories = ProductCategory.objects.all()

    context = {
        'products': page_obj.object_list,  # 当前页的数据
        'page_obj': page_obj,              # 分页对象
        'paginator': paginator,            # 分页器
        'categories': categories,          # 类别选择框初始化
        'query': query                     # 搜索关键字回显
    }
    return render(request, 'master_data/product_list.html', context)


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return JsonResponse({'success': True, 'message': '产品已删除'})

def generate_product_code():
    prefix = "PROD"  # 固定前缀
    max_code = Product.objects.aggregate(max_code=Max('product_code'))['max_code']
    if max_code:
        last_number = int(max_code.replace(prefix, ""))
        new_number = last_number + 1
    else:
        new_number = 1
    return f"{prefix}{new_number:06d}"

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # 处理新类别逻辑
            category_id = request.POST.get('category')  # 获取现有类别 ID
            new_category_name = request.POST.get('new_category')  # 获取新类别名称

            if new_category_name and category_id:
                return JsonResponse({'success': False, 'message': '不能同时选择现有类别和新类别'}, status=400)

            category = None
            if new_category_name:  # 如果有新类别名称
                category, created = ProductCategory.objects.get_or_create(name=new_category_name)
            elif category_id:  # 如果有现有类别 ID
                try:
                    category = ProductCategory.objects.get(id=category_id)
                except ProductCategory.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '选择的类别无效'}, status=400)

            # 将类别赋值到表单实例
            form.instance.category = category

            # 保存产品实例
            product = form.save()
            return JsonResponse({
                'success': True,
                'message': '产品创建成功',
                'product': {
                    'id': product.id,
                    'product_code': product.product_code,
                    'name': product.name,
                    'category': product.category.name if product.category else '无',
                    'unit_price': str(product.unit_price),
                    'container_material': product.container_material,
                    'capacity': product.capacity,
                    'technology': product.technology,
                    'color': product.color,
                    'contract_date': product.contract_date,
                    'remarks': product.remarks,
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'message': '请求方法错误'}, status=405)



def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': '产品更新成功'})
        return JsonResponse({'success': False, 'errors': form.errors})
    
def product_list_ajax(request):
    """AJAX请求，获取产品列表"""
    search_query = request.GET.get("search", "").strip()  # 获取搜索关键字
    page = int(request.GET.get("page", 1))  # 当前页码
    page_size = 20  # 每页显示的产品数量

    # 构建查询条件，支持按名称、编号、类别名称检索
    products = Product.objects.filter(
        Q(name__icontains=search_query) |  # 按产品名称搜索
        Q(product_code__icontains=search_query) |  # 按产品编号搜索
        Q(category__name__icontains=search_query)  # 按类别名称搜索
    )

    total_count = products.count()  # 总记录数

    # 分页处理
    products = products[(page - 1) * page_size : page * page_size]

    # 构建返回的结果
    results = [
        {
            "id": product.id,
            "product_code": product.product_code,
            "name": product.name,
            "category": product.category.name if product.category else "无",
            "unit_price": str(product.unit_price),  # 确保单价为字符串
            "material": product.material,
            "capacity": product.capacity,
            "technology": product.technology,
            "color": product.color,
            "contract_date": product.contract_date.strftime('%Y-%m-%d') if product.contract_date else "",
            "remark": product.remark,
        }
        for product in products
    ]

    # 返回 JSON 数据
    return JsonResponse(
        {
            "results": results,
            "current_page": page,
            "total_pages": (total_count + page_size - 1) // page_size,
        }
    )


@csrf_exempt
def product_create_ajax(request):
    if request.method == 'POST':
        new_category_name = request.POST.get('new_category', '').strip()
        if new_category_name:
            category, _ = ProductCategory.objects.get_or_create(name=new_category_name)
        else:
            category = None

        product = Product(
            name=request.POST.get('name'),
            category=category or ProductCategory.objects.get(id=request.POST.get('category')),
            unit_price=request.POST.get('unit_price'),
            material=request.POST.get('material'),
            capacity=request.POST.get('capacity'),
            technology=request.POST.get('technology'),
            color=request.POST.get('color'),
            remark=request.POST.get('remark'),
        )
        product.save()

        return JsonResponse({'success': True, 'message': '产品创建成功'})
    return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})



@csrf_exempt
def product_edit_ajax(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        categories = ProductCategory.objects.all().values('id', 'name')
        return JsonResponse({
            'success': True,
            'product': {
                'name': product.name,
                'category': product.category.id if product.category else '',
                'unit_price': str(product.unit_price),
                'material': product.material,
                'capacity': product.capacity,
                'technology': product.technology,
                'color': product.color,
                'remark': product.remark,
            },
            'categories': list(categories),
        })

    elif request.method == 'POST':
        product.name = request.POST.get('name')
        product.category_id = request.POST.get('category')
        product.unit_price = request.POST.get('unit_price')
        product.material = request.POST.get('material')
        product.capacity = request.POST.get('capacity')
        product.technology = request.POST.get('technology')
        product.color = request.POST.get('color')
        product.remark = request.POST.get('remark')
        product.save()
        return JsonResponse({'success': True, 'message': '产品更新成功'})

    return JsonResponse({'success': False, 'message': '仅支持 GET 或 POST 请求'})



@csrf_exempt
def product_delete_ajax(request, pk):
    """AJAX请求，删除产品"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'DELETE':
        product.delete()
        return JsonResponse({'success': True, 'message': '产品删除成功'})
    return JsonResponse({'success': False, 'message': '仅支持DELETE请求'})

def recipe_list(request):
    """配方列表视图"""
    query = request.GET.get('q', '').strip()
    recipes = Recipe.objects.filter(product__name__icontains=query) if query else Recipe.objects.all()

    paginator = Paginator(recipes, 30)  # 每页显示 30 条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 初始化产品和材料数据
    materials = Material.objects.all()  # 获取所有材料

    context = {
        'recipes': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'query': query,
    }
    return render(request, 'master_data/recipe_list.html', context)

def product_list_api(request):
    """产品列表 API 视图，实现产品的搜索与分页"""
    product_query = request.GET.get('product_q', '').strip()

    products = Product.objects.all()
    if product_query:
        products = products.filter(Q(name__icontains=product_query) | Q(product_code__icontains=product_query)).distinct()

    product_paginator = Paginator(products, 20)  # 每页显示 10 条记录
    product_page_number = request.GET.get('product_page', 1)

    product_page_obj = product_paginator.get_page(product_page_number)

    # 构建返回数据
    product_data = [{
        'id': product.id,
        'product_code': product.product_code,
        'name': product.name,
        'category': product.category.name,
        'unit_price': product.unit_price,
        'material': product.material,
        'capacity': product.capacity,
        'color': product.color,
        'technology': product.technology,
        'remark': product.remark,
    } for product in product_page_obj]

    response_data = {
        'products': product_data,
        'has_previous': product_page_obj.has_previous(),
        'has_next': product_page_obj.has_next(),
        'number': product_page_obj.number,
        'total_pages': product_paginator.num_pages,
    }

    return JsonResponse(response_data)

def material_list_api(request):
    """材料列表 API 视图，实现材料的搜索与分页"""
    material_query = request.GET.get('material_q', '').strip()

    materials = Material.objects.all()
    if material_query:
        # 通过名称、料号、类别、供应商进行过滤
        materials = materials.filter(
            Q(name__icontains=material_query) |
            Q(material_number__icontains=material_query) |
            Q(supplier__name__icontains=material_query)
        ).distinct()

    material_paginator = Paginator(materials, 20)  # 每页显示 10 条记录
    material_page_number = request.GET.get('material_page', 1)

    material_page_obj = material_paginator.get_page(material_page_number)

    # 构建返回数据
    material_data = [{
        'id': material.id,
        'material_number': material.material_number,
        'name': material.name,
        'category': material.category.name if material.category else None,
        'supplier': material.supplier.name if material.supplier else None,
        'unit_price': material.unit_price,  
        'capacity': material.capacity,
        'color': material.color,
        'customer_supply': material.customer_supply,
        'technology': material.technology,
        'remark': material.remark,
    } for material in material_page_obj]

    response_data = {
        'materials': material_data,
        'has_previous': material_page_obj.has_previous(),
        'has_next': material_page_obj.has_next(),
        'number': material_page_obj.number,
        'total_pages': material_paginator.num_pages,
    }

    return JsonResponse(response_data)

def recipe_create(request):
    """创建配方视图"""
    if request.method == 'POST':
        product_id = request.POST.get('product')
        materials_data = request.POST.getlist('materials')
        quantities = request.POST.getlist('quantities')
        description = request.POST.get('description', '')

        try:
            product = Product.objects.get(id=product_id)

             # 检查该产品是否已有配方
            if Recipe.objects.filter(product=product).exists():
                return JsonResponse({'success': False, 'message': '该产品已存在配方'})
            
            recipe = Recipe(product=product, description=description)
            recipe.save()
            for material_id, quantity in zip(materials_data, quantities):
                material = Material.objects.get(id=material_id)
                RecipeMaterial.objects.create(recipe=recipe, material=material, quantity=quantity)

            return JsonResponse({'success': True, 'message': '配方创建成功'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': '所选产品不存在'})
        except Material.DoesNotExist:
            return JsonResponse({'success': False, 'message': '所选材料不存在'})
    return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})

def recipe_update(request, pk):
    """编辑配方视图"""
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == 'GET':
        # 获取配方关联的材料及其数量
        materials = recipe.recipematerial_set.all().values(
            'material__id', 'material__name', 'quantity'
        )

        return JsonResponse({
            'success': True,
            'recipe': {
                'description': recipe.description or "",
                'materials': list(materials),  # 材料列表
                'product_id': recipe.product.id,  # 产品ID
                'product_name': recipe.product.name,
            }
        })

    elif request.method == 'POST':
        # 更新配方描述及材料关联
        description = request.POST.get('description', '')
        materials_data = request.POST.getlist('materials')
        quantities = request.POST.getlist('quantities')
        product_id = request.POST.get('product')
        #删除原配方，新建配方
        recipe.delete()
        product = Product.objects.get(id=product_id)
        recipe = Recipe(product=product, description=description)
        recipe.save()
        # recipe.recipematerial_set.all().delete()  # 删除旧的材料关联

        try:
            for material_id, quantity in zip(materials_data, quantities):
                material = Material.objects.get(id=material_id)
                RecipeMaterial.objects.create(recipe=recipe, material=material, quantity=quantity)
            recipe.save()
            return JsonResponse({'success': True, 'message': '配方更新成功'})
        except Material.DoesNotExist:
            return JsonResponse({'success': False, 'message': '所选材料不存在'})

    return JsonResponse({'success': False, 'message': '仅支持 GET 或 POST 请求'})


def recipe_delete(request, pk):
    """删除配方视图"""
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'DELETE':
        recipe.delete()
        return JsonResponse({'success': True, 'message': '配方删除成功'})
    return JsonResponse({'success': False, 'message': '仅支持 DELETE 请求'})

def supplier_list(request):
    suppliers = Supplier.objects.all()
    form = SupplierForm()
    return render(request, 'master_data/supplier_list.html', {'suppliers': suppliers, 'form': form})


def supplier_list_ajax(request):
    """AJAX请求，获取供应商列表"""
    search_query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    page_size = 20  # 每页显示的供应商数量

    suppliers = Supplier.objects.filter(name__icontains=search_query)
    total_count = suppliers.count()
    suppliers = suppliers[(page - 1) * page_size: page * page_size]

    results = [
        {
            'id': supplier.id,
            'name': supplier.name,
            'contact': supplier.contact,
            'address': supplier.address,
        } for supplier in suppliers
    ]

    return JsonResponse({
        'results': results,
        'current_page': page,
        'total_pages': (total_count + page_size - 1) // page_size,
    })


@csrf_exempt
def supplier_create_ajax(request):
    """AJAX请求，创建供应商"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            return JsonResponse({'success': True, 'message': '供应商创建成功', 'id': supplier.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': '仅支持POST请求'})


@csrf_exempt
def supplier_edit_ajax(request, pk):
    """AJAX请求，编辑供应商"""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': '供应商更新成功'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': '仅支持POST请求'})


@csrf_exempt
def supplier_delete_ajax(request, pk):
    """AJAX请求，删除供应商"""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'DELETE':
        supplier.delete()
        return JsonResponse({'success': True, 'message': '供应商删除成功'})
    return JsonResponse({'success': False, 'message': '仅支持DELETE请求'})

def production_line_list(request):
    """展示产线列表"""
    production_lines = ProductionLine.objects.all()
    form = ProductionLineForm()
    return render(request, 'master_data/production_line_list.html', {'production_lines': production_lines, 'form': form})


def production_line_list_ajax(request):
    """AJAX请求，获取产线列表"""
    search_query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    page_size = 20  # 每页显示的产线数量

    production_lines = ProductionLine.objects.filter(name__icontains=search_query)
    total_count = production_lines.count()
    production_lines = production_lines[(page - 1) * page_size: page * page_size]

    results = [
        {
            'id': production_line.id,
            'name': production_line.name,
            'description': production_line.description,
        } for production_line in production_lines
    ]

    return JsonResponse({
        'results': results,
        'current_page': page,
        'total_pages': (total_count + page_size - 1) // page_size,
    })


@csrf_exempt
def production_line_create_ajax(request):
    """AJAX请求，创建产线"""
    if request.method == 'POST':
        form = ProductionLineForm(request.POST)
        if form.is_valid():
            production_line = form.save()
            return JsonResponse({'success': True, 'message': '产线创建成功', 'id': production_line.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': '仅支持POST请求'})


@csrf_exempt
def production_line_edit_ajax(request, pk):
    """AJAX请求，编辑产线"""
    production_line = get_object_or_404(ProductionLine, pk=pk)
    if request.method == 'POST':
        form = ProductionLineForm(request.POST, instance=production_line)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': '产线更新成功'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': '仅支持POST请求'})


@csrf_exempt
def production_line_delete_ajax(request, pk):
    """AJAX请求，删除产线"""
    production_line = get_object_or_404(ProductionLine, pk=pk)
    if request.method == 'DELETE':
        production_line.delete()
        return JsonResponse({'success': True, 'message': '产线删除成功'})
    return JsonResponse({'success': False, 'message': '仅支持DELETE请求'})

# 通用创建视图
def create_item(request, model, form_class):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': f'{model._meta.verbose_name}创建成功'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})

# 通用更新视图
def update_item(request, model, pk, form_class):
    instance = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': f'{model._meta.verbose_name}更新成功'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})

# 通用删除视图
def delete_item(request, model, pk):
    instance = get_object_or_404(model, pk=pk)
    instance.delete()
    return JsonResponse({'success': True, 'message': f'{model._meta.verbose_name}删除成功'})

def customer_list(request):
    query = request.GET.get('q', '')
    customers = Customer.objects.filter(
        name__icontains=query
    ) if query else Customer.objects.all()

    # 添加分页
    paginator = Paginator(customers, 20)  # 每页显示10个客户
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'customers': page_obj.object_list,
        'paginator': paginator,
        'page_obj': page_obj,
    }
    return render(request, 'master_data/customer_list.html', context)

@csrf_exempt
def customer_create(request):
    """创建客户"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return JsonResponse({'success': True, 'id': customer.id, 'name': customer.name})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def customer_edit(request, pk):
    """
    处理客户编辑逻辑。
    GET: 返回客户信息用于前端填充表单。
    POST: 保存更新后的客户数据。
    """
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'GET':
        # 返回客户信息，用于前端编辑表单的填充
        return JsonResponse({
            'success': True,
            'customer': {
                'name': customer.name,
                'contact_info': customer.contact_info or '',
                'email': customer.email or '',
                'address': customer.address or '',
                'grade': customer.grade or 'C',
                'company': customer.company or '',
                'remarks': customer.remarks or '',
            }
        })

    elif request.method == 'POST':
        # 更新客户信息
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': '客户信息更新成功！'})
        else:
            # 返回表单错误
            return JsonResponse({'success': False, 'errors': form.errors})

    # 非 GET 或 POST 请求返回错误
    return JsonResponse({'success': False, 'message': '无效的请求方法。'}, status=405)


@csrf_exempt
def customer_delete(request, pk):
    """删除客户"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'DELETE':
        customer.delete()
        return JsonResponse({'success': True, 'message': '客户已删除'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

# CRUD 操作
def material_update(request, pk):
    return update_item(request, Material, pk, MaterialForm)

def material_delete(request, pk):
    return delete_item(request, Material, pk)

def product_create(request):
    return create_item(request, Product, ProductForm)

def product_update(request, pk):
    return update_item(request, Product, pk, ProductForm)

def product_delete(request, pk):
    return delete_item(request, Product, pk)

def supplier_create(request):
    return create_item(request, Supplier, SupplierForm)

def supplier_update(request, pk):
    return update_item(request, Supplier, pk, SupplierForm)

def supplier_delete(request, pk):
    return delete_item(request, Supplier, pk)

def customer_create(request):
    return create_item(request, Customer, CustomerForm)

def customer_update(request, pk):
    return update_item(request, Customer, pk, CustomerForm)

def customer_delete(request, pk):
    return delete_item(request, Customer, pk)
