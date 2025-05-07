# Импорт модуля forms из Django для создания форм.
from django import forms

# Импорт стандартных форм Django для изменения и создания пользователей.
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

# Импорт библиотеки requests для отправки HTTP-запросов (например, для проверки капчи).
import requests

# Импорт исключения ValidationError для обработки ошибок валидации.
from django.core.exceptions import ValidationError

# Импорт настроек Django для доступа к переменным, таким как ключи капчи.
from django.conf import settings

# Импорт моделей из приложения landing для использования в формах.
from landing.models import User, Review, Place, Event, OwnerProfile, GourmandProfile, NPSTag, NPSResponse


# Класс YandexCaptchaField — кастомное поле формы для интеграции капчи Yandex SmartCaptcha.
class YandexCaptchaField(forms.Field):
    # Метод __init__ инициализирует поле, добавляя скрытый виджет.
    def __init__(self, *args, **kwargs):
        # Устанавливаем виджет HiddenInput, так как капча передаётся через токен.
        kwargs['widget'] = forms.HiddenInput()
        # Вызываем родительский конструктор с переданными аргументами.
        super().__init__(*args, **kwargs)

    # Метод validate проверяет значение токена капчи.
    def validate(self, value):
        # Вызываем родительский метод валидации для базовых проверок.
        super().validate(value)
        # Проверяем, что токен капчи не пустой.
        if not value:
            print("DEBUG: Captcha value is empty")
            raise forms.ValidationError("Пожалуйста, пройдите проверку капчи.")
        try:
            # Отправляем POST-запрос на сервер Yandex для проверки токена.
            response = requests.post(
                'https://smartcaptcha.yandexcloud.net/validate',
                data={
                    'secret': settings.YANDEX_CAPTCHA_SERVER_KEY,  # Секретный ключ из настроек.
                    'token': value,  # Токен капчи, переданный из формы.
                },
                timeout=5  # Устанавливаем таймаут в 5 секунд для запроса.
            )
            # Проверяем, нет ли HTTP-ошибок в ответе.
            response.raise_for_status()
            # Парсим JSON-ответ от сервера капчи.
            result = response.json()
            print("DEBUG: CAPTCHA API response:", result)
            # Проверяем, что статус ответа 'ok', иначе капча не пройдена.
            if result.get('status') != 'ok':
                print("DEBUG: CAPTCHA validation failed")
                raise forms.ValidationError("Ошибка проверки капчи. Попробуйте снова.")
        except requests.RequestException as e:
            # Обрабатываем ошибки запроса (например, проблемы с сетью).
            print("DEBUG: CAPTCHA API request failed:", str(e))
            raise forms.ValidationError("Ошибка связи с сервером капчи.")


# Класс SignupForm — форма для регистрации пользователей, наследуется от UserCreationForm.
class SignupForm(UserCreationForm):
    # Поле role — выбор роли пользователя (гурман или владелец).
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,  # Варианты ролей из модели User.
        widget=forms.Select(attrs={'class': 'form-control'}),  # Виджет выбора с классом Bootstrap.
        label="Выберите роль"  # Метка поля.
    )
    # Поле captcha — кастомное поле для проверки Yandex SmartCaptcha.
    captcha = YandexCaptchaField(required=True)

    # Метакласс Meta определяет настройки формы.
    class Meta:
        model = User  # Указываем модель, с которой работает форма.
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'role']  # Поля формы.
        widgets = {
            # Настройки виджетов для полей формы с классами Bootstrap.
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'floatingTitle',
                'placeholder': 'Имя',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'floatingLastname',
                'aria-label': 'Фамилия',
                'placeholder': 'Фамилия',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'floatingEmail',
                'placeholder': 'Почта',
                'required': True
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'id': 'password1',
                'aria-label': 'Пароль',
                'placeholder': 'Пароль',
                'required': True
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'id': 'password2',
                'aria-label': 'Подтверждение пароля',
                'placeholder': 'Подтвердите пароль',
                'required': True
            }),
        }

    # Метод __init__ инициализирует форму и добавляет атрибуты для капчи.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Закомментированные строки для добавления атрибутов капчи (если нужно).
        # self.fields['captcha'].widget.attrs['class'] = 'yandex-captcha'
        # self.fields['captcha'].widget.attrs['data-sitekey'] = settings.YANDEX_CAPTCHA_CLIENT_KEY

    # Метод clean_email проверяет уникальность email.
    def clean_email(self):
        # Получаем очищенные данные email.
        email = self.cleaned_data.get('email')
        # Проверяем, существует ли пользователь с таким email.
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    # Метод save сохраняет пользователя с дополнительными полями.
    def save(self, commit=True):
        # Получаем объект пользователя без сохранения в базе.
        user = super().save(commit=False)
        # Устанавливаем значения полей из формы.
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        # Если commit=True, сохраняем пользователя в базе.
        if commit:
            user.save()
        return user


