import datetime as dt

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from userapp.forms import MessageTextForm, RatingForm, RequestCreatingForm
from userapp.models import (Log, Message, Request, ResponsibilityGroup,
                            Service, Work)

User = get_user_model()


class ContextProcessor(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_messages'] = Message.objects.select_related(
            'IDAutor',
            'IDRequest',
            ).filter(IDRecipient=user, Status=False)
        context['user_messages_count'] = context['user_messages'].count()
        context['user_requests'] = Request.objects.filter(
            ~Q(Status='Выполнена'),
            IDAutor=user,
            ).count()
        context['group'] = ResponsibilityGroup.objects.filter(profile__User=user).exists()
        if context['group']:
            context['group_requests'] = Request.objects.filter(
                Q(Status='Новая') | Q(Status='В_работе'),
                IDResponsibilityGroup__profile__User=user,
                ).count()
        context['scope'] = self.kwargs.get('scope')
        context['filter'] = self.kwargs.get('filter')
        context['id_service'] = self.request.GET.get('id_service', 'None')
        if context['id_service'] != 'None':
            context['service_name'] = Service.objects.get(
                id=context['id_service']
                ).Name
        return context


class Index(LoginRequiredMixin, ContextProcessor, TemplateView):
    template_name = 'UserAPP/index.html'


class UserAPP(LoginRequiredMixin, ContextProcessor, ListView):
    context_object_name = 'requests'
    paginate_by = 10
    template_name = 'UserAPP/userapp.html'

    def get(self, request, *args, **kwargs):
        if self.kwargs['scope'] == 'group-requests':
            self.requests = Request.objects.select_related(
                'IDWork',
                'IDAutor',
                'IDExecutor',
                'IDResponsibilityGroup',
                ).filter(IDResponsibilityGroup__profile__User=self.request.user)
        elif self.kwargs['scope'] == 'requests-by-category':
            self.requests = Request.objects.select_related(
                'IDWork',
                'IDAutor',
                'IDExecutor',
                'IDResponsibilityGroup',
                ).filter(IDWork__IDService=self.request.GET['id_service'])
        elif self.kwargs['scope'] == 'all-requests':
            self.requests = Request.objects.select_related(
                'IDWork__IDService',
                'IDAutor',
                'IDExecutor',
                'IDResponsibilityGroup',
                ).order_by("IDWork__IDService__Name")
        else:
            self.requests = Request.objects.select_related(
                'IDWork',
                'IDAutor',
                'IDExecutor',
                'IDResponsibilityGroup',
                ).filter(IDAutor=self.request.user)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.filter = self.kwargs['filter']
        if self.filter == 'Просрочена':
            return self.requests.filter(
                ~Q(Status='Выполнена'),
                DateOfCreation__lt=dt.datetime.now() - F('IDWork__ReactionTime') - F('IDWork__TimeOfExecution')
            )
        else:
            return self.requests.filter(Status=self.filter)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RatingForm()
        context['new_requests'] = self.requests.filter(
                                        Status='Новая'
                                        ).count()
        context['in_work_requests'] = self.requests.filter(
                                        Status='В_работе'
                                        ).count()
        context['on_checking_requests'] = self.requests.filter(
                                        Status='На_проверке'
                                        ).count()
        context['alarm_requests'] = self.requests.filter(
                                        ~Q(Status='Выполнена'),
                                        DateOfCreation__lt=dt.datetime.now() - F('IDWork__ReactionTime') - F('IDWork__TimeOfExecution')
                                        ).count()
        context['finished_requests'] = self.requests.filter(
                                        Status='Выполнена'
                                        ).count()
        return context


class CreateRequest(LoginRequiredMixin, ContextProcessor, TemplateView):
    template_name = 'UserAPP/requestcreating.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        return context


class CreateRequest2(LoginRequiredMixin, ContextProcessor, FormView):
    template_name = 'UserAPP/requestcreating2.html'
    success_url = '/user-app/my-requests/Новая/'
    form_class = RequestCreatingForm

    def get(self, request, *args, **kwargs):
        input_service = request.GET.get('input_service')
        self.works = Work.objects.filter(IDService__Name=input_service).values_list('id', 'Name')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.works = Work.objects.values_list('id', 'Name')
        return super().post(request, *args, **kwargs)

    def get_form(self):
        return self.form_class(self.works, **self.get_form_kwargs())

    def form_valid(self, form):
        cd = form.cleaned_data
        id_work = Work.objects.get(id=cd['InputWork'])
        autor = User.objects.get(username=self.request.user)
        id_responsibility_group = ResponsibilityGroup.objects.get(Default=True)
        new_request = Request(IDWork=id_work,
                              Name=cd['Name'],
                              Сomment=cd['Сomment'],
                              IDAutor=autor,
                              IDResponsibilityGroup=id_responsibility_group)
        new_request.save()
        new_log = Log(Action='Создана заявка', IDRequest=new_request)
        new_log.save()
        return super().form_valid(form)


