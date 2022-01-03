from django.shortcuts import render
from registration.forms import RegistrationForm
from registration.models import Profile
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

User = get_user_model()


def registration(request):
    """Выводим форму для регистрации пользователя и валидируем ее."""
    if request.method == 'GET':
        form = RegistrationForm()
        return render(
            request,
            'registration/registration.html',
            {'form': form}
        )
    elif request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
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
        else:
            return render(
                request,
                'registration/registration.html',
                {'form': form}
            )