# Класс GourmandProfileForm — форма для редактирования профиля гурмана.
class GourmandProfileForm(forms.ModelForm):
    # Метакласс Meta определяет настройки формы.
    class Meta:
        model = GourmandProfile  # Указываем модель, с которой работает форма.
        fields = ['description', 'rating', 'image']  # Поля формы.
        widgets = {
            # Настройки виджетов для полей формы с классами Bootstrap.
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Опишите себя'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10, 'step': '0.1'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


# Класс OwnerProfileForm — форма для редактирования профиля владельца.
class OwnerProfileForm(forms.ModelForm):
    # Метакласс Meta определяет настройки формы.
    class Meta:
        model = OwnerProfile  # Указываем модель, с которой работает форма.
        fields = ['description', 'places', 'image']  # Поля формы.
        widgets = {
            # Настройки виджетов для полей формы с классами Bootstrap.
            'places': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # Метод __init__ инициализирует форму и устанавливает начальные значения для поля places.
    def __init__(self, *args, **kwargs):
        super(OwnerProfileForm, self).__init__(*args, **kwargs)
        # Если профиль уже существует, устанавливаем начальные значения для связанных мест.
        if self.instance.pk:
            self.fields['places'].initial = self.instance.places.all()

    # Метод save сохраняет профиль и обновляет связанные места.
    def save(self, commit=True):
        # Получаем объект профиля без сохранения в базе.
        instance = super().save(commit=False)
        # Если commit=True, сохраняем профиль и обновляем связанные места.
        if commit:
            instance.save()
            # Устанавливаем новые связанные места из формы.
            instance.places.set(self.cleaned_data['places'])
        return instance


# Класс CustomUserChangeForm — форма для изменения данных пользователя.
class CustomUserChangeForm(UserChangeForm):
    # Метакласс Meta определяет настройки формы.
    class Meta:
        model = User  # Указываем модель, с которой работает форма.
        fields = ['first_name', 'last_name', 'email']  # Поля формы.


# Класс ReviewCreateForm — форма для создания отзыва с NPS-оценкой.
class ReviewCreateForm(forms.ModelForm):
    # Поле nps_score — оценка NPS от 0 до 10.
    nps_score = forms.IntegerField(
        label="Насколько вы порекомендуете данное заведение своим друзьям, коллегам, родственникам (0-10)",
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '10', 'step': '1', 'class': 'form-range'}),
        initial=5  # Начальное значение по центру.
    )
    # Поле nps_tags — выбор тегов NPS, необязательное.
    nps_tags = forms.ModelMultipleChoiceField(
        label="Что повлияло на вашу оценку?",
        queryset=NPSTag.objects.all(),  # Получаем все теги из базы.
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    # Метакласс Meta определяет настройки формы.
    class Meta:
        model = Review  # Указываем модель, с которой работает форма.
        fields = ['name', 'description', 'place', 'gourmand_rating']  # Поля формы.
        widgets = {
            # Настройки виджетов для полей формы с классами Bootstrap.
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'place': forms.Select(attrs={'class': 'form-select'}),
            'gourmand_rating': forms.Select(
                attrs={'class': 'form-control'},
                choices=[(i, str(i)) for i in range(1, 6)]  # Варианты оценки от 1 до 5.
            ),
        }
        labels = {
            'name': 'Название отзыва',
            'description': 'Описание',
            'place': 'Заведение',
            'gourmand_rating': 'Оценка',
        }

    # Метод save сохраняет отзыв и создаёт связанный объект NPS.
    def save(self, commit=True):
        # Получаем объект отзыва без сохранения в базе.
        review = super().save(commit=False)
        # Если commit=True, сохраняем отзыв и создаём NPS.
        if commit:
            review.save()
            # Создаём объект NPSResponse с оценкой и тегами.
            nps = NPSResponse.objects.create(
                review=review,
                score=self.cleaned_data['nps_score'],
            )
            nps.tags.set(self.cleaned_data['nps_tags'])
        return review


# Класс PlaceCreateForm — форма для создания заведения.
class PlaceCreateForm(forms.ModelForm):
    # Метакласс Meta определяет настройки формы.
    class Meta:
        model = Place  # Указываем модель, с которой работает форма.
        fields = ['name', 'description', 'place_email', 'location', 'phone', 'website']  # Поля формы.
        widgets = {
            # Настройки виджетов для полей формы с классами Bootstrap.
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'place_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'example.com'}),
        }
        labels = {
            'name': 'Название заведения',
            'description': 'Описание',
            'place_email': 'Email',
            'location': 'Местоположение',
            'phone': 'Телефон',
            'website': 'Сайт',
        }


# Класс EventCreateForm — форма для создания мероприятия.
class EventCreateForm(forms.ModelForm):
    # Метакласс Meta определяет настройки формы.
    class Meta:
        model = Event  # Указываем модель, с которой работает форма.
        fields = ['name', 'description', 'event_date', 'place', 'is_weekly', 'day_of_week']  # Поля формы.
        widgets = {
            # Настройки виджетов для полей формы с классами Bootstrap.
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'event_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'place': forms.Select(attrs={'class': 'form-control'}),
            'is_weekly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
        }

    # Метод clean выполняет кастомную валидацию формы.
    def clean(self):
        # Получаем очищенные данные.
        cleaned_data = super().clean()
        is_weekly = cleaned_data.get('is_weekly')
        day_of_week = cleaned_data.get('day_of_week')
        event_date = cleaned_data.get('event_date')

        # Проверяем логику для еженедельных событий.
        # Если событие еженедельное, day_of_week обязателен.
        if is_weekly and day_of_week is None:
            self.add_error('day_of_week', 'Укажите день недели для еженедельного события.')
        # Если событие не еженедельное, day_of_week должен быть None.
        elif not is_weekly and day_of_week is not None:
            self.add_error('day_of_week', 'День недели указывается только для еженедельных событий.')
        # Если событие не еженедельное, event_date обязателен.
        if not is_weekly and not event_date:
            self.add_error('event_date', 'Укажите дату события для не еженедельного события.')
        # Если событие еженедельное, event_date не нужен.
        elif is_weekly and event_date:
            self.add_error('event_date', 'Дата события не указывается для еженедельных событий.')

        return cleaned_data