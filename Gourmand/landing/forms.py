from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

from landing.models import User, Review, Place, Event



class SignupForm(forms.ModelForm):
  confirm_password = forms.CharField(
    widget=forms.PasswordInput(attrs={
      'class': 'form-control',
      'id': 'floatingPasswordConfirm',
      'placeholder': 'Подтверждение пароля',
      'required': True
    })
  )

  role = forms.ChoiceField(
    choices=User.ROLE_CHOICES,
    widget=forms.Select(attrs={
      'class': 'form-control',
      'id': 'floatingRole',
      'required': True
    })
  )

  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'username', 'email', 'password', 'role']
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
      'username': forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'floatingUsername',
        'placeholder': 'Логин пользователя',
        'aria-label': 'Логин пользователя',
        'required': True
      }),
      'email': forms.EmailInput(attrs={
        'class': 'form-control',
        'id': 'floatingEmail',
        'placeholder': 'Почта',
        'required': True
      }),
      'password': forms.PasswordInput(attrs={
        'class': 'form-control',
        'id': 'floatingPassword',
        'placeholder': 'Пароль',
        'required': True
      }),
    }

  def clean_email(self):
    email = self.cleaned_data.get("email")
    if User.objects.filter(email=email).exists():
      raise ValidationError("Этот email уже зарегистрирован.")
    return email

  def clean_username(self):
    username = self.cleaned_data.get("username")
    if User.objects.filter(username=username).exists():
      raise ValidationError("Этот логин уже занят.")
    return username

  def clean(self):
    cleaned_data = super().clean()
    password = cleaned_data.get("password")
    confirm_password = cleaned_data.get("confirm_password")

    if password and confirm_password and password != confirm_password:
      raise ValidationError("Пароли не совпадают!")

    return cleaned_data

  def save(self, commit=True):
    user = super().save(commit=False)
    user.set_password(self.cleaned_data["password"])  # Хешируем пароль!
    if commit:
      user.save()
    return user

class CustomUserChangeForm(UserChangeForm):
  class Meta:
      model = User
      fields = ['first_name', 'last_name', 'username', 'email']


class CustomUserCreationForm(UserCreationForm):
  role = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Выберите роль")

  class Meta:
    model = User
    fields = ('username', 'email', 'role', 'password1', 'password2')


# class ReviewCreateForm(forms.ModelForm):
#     class Meta:
#         model = Review
#         fields = ['name', 'review_date', 'description', 'place']
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#             'review_date': forms.DateField(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#             'description': forms.TextInput(attrs={
#                 'class': 'form-select',
#                 'required': True
#             }),
#             'place': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#         }
#         labels = {
#             'name': 'Название отзыва',
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(ReviewCreateForm, self).__init__(*args, **kwargs)
#         self.fields['name'].widget.attrs.update({'aria-label': 'Название отзыва'})
#         self.fields['review_date'].widget.attrs.update({'aria-label': 'Дата отзыва'})
#         self.fields['description'].widget.attrs.update({'aria-label': 'Детали отзыва'})
#         self.fields['place'].widget.attrs.update({'aria-label': 'Наименование заведения'})
#
#
# class PlaceCreateForm(forms.ModelForm):
#     class Meta:
#         model = Place
#         fields = ['name', 'description', 'place_email', 'location', 'rating']
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#             'description': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#             'place_email': forms.EmailInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#             'location': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#             'rating': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#         }
#         labels = {
#             'name': 'Название отзыва',
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(PlaceCreateForm, self).__init__(*args, **kwargs)
#         self.fields['name'].widget.attrs.update({'aria-label': 'Название отзыва'})
#         self.fields['description'].widget.attrs.update({'aria-label': 'Описание заведения'})
#         self.fields['place_email'].widget.attrs.update({'aria-label': 'Емайл заведения'})
#         self.fields['location'].widget.attrs.update({'aria-label': 'Адрес заведения'})
#         self.fields['rating'].widget.attrs.update({'aria-label': 'Рейтинг заведения'})
#
#
# class EvenCreateForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = ['name', 'description', 'place']
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#             'description': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#             'place': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#         }
#         labels = {
#             'name': 'Название ивента',
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(EvenCreateForm, self).__init__(*args, **kwargs)
#         self.fields['name'].widget.attrs.update({'aria-label': 'Название ивента'})
#         self.fields['description'].widget.attrs.update({'aria-label': 'Описание ивента'})
#         self.fields['place'].widget.attrs.update({'aria-label': 'Наименование заведения в котором будет ивент'})