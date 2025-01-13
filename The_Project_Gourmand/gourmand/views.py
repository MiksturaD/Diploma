from django.shortcuts import render

def index(request):
  #category_list = Category.objects.all()
  return render(request, 'gourmand/index.html')#, context={'categories': category_list})


def main(request):
  return None


def edit_profile(request):
  return None


def signup(request):
  return None


def signin(request):
  return None


def signout(request):
  return None


def profile(request):
  return None


def events(request):
  return None


def event(request):
  return None


def create_event(request):
  return None


def places(request):
  return None


def place(request):
  return None


def create_places(request):
  return None


def reviews(request):
  return None


def review(request):
  return None


def create_review(request):
  return None