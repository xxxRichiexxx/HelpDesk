import re

from django import forms
from django.forms.fields import CharField, EmailField, ImageField, DecimalField
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm (forms.Form):
    """Форма регистраци новго пользователя."""
    Name = CharField(required=True, label="Имя")
    Surname = CharField(required=True, label="Фамилия")
    Department = CharField(required=True, label="Отдел")
    Email = EmailField(required=True, label="Email")
    Phone = DecimalField(required=True, label="Телефон")
    Photo = ImageField(required=False, label='Фото')
    Login = CharField(required=True, label="Логин")
    Password1 = CharField(required=True,
                          widget=forms.PasswordInput(),
                          label="Пароль")
    Password2 = CharField(required=True,
                          widget=forms.PasswordInput(),
                          label="Повторите пароль")

    def name_surname_validation(self, error_text, cd):
        if re.findall(r'\W', cd)\
                or re.findall(r'\d', cd)\
                or re.findall(r'[a-z]', cd):
            raise forms.ValidationError(error_text)  # проверка на спецсимволы
        return cd

    def clean_Name(self):
        cd = self.cleaned_data['Name']
        error_text = 'Имя должно содержать только кирелические символы'
        return self.name_surname_validation(error_text, cd)

    def clean_Surname(self):
        cd = self.cleaned_data['Surname']
        error_text = 'Фамилия должна содержать только кирелические символы'
        return self.name_surname_validation(error_text, cd)

    def password_validation(self, cd):
        if len(cd) < 8:
            raise forms.ValidationError('Пароль должен быть более 8 символов')
        elif re.findall(r'[а-я]', cd):
            raise forms.ValidationError(
                'Пароль должен содержать только латиницу')
        elif not re.findall(r'\W', cd):
            raise forms.ValidationError(
                'Пароль должен содержать специальные символы')
        elif not re.findall(r'\d', cd):
            raise forms.ValidationError('Пароль должен содержать цифры')
        elif not re.findall(r'[a-z]', cd):
            raise forms.ValidationError(
                'Пароль должен содержать латинские буквы')
        return cd

    def clean_Login(self):
        cd = self.cleaned_data['Login']
        user = User.objects.filter(username=cd).exists()
        if user:
            raise forms.ValidationError(
                'Пользователь с таким логином уже существует.')
        return cd

    def clean_Password1(self):
        cd = self.cleaned_data['Password1']
        return self.password_validation(cd)

    def clean_Password2(self):
        cd = self.cleaned_data['Password2']
        return self.password_validation(cd)

    def clean(self):
        cd = self.cleaned_data
        if cd.get('Password1') != cd.get('Password2'):
            raise forms.ValidationError('Пароли не совпадают')
