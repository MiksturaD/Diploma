from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.password_validation import MinimumLengthValidator
from django.core.exceptions import ValidationError

from landing.models import User, Review, Place, Event, OwnerProfile, GourmandProfile, NPSTag, NPSResponse


class SignupForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Выберите роль"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'role']
        widgets = {
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user

class GourmandProfileForm(forms.ModelForm):
    class Meta:
        model = GourmandProfile
        fields = ['description', 'rating', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Опишите себя'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10, 'step': '0.1'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class OwnerProfileForm(forms.ModelForm):
    class Meta:
        model = OwnerProfile
        fields = ['description', 'places', 'image']
        widgets = {
            'places': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
      super(OwnerProfileForm, self).__init__(*args, **kwargs)
      if self.instance.pk:
        self.fields['places'].initial = self.instance.places.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
          instance.save()
          # Обновляем связанные места
          instance.places.set(self.cleaned_data['places'])
        return instance

class CustomUserChangeForm(UserChangeForm):
  class Meta:
      model = User
      fields = ['first_name', 'last_name', 'email']



class ReviewCreateForm(forms.ModelForm):
    nps_score = forms.IntegerField(
        label="Насколько вы порекомендуете данное заведение своим друзьям, коллегам, родственникам (0-10)",
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '10', 'step': '1', 'class': 'form-range'}),
        initial=5  # Начальное значение по центру
    )
    nps_tags = forms.ModelMultipleChoiceField(
        label="Что повлияло на вашу оценку?",
        queryset=NPSTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = Review
        fields = ['name', 'description', 'place', 'gourmand_rating']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'place': forms.Select(attrs={'class': 'form-select'}),
            'gourmand_rating': forms.Select(
                attrs={'class': 'form-control'},
                choices=[(i, str(i)) for i in range(1, 6)]
            ),
        }
        labels = {
            'name': 'Название отзыва',
            'description': 'Описание',
            'place': 'Заведение',
            'gourmand_rating': 'Оценка',
        }

    def save(self, commit=True):
        review = super().save(commit=False)
        if commit:
            review.save()
            nps = NPSResponse.objects.create(
                review=review,
                score=self.cleaned_data['nps_score'],
            )
            nps.tags.set(self.cleaned_data['nps_tags'])
        return review


class PlaceCreateForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'description', 'place_email', 'location', 'phone', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'place_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        }
        labels = {
            'name': 'Название заведения',
            'description': 'Описание',
            'place_email': 'Email',
            'location': 'Местоположение',
            'phone': 'Телефон',
            'website':'Сайт',
        }

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'event_date', 'place','is_weekly', 'day_of_week']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'event_date': forms.DateTimeInput(attrs={'class': 'form-control','type': 'datetime-local'}),
            'place': forms.Select(attrs={'class': 'form-control'}),
            'is_weekly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
        }

