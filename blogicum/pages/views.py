from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('blog:index'))
    else:
        form = UserCreationForm()
    return render(
        request,
        'registration/registration_form.html',
        {'form': form}
    )
