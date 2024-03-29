from django.template.defaultfilters import register


@register.simple_tag
def dict_get(a_dict, key, default=''):
    return a_dict.get(key, default)
