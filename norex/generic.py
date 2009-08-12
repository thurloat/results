from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template
import re

def set_dir(request, tpl, queryset = None, view = None):
    p = re.compile('iPhone|iPod|Android|webOS', re.IGNORECASE)
    if p.search(request.META['HTTP_USER_AGENT']):
        dir = 'iphone'
    else:
        p = re.compile('BlackBerry|Nokia|Mobile', re.IGNORECASE)
        dir = 'mobile' if p.search(request.META['HTTP_USER_AGENT']) else ''
    if tpl is None:
        model = queryset.model
        templatename = "%s/%s_%s.html" % (dir,model._meta.object_name.lower(),view) if dir is not '' else "%s_%s.html" % (model._meta.object_name.lower(),view)
    else:
        templatename = "%s/%s" % (dir,tpl) if dir is not '' else tpl    
    return templatename

def UA_direct(request, template, extra_context=None, mimetype=None, **kwargs):
    return direct_to_template(request, set_dir(request,template), extra_context=extra_context, mimetype=None, **kwargs)

def UA_object_list(request, queryset, template_name = None, extra_context = None, **kwargs):
    return object_list(request, queryset, template_name = set_dir(request, template_name, queryset, "list"), extra_context = extra_context)

def UA_object_detail(request, queryset, slug_field = None, slug = None, template_name = None, template_object_name = None, extra_context = None, **kwargs):
    return object_detail(request,queryset,slug_field=slug_field,slug=int(slug), template_name=set_dir(request, template_name, queryset, "detail"), template_object_name = template_object_name, extra_context = extra_context)