from django.shortcuts import render


def handler404(
        request, exception, template_name="flatpages/title_and_text.html"):
    context = {
        'title': 'Страница не найдена (ошибка 404)',
        'text': '''
        Такой страницы нет. Я за неё.<br>'''
    }
    return render(request, template_name, context=context, status=404)


def handler500(request, *args, **argv):
    context = {
        'title': 'Ошибка сервера (500)',
        'text': '''
        Что-то пошло не так.'''
    }
    template_name = "flatpages/title_and_text.html"
    return render(request, template_name, status=500, context=context)
