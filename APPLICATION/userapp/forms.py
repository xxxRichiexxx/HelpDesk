from django import forms
from django.contrib.auth.models import User
from django.db.models import fields
from django.forms.fields import CharField, ChoiceField, FileField

from userapp.models import ResponsibilityGroup, Message


class RequestCreatingForm(forms.Form):
    """Форма создания заявки."""
    InputWork = ChoiceField(
        choices=(),
        required=True,
        label='Вид работ',
        help_text='Выберите вид работ, к которому будет относиться заявка',
        )
    Name = CharField(
        required=True,
        label='Тема',
        help_text='Введите краткую тему заявки',
        )
    Сomment = CharField(
        required=True,
        widget=forms.Textarea(),
        label='Содержание',
        help_text='Введите содержание заявки',
        )

    def __init__(self, work_choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['InputWork'].choices = work_choices

    def clean_Name(self):
        Name = self.cleaned_data['Name']
        if len(Name) < 4:
            raise forms.ValidationError('Слишком короткая тема')
        return Name

    def clean_Сomment(self):
        Comment = self.cleaned_data['Сomment']
        if len(Comment) < 4:
            raise forms.ValidationError('Слишком короткое содержание')
        return Comment

    def clean(self):
        if ResponsibilityGroup.objects.filter(Default=True).count() != 1:
            raise forms.ValidationError(
                'Настройте в админке '
                'группы ответственности. Группа ответственности '
                'с значением default=True может быть только одна.')


class RatingForm (forms.Form):
    """Форма оценки заявки."""
    Rating = ChoiceField(
        choices=(
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
        ),
        widget=forms.RadioSelect(),
        label="Оцените работу по пятибальной шкале"
    )


class MessageTextForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('IDRecipient', 'Text', 'File')
        widgets = {'Text': forms.Textarea(attrs={'rows':3})}
