from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm


def registration(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')
    else:
        form = CustomUserCreationForm()

    return render(
        request, 'registration/registration_form.html', {'form': form}
    )
