from django.shortcuts import render
from django.core import serializers
from apps.pages.models import Product

# Create your views here.

def charts(request):
    products = serializers.serialize('json', Product.objects.all())
    context = {
        'segment'  : 'react_charts',
        'parent'   : 'apps',
        'products': products
    }
    return render(request, 'charts/react/index.html', context)