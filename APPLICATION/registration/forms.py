from django import forms
from django.forms.fields import CharField, EmailField, ImageField, DecimalField
import re


class RegistrationForm (forms.Form):
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

    def NameSurnameValidation(self, error_text, cd):
        if re.findall(r'\W', cd):
            raise forms.ValidationError(error_text)  # проверка на спецсимволы
        elif re.findall(r'\d', cd):
            raise forms.ValidationError(error_text)  # проверка на цифры
        elif re.findall(r'[QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm]', cd):
            raise forms.ValidationError(error_text)  # проверка на латиницу
        return cd

    def clean_Name(self):
        cd = self.cleaned_data['Name']
        error_text = 'Имя должно содержать только кирелические символы'
        return self.NameSurnameValidation(error_text, cd)

    def clean_Surname(self):
        cd = self.cleaned_data['Surname']
        error_text = 'Фамилия должна содержать только кирелические символы'
        return self.NameSurnameValidation(error_text, cd)

    def PasswordValidation(self, cd):
        if len(cd) < 8:
            raise forms.ValidationError('Пароль должен быть более 8 символов')
        elif re.findall(r'[йцукенгшщзхъфывапролджэячсмитьбюёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ]', cd):
            raise forms.ValidationError('Пароль должен содержать только латиницу')
        elif re.findall(r'\W', cd) == []:
            raise forms.ValidationError('Пароль должен содержать специальные символы')
        elif re.findall(r'\d', cd) == []:
            raise forms.ValidationError('Пароль должен содержать цифры')
        elif re.findall(r'[qwertyuiopasdfghjklzxcvbnm]', cd) == []:
            raise forms.ValidationError('Пароль должен содержать латинские буквы')
        return cd

    def clean_Password1(self):
        cd = self.cleaned_data['Password1']
        return self.PasswordValidation(cd)

    def clean_Password2(self):
        cd = self.cleaned_data['Password2']
        return self.PasswordValidation(cd)

    def clean(self):
        cd = self.cleaned_data
        if len(self['Password1'].errors) != 0 or len(self['Password2'].errors) != 0:
            pass
        elif cd['Password1'] != cd['Password2']:
            print('Пароли не совпадают')
            raise forms.ValidationError('Пароли не совпадают')
