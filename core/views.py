from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


@requires_csrf_token
def csrf_failure(request, reason='', exception=None):
    return render(request, 'pages/403csrf.html', status=403)


def error500(request):
    return render(request, 'pages/500.html', status=500)
