from django.shortcuts import render, get_object_or_404
from .models import CategoryGroup

def category_groups(request):
    groups = CategoryGroup.objects.all()
    return render(request, "category_groups.html", {"groups": groups})

def category_group_detail(request, group_id):
    group = get_object_or_404(CategoryGroup, id=group_id)
    categories = group.categories.all()
    return render(request, "category_detail.html", {
        "group": group,
        "categories": categories
    })
