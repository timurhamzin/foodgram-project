from django.shortcuts import render
from django.views.generic import TemplateView


class FlatPage404(TemplateView):
    template_name = 'recipe/flatpages/title_and_text.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Страница не найдена'
        context['text'] = '''
            Такой страницы нет. Я за неё.<br>
        '''
        return context


class FlatPage500(TemplateView):
    template_name = 'recipe/flatpages/title_and_text.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ошибка сервера'
        context['text'] = '''
            Что-то пошло не так. Напишите мне, контакты по ссылке "Об авторе".
        '''
        return context


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
