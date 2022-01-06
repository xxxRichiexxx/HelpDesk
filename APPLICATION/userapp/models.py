from django.contrib.auth.models import User
from django.db.models import (CharField, ImageField, ForeignKey,
                              IntegerField, DurationField, DateTimeField,
                              BooleanField, Model, CASCADE, FileField)

STATUS_CHOICES = (
    ('new', 'Новая'),
    ('in_work', 'В работе'),
    ('on_check', 'На проверке'),
    ('completed', 'Выполнена'),
)


class Service(Model):
    """Модель, описывающая предоставляемые сервисы."""
    Name = CharField(max_length=100, verbose_name="Название")
    Image = ImageField(null=True, blank=True)

    def __str__(self):
        return self.Name

    class Meta:
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'


class ResponsibilityGroup(Model):
    """Модель, хрянящая группы ответственности."""
    Name = CharField(max_length=100)
    Default = BooleanField()

    def __str__(self):
        return self.Name

    class Meta:
        verbose_name = 'Группа ответственности'
        verbose_name_plural = 'Группы ответственности'


class Work(Model):
    """Модель, хранящая виды работ в рамках предоставляемых сервисов."""
    IDService = ForeignKey(Service, on_delete=CASCADE, related_name='works')
    Name = CharField(max_length=100, verbose_name="Название")
    TYPE_CHOICES = (('Инцедент', 'Инцедент'),
                    ('Запрос на обслуживание', 'Запрос на обслуживание'))
    Type = CharField(max_length=30,
                     choices=TYPE_CHOICES,
                     verbose_name="Тип")
    Сomplexity = IntegerField(verbose_name="Сложность")
    ReactionTime = DurationField(verbose_name="Время реакции,ч")
    TimeOfExecution = DurationField(verbose_name="Время выполненияб,ч")

    def __str__(self):
        return self.Name

    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'


class Request(Model):
    """Модель, хранящая заявки(запросы)."""
    IDWork = ForeignKey(
        Work,
        on_delete=CASCADE,
        verbose_name='Работа',
        help_text='Выберите вид работ, к которому относится заявка',
        )
    DateOfCreation = DateTimeField(auto_now_add=True)
    DateOfComplete = DateTimeField(blank=True, null=True)
    Name = CharField(
        max_length=100,
        verbose_name='Тема',
        help_text='Введите тему заявки, описывающую суть проблемы/запроса',
        )
    Сomment = CharField(
        max_length=1000,
        verbose_name='Содержание заявки',
        help_text='Введите детальное описание проблемы',
        )
    IDAutor = ForeignKey(
        User,
        related_name='autor_requests',
        on_delete=CASCADE,
        verbose_name='Автор',
        help_text='Выберите автора заявки',
        )
    IDExecutor = ForeignKey(
        User,
        related_name='executor_requests',
        null=True,
        blank=True,
        on_delete=CASCADE,
        verbose_name='Исполнитель',
        help_text='Выберите исполнителя заявки',
        )
    Status = CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус',
        help_text='Выберите текущий статус заявки',
        )
    RATING_CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
    Rating = IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name='Оценка',
        help_text='Оцените работу по заявке от 1 до 5 (5 - отлично)',)
    IDResponsibilityGroup = ForeignKey(
        ResponsibilityGroup,
        on_delete=CASCADE,
        verbose_name='Группа ответственности',
        help_text='Выберите группу ответственности, в которую попадет заявка',
        )

    def __str__(self):
        return f'{self.IDAutor}: {self.Name}'

    class Meta:
        ordering = ["-DateOfCreation"]
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        default_related_name = 'requests'


class Message (Model):
    """Модель, хранящая переписку в рамках одной заявки."""
    IDRequest = ForeignKey(
        Request,
        on_delete=CASCADE,
        related_name='messages',
        verbose_name='Заявка',
        help_text='Выберите заявку, к которой относится сообщение',
        )
    Text = CharField(
        max_length=1000,
        verbose_name='Текст сообщения',
        help_text='Введите текст сообщения',
        )
    Data = DateTimeField(auto_now=True)
    IDAutor = ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=CASCADE,
        related_name='autor_messages',
        verbose_name='Автор',
        help_text='Выберите автора сообщения',
        )
    IDRecipient = ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=CASCADE,
        related_name='recipient_messages',
        verbose_name='Получатель',
        help_text='Выберите получателя сообщения',
        )
    File = FileField(
        null=True,
        blank=True,
        verbose_name='Файл')
    Status = BooleanField(
        null=True,
        blank=True,
        default=False,
        verbose_name='Статус',
        help_text='Выберите статус сообщения '
                  '(прочитано оно получателем или нет)',
        )

    def __str__(self):
        return f'Заявка "{self.IDRequest}": {self.Text[:20]}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Log (Model):
    """Модель, хранящая логи(события) в рамках каждой из заявок."""
    Action = CharField(max_length=100, null=True, blank=True)
    Date = DateTimeField(auto_now=True)
    IDRequest = ForeignKey(Request, on_delete=CASCADE)

    def __str__(self):
        return self.Action

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'
