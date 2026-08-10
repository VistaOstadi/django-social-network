from django.shortcuts import render
from django.views import View
from .forms import UserRegisterForm

class UserRegisterView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, "account/user_register.html",{"form":form})

    def post(self, request):
        pass