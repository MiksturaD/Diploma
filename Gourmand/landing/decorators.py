from django.http import HttpResponseForbidden

def gourmand_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_gourmand():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Доступ только для гурманов")
    return wrapper

def owner_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_owner():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Доступ только для владельцев заведений")
    return wrapper
