from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import CustomUser, Role, Menu
from .forms import CustomUserForm, RoleForm, CustomUserCreationForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from .models import CustomUser
from .forms import CustomUserCreationForm

# 用户列表

def user_list(request):
    # 查询用户数据
    users = CustomUser.objects.all()
    # 创建表单实例
    user_form = CustomUserCreationForm()
    # 渲染模板
    return render(request, 'users/user_list.html', {
        'users': users,
        'user_form': user_form,  # 确保传递表单实例
    })

def user_list_ajax(request):
    # 获取搜索和分页参数
    search_query = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)

    # 过滤用户
    users = CustomUser.objects.filter(username__icontains=search_query) | CustomUser.objects.filter(email__icontains=search_query)

    # 分页
    paginator = Paginator(users, 10)  # 每页显示 10 条记录
    try:
        users_page = paginator.page(page)
    except Exception:
        users_page = paginator.page(1)

    # 返回 JSON 数据
    results = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': {'id': user.role.id, 'name': user.role.name} if user.role else None,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for user in users_page
    ]
    return JsonResponse({
        'results': results,
        'current_page': users_page.number,
        'total_pages': paginator.num_pages,
    })


# 创建用户
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': '用户编辑成功！'})
        return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CustomUserForm(instance=user)
        return render(request, 'users/user_edit.html', {'form': form})

# 删除用户
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        return JsonResponse({'success': True, 'message': '用户已删除！'})
    return JsonResponse({'success': False, 'message': '无效的请求'})

def role_list(request):
    roles = Role.objects.all()
    menus = Menu.objects.all()
    return render(request, 'users/role_list.html', {
        'roles': roles,
        'menus': menus,
    })


def role_list_ajax(request):
    search_query = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)

    roles = Role.objects.filter(name__icontains=search_query)
    paginator = Paginator(roles, 10)

    try:
        roles_page = paginator.page(page)
    except Exception:
        roles_page = paginator.page(1)

    results = [
        {
            'id': role.id,
            'name': role.name,
            'description': role.description or '-',
            'created_at': role.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'menus': [menu.name for menu in role.menus.all()],
        }
        for role in roles_page
    ]

    return JsonResponse({
        'results': results,
        'current_page': roles_page.number,
        'total_pages': paginator.num_pages,
    })

# 删除角色
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        return JsonResponse({'success': True, 'message': '角色已删除！'})
    return JsonResponse({'success': False, 'message': '无效的请求'})

def role_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        all_menus = request.POST.get('all_menus') == 'true'
        menu_ids = request.POST.getlist('menus')

        role = Role.objects.create(name=name, description=description, all_menus=all_menus)
        if not all_menus:  # 如果不是全权限，绑定具体菜单
            role.menus.set(Menu.objects.filter(id__in=menu_ids))
        role.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.name = request.POST.get('name')
        role.description = request.POST.get('description', '')
        role.all_menus = request.POST.get('all_menus') == 'true'
        menu_ids = request.POST.getlist('menus')

        if not role.all_menus:  # 如果不是全权限，绑定具体菜单
            role.menus.set(Menu.objects.filter(id__in=menu_ids))
        else:
            role.menus.clear()  # 清空具体菜单绑定

        role.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


