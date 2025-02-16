from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
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
      'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
      'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
      'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
    }

  def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
      raise ValidationError("Пользователь с таким email уже зарегистрирован.")
    return email

  def save(self, commit=True):
    user = super().save(commit=False)
    user.set_password(self.cleaned_data["password1"])
    if commit:
      user.save()
    return user

class GourmandProfileForm(forms.ModelForm):
  class Meta:
    model = GourmandProfile
    fields = ['description', 'rating', 'image']
    widgets = {
      'description': forms.Textarea(attrs={'class': 'form-control'}),
      'image': forms.FileInput(attrs={'class': 'form-control'}),
    }

class OwnerProfileForm(forms.ModelForm):
  places = forms.ModelMultipleChoiceField(
    queryset=Place.objects.all(),
    widget=forms.CheckboxSelectMultiple,
    required=False,
    label="Выберите заведения"
  )

  class Meta:
    model = OwnerProfile
    fields = ['description', 'places', 'image']
    widgets = {
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


class CustomUserCreationForm(UserCreationForm):
  role = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Выберите роль")

  class Meta:
    model = User
    fields = ('email', 'role', 'password1', 'password2')


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
class PlaceCreateForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'description', 'place_email', 'location', 'rating', 'phone', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'place_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'rating': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
            'class': 'form-control',
            'required': True
            }),
            'image': forms.FileInput(attrs={
            'class': 'form-control',
            'required': True
            }),
        }
        labels = {
            'name': 'Название заведения',
            'description': 'Описание',
            'place_email': 'Е-майл',
            'location': 'Местоположение заведения',
            'rating': 'Рейтинг заведения',
            'phone': 'Телефоны',

        }
#
#
# class EventCreateForm(forms.ModelForm):
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