from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

from registration.forms import RegistrationForm
from registration.models import Profile
from userapp.views import ContextProcessor

User = get_user_model()


@require_http_methods(["GET", "POST"])
def registration(request):
    """
    Выводим форму для регистрации пользователя и валидируем ее.
    Реализовано через FBV в учебных целях.
    """
    form = RegistrationForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        cd = form.cleaned_data
        user = User.objects.create_user(
                                        username=cd['Login'],
                                        password=cd['Password1'],
                                        first_name=cd['Name'],
                                        last_name=cd['Surname'],
                                        email=cd['Email']
                                        )
        profile = Profile(User=user,
                          Department=cd['Department'],
                          Phone=cd['Phone'],
                          Photo=cd['Photo'])
        user.save()
        profile.save()
        return redirect('authentication:login')
    return render(
        request,
        'registration/registration.html',
        {'form': form}
    )


class ProfileView(ContextProcessor, TemplateView):
    template_name = 'registration/profile.html'