@require_POST
@login_required
def SetRating(request):
    request_id = request.POST.get('request_id')
    request_item = get_object_or_404(Request, id=request_id)
    Form = RatingForm(request.POST)
    if request.user == request_item.IDAutor and Form.is_valid():
        cd = Form.cleaned_data
        request_item.Rating = cd['Rating']
        request_item.Status = 'Выполнена'
        request_item.save()
        new_log = Log(Action=f'Заявка оценена {request.user} и переведена в состояние "Выполнена"',
                      IDRequest=request_item)
        new_log.save()
    return redirect(request.META.get('HTTP_REFERER'))


class RequestDetail(LoginRequiredMixin, ContextProcessor, DetailView):
    queryset = Request.objects.select_related(
                'IDWork__IDService',
                'IDAutor__Profile',
                'IDExecutor__Profile',
                'IDResponsibilityGroup',
                )
    context_object_name = 'request_detail'
    template_name = 'UserAPP/requestdetail.html'
    template_name_messages = 'UserAPP/requestmessage.html'
    template_name_logs = 'UserAPP/requestlogs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RatingForm()
        context['groups'] = ResponsibilityGroup.objects.all()
        context['messages_count'] = context['request_detail'].messages.count()
        context['page'] = self.request.GET['page']
        if self.kwargs['type'] == 'Messages':
            context['messages_form'] = MessageTextForm()
            context['messages'] = context['request_detail'].messages.select_related('IDAutor', 'IDRecipient')
        if self.kwargs['type'] == 'Logs':
            context['logs'] = Log.objects.filter(IDRequest=context['request_detail'])
        return context

    def get_template_names(self):
        if self.kwargs['type'] == 'Messages':
            return self.template_name_messages
        elif self.kwargs['type'] == 'Logs':
            return self.template_name_logs
        return super().get_template_names()


@require_POST
@login_required
def SetStatus(request):
    request_id = request.POST.get('id')
    request_item = get_object_or_404(Request, id=request_id)
    old_status = request_item.Status
    new_status = request.POST.get('Status')
    if new_status == 'В_работе' and old_status == 'Новая':
        request_item.Rating = None
        request_item.IDExecutor = User.objects.get(username=request.user)
    elif ((new_status == 'В_работе' and old_status == 'На_проверке') or
          (new_status == 'На_проверке' and old_status == 'В_работе') or
          (new_status == 'Выполнена' and old_status == 'На_проверке')):
        pass
    else:
        return redirect(request.META.get('HTTP_REFERER'))
    request_item.Status = new_status
    request_item.save()
    new_log = Log(Action=f'{request.user}: установлен статус "{new_status}"',
                  IDRequest=request_item)
    new_log.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def Excalation(request):
    request_id = request.POST.get('id')
    request_item = get_object_or_404(Request, id=request_id)
    if request.user == request_item.IDExecutor:
        group_id = request.POST.get('group_id')
        group_item = get_object_or_404(ResponsibilityGroup, id=group_id)
        request_item.IDResponsibilityGroup = group_item
        request_item.IDExecutor = None
        request_item.Status = 'Новая'
        request_item.save()
        NewLog = Log(Action=f'Заявка эскалирована {request.user} на "{group_item.Name}"',
                     IDRequest=request_item)
        NewLog.save()
    return redirect(request.META.get('HTTP_REFERER'))


@require_POST
@login_required
def SendMessage(request):
    messages_form = MessageTextForm(request.POST, request.FILES)
    if messages_form.is_valid():
        obj = messages_form.save(commit=False)
        author = request.user
        id = request.GET['id']
        obj.IDRequest = Request.objects.get(id=id)
        obj.IDAutor = author
        obj.save()
    return redirect(request.META.get('HTTP_REFERER'))


class RequestsByCategory (LoginRequiredMixin, ContextProcessor, ListView):
    model = Service
    template_name = 'UserAPP/requests_by_category.html'
    context_object_name = 'services_list'


class AllRequests(UserAPP):
    template_name = 'UserAPP/AllRequests.html'
    paginate_by = 0


@require_POST
@login_required
def CleanMessages(request):
    Message.objects.filter(IDRecipient__username=request.user,
                           Status=False).update(Status=True)
    return redirect(request.META.get('HTTP_REFERER'))
