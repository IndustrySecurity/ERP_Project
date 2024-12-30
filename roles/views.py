from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Role
from .forms import RoleForm

def role_list(request):
    roles = Role.objects.all()
    form = RoleForm()  # 初始化空表单用于创建角色
    return render(request, 'roles/role_list.html', {'roles': roles, 'form': form})


def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': '角色创建成功！'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': '非法请求！'})


def role_update(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': '角色更新成功！'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = RoleForm(instance=role)
    return render(request, 'roles/partials/role_update_form.html', {'form': form, 'role': role})


def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        return JsonResponse({'success': True, 'message': '角色删除成功！'})
    return JsonResponse({'success': False, 'message': '非法请求！'})
