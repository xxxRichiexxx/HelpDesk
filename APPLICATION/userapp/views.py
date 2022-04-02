import datetime as dt

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.conf import settings

from .forms import MessageTextForm, RatingForm, RequestCreatingForm
from .models import (Log, Message, Request, ResponsibilityGroup,
                     Service, Work, STATUS_CHOICES)
from userapp.tasks import email

User = get_user_model()


class ContextProcessor(ContextMixin):
    """
    Т.к есть информация, отображающаяся на всех страницах
    (например, количество непрочитанных сообщений и т.п),
    то будем добавлять ее в контекст в данном миксине.
    Далее, от него унаследуем все последующие представления.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # сохраняем в контекст непрочитанные сообщения пользователя
        context['user_messages'] = Message.objects.select_related(
            'IDAuthor',
            'IDRequest',
        ).filter(IDRecipient=user, Status=False)
        # сохраняем в контекст количество непрочитанных сообщений пользователя
        context['user_messages_count'] = context['user_messages'].count()
        # сохраняем в контекст количество незавершенных заявок пользователя
        context['user_requests'] = Request.objects.filter(
            ~Q(Status='completed'),
            IDAuthor=user,
        ).count()
        # сохраняем в контекст булево значение группы ответственности
        # пользователя
        # это используется для скрытия/показа кнопки с заявками группы
        context['group'] = ResponsibilityGroup.objects.filter(
            profile__User=user).exists()
        if context['group']:
            # если пользователь состоит в группе ответственности,
            # то считаем количество заявок на этой группе
            context['group_requests'] = Request.objects.filter(
                Q(Status='new') | Q(Status='in_work'),
                IDResponsibilityGroup__profile__User=user,
            ).count()
        # записываем в контекст такие параметры запроса,
        # как область, фильтр, сервис
        context['scope'] = self.kwargs.get('scope')
        context['filter'] = self.kwargs.get('filter')
        context['id_service'] = self.request.GET.get('id_service', 'None')
        if context['id_service'] != 'None':
            context['service_name'] = Service.objects.get(
                id=context['id_service']
            ).Name
        context['search'] = self.request.GET.get('search')
        return context


class UserAPP(LoginRequiredMixin, ContextProcessor, ListView):
    """
    Формирует перечень завок в зависимости от области видимости
    (пользовательские заявки, заявки группы ответственности, все заявки ...)
    и выбранного фильтра/статуса (в работе и т.п).
    """
    context_object_name = 'requests'
    paginate_by = 10
    template_name = 'UserAPP/userapp.html'

    def get_queryset(self):
        """
        Переопределяем данный метод,
        чтобы получить заявки, относящиеся к заданной области видимости
        и применить к ним фильтрацию.
        """
        basic_query = Request.objects.select_related(
            'IDWork',
            'IDWork__IDService',
            'IDAuthor',
            'IDExecutor',
            'IDResponsibilityGroup',
        )
        if self.kwargs['scope'] == 'group-requests':
            self.requests = basic_query.filter(
                IDResponsibilityGroup__profile__User=self.request.user)
        elif self.kwargs['scope'] == 'requests-by-category':
            self.requests = basic_query.filter(
                IDWork__IDService=self.request.GET['id_service'])
        elif self.kwargs['scope'] == 'all-requests':
            self.requests = basic_query.order_by("IDWork__IDService__Name")
        elif self.kwargs['scope'] == 'i-executor':
            self.requests = basic_query.filter(IDExecutor=self.request.user)
        else:
            self.requests = basic_query.filter(IDAuthor=self.request.user)

        filter_value = self.kwargs['filter']
        if filter_value == 'lost':
            return self.requests.filter(
                Q(Status='new') | Q(Status='in_work'),
                DateOfCreation__lt=dt.datetime.now() -
                F('IDWork__ReactionTime') -
                F('IDWork__TimeOfExecution')
            )
        return self.requests.filter(Status=filter_value)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RatingForm()
        context['new_requests'] = self.requests.filter(
            Status='new'
        ).count()
        context['in_work_requests'] = self.requests.filter(
            Status='in_work'
        ).count()
        context['on_checking_requests'] = self.requests.filter(
            Status='on_check'
        ).count()
        context['alarm_requests'] = self.requests.filter(
            ~Q(Status='completed'),
            DateOfCreation__lt=dt.datetime.now() -
            F('IDWork__ReactionTime') -
            F('IDWork__TimeOfExecution')
        ).count()
        context['finished_requests'] = self.requests.filter(
            Status='completed'
        ).count()
        return context


class CreateRequest(LoginRequiredMixin, ContextProcessor, TemplateView):
    """Первый шаг создания заявки."""
    template_name = 'UserAPP/requestcreating.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        return context


class CreateRequest2(LoginRequiredMixin, ContextProcessor, FormView):
    """Второй шаг создания заявки."""
    template_name = 'UserAPP/requestcreating2.html'
    success_url = '/user-app/my-requests/new/'
    form_class = RequestCreatingForm

    def get(self, request, *args, **kwargs):
        input_service = request.GET.get('input_service')
        self.works = Work.objects.filter(
            IDService__Name=input_service).values_list('id', 'Name')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.works = Work.objects.values_list('id', 'Name')
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return self.form_class(self.works, **self.get_form_kwargs())

    def form_valid(self, form):
        cd = form.cleaned_data
        id_work = Work.objects.get(id=cd['InputWork'])
        author = User.objects.get(username=self.request.user)
        id_responsibility_group = ResponsibilityGroup.objects.get(Default=True)
        new_request = Request(IDWork=id_work,
                              Name=cd['Name'],
                              Comment=cd['Comment'],
                              IDAuthor=author,
                              IDResponsibilityGroup=id_responsibility_group)
        new_request.save()
        new_log = Log(Action='Создана заявка', IDRequest=new_request)
        new_log.save()
        return super().form_valid(form)


class RequestDetail(LoginRequiredMixin, ContextProcessor, DetailView):
    """
    Выводит детализацию по заявке.
    Используются разные шаблоны в зависимости от того,
    выводим мы общую информацию, переписку по заявке или логи заявки.
    """
    queryset = Request.objects.select_related(
        'IDWork__IDService',
        'IDAuthor__Profile',
        'IDExecutor__Profile',
        'IDResponsibilityGroup',
    )
    context_object_name = 'request_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RatingForm()
        context['groups'] = ResponsibilityGroup.objects.all()
        context['messages_count'] = context['request_detail'].messages.count()
        context['page'] = self.request.GET['page']
        if self.kwargs['type'] == 'Messages':
            context['messages_form'] = MessageTextForm()
            context['messages'] = context['request_detail'].messages.select_related(
                'IDAuthor', 'IDRecipient', )
            readed_messages = context['messages'].filter(IDRecipient__username=self.request.user,
                                                         Status=False).update(Status=True)
            context['user_messages_count'] -= readed_messages
        if self.kwargs['type'] == 'Logs':
            context['logs'] = Log.objects.filter(IDRequest=context['request_detail'])
        return context

    def get_template_names(self):
        if self.kwargs['type'] == 'Messages':
            return 'UserAPP/requestmessage.html'
        elif self.kwargs['type'] == 'Logs':
            return 'UserAPP/requestlogs.html'
        return 'UserAPP/requestdetail.html'


@require_POST
@login_required
def set_status(request):
    """Устанавливает статус заявки в пределенном порядке."""
    request_id = request.POST.get('id')
    request_item = get_object_or_404(
        Request.objects.select_related('IDAuthor'),
        id=request_id,
    )
    old_status = request_item.Status
    new_status = request.POST.get('Status')
    # Перевод заявки из состояния "Новая" в состояние "В работе"
    # Сбрасываем рейтинг и записываем исполнителя
    if (new_status == STATUS_CHOICES[1][0] and
            old_status == STATUS_CHOICES[0][0] and
            request.user.Profile.IDResponsibilityGroup):
        request_item.Rating = None
        request_item.IDExecutor = request.user
    # Определяем допустимые переходы статуса заявки. При них не делаем ничего.
    elif ((new_status == STATUS_CHOICES[1][0] and
           old_status == STATUS_CHOICES[2][0] and
           request.user == request_item.IDAuthor) or
          (new_status == STATUS_CHOICES[2][0] and
           old_status == STATUS_CHOICES[1][0] and
           request.user.Profile.IDResponsibilityGroup) or
          (new_status == STATUS_CHOICES[3][0] and
           old_status == STATUS_CHOICES[2][0] and
           request.user.Profile.IDResponsibilityGroup)):
        pass
    # При остальных вариантах переходов состояний делаем редирект.
    else:
        return redirect(request.META.get('HTTP_REFERER'))
    request_item.Status = new_status
    request_item.save()
    new_log = Log(Action=f'{request.user}: установлен статус "{new_status}"',
                  IDRequest=request_item)
    new_log.save()
    try:
        email.delay(
            request_id,
            settings.EMAIL_HOST_USER,
            request_item.IDAuthor.email,
        )
    except Exception:                                   # Добавить логирование
        print('Письмо не отправленою')
    return redirect(request.META.get('HTTP_REFERER'))


@require_POST
@login_required
def excalation(request):
    """Эскалируем заявку."""
    request_id = request.POST.get('id')
    request_item = get_object_or_404(Request, id=request_id)
    if (request.user.Profile.IDResponsibilityGroup == request_item.IDResponsibilityGroup and
            request_item.Status in (STATUS_CHOICES[0][0], STATUS_CHOICES[1][0])):
        group_id = request.POST.get('group_id')
        group_item = get_object_or_404(ResponsibilityGroup, id=group_id)
        request_item.IDResponsibilityGroup = group_item
        request_item.IDExecutor = None
        request_item.Status = 'new'
        request_item.save()
        new_log = Log(Action=f'Заявка эскалирована {request.user} на "{group_item.Name}"',
                      IDRequest=request_item)
        new_log.save()
    return redirect(request.META.get('HTTP_REFERER'))


@require_POST
@login_required
def set_rating(request):
    """Устанавливаем рейтинг(оценку) для заявки."""
    request_id = request.POST.get('request_id')
    request_item = get_object_or_404(Request, id=request_id)
    form = RatingForm(request.POST)
    if request.user == request_item.IDAuthor and form.is_valid():
        cd = form.cleaned_data
        request_item.Rating = cd['Rating']
        request_item.Status = 'completed'
        request_item.DateOfComplete = dt.datetime.now()
        request_item.save()
        new_log = Log(Action=f'Заявка оценена {request.user} и переведена в состояние "Выполнена"',
                      IDRequest=request_item)
        new_log.save()
    return redirect(request.META.get('HTTP_REFERER'))


@require_POST
@login_required
def send_message(request):
    """Отправляем сообщение в окне заявки."""
    messages_form = MessageTextForm(request.POST, request.FILES)
    if messages_form.is_valid():
        obj = messages_form.save(commit=False)
        author = request.user
        id = request.GET['id']
        obj.IDRequest = Request.objects.get(id=id)
        obj.IDAuthor = author
        obj.save()
    return redirect(request.META.get('HTTP_REFERER'))


class RequestsByCategory(LoginRequiredMixin, ContextProcessor, ListView):
    """
    Выводим список предоставляемых сервисов
    и количество неотработанных заявок по ним.
    Количество заявок считаем при рендеринге шаблона
    с помощью специального фильтра.
    """
    template_name = 'UserAPP/requests_by_category.html'
    context_object_name = 'services_list'

    def get_queryset(self):
        queryset = Service.objects.annotate(
            requests_count=Count(
                'works__requests__id',
                filter=Q(works__requests__Status="new") |
                       Q(works__requests__Status="in_work")
            )
        )
        return queryset


class AllRequests(UserAPP):
    """
    Выводим заявки общим списком.
    Работа этого представления не отличается от вышеописанного UserAPP,
    поэтому наследуемся от него и переопределяем пагинацию.
    """
    template_name = 'UserAPP/AllRequests.html'
    paginate_by = 0


@require_POST
@login_required
def clean_messages(request):
    """Переводим все непрочитанные сообщение в состояние прочитано."""
    Message.objects.filter(IDRecipient__username=request.user,
                           Status=False).update(Status=True)
    return redirect(request.META.get('HTTP_REFERER'))
