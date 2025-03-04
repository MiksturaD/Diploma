from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.password_validation import MinimumLengthValidator
from django.core.exceptions import ValidationError

from landing.models import User, Review, Place, Event, OwnerProfile, GourmandProfile


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
    class Meta:
        model = Review
        fields = ['name', 'description', 'place']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'place': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Название отзыва',
            'description': 'Описание',
            'place': 'Заведение',
        }


class PlaceCreateForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'description', 'place_email', 'location', 'rating', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'place_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название заведения',
            'description': 'Описание',
            'place_email': 'Email',
            'location': 'Местоположение',
            'rating': 'Рейтинг',
            'phone': 'Телефон',
        }

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'event_date', 'places']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'places': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super(EventCreateForm, self).__init__(*args, **kwargs)
        self.fields['places'].queryset = Place.objects.all()