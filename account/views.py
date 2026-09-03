from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post


class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = "account/user_register.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in!", "info")
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)


    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name,{"form":form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(username=cd["username"], email=cd["email"], password=cd["password"])
            messages.success(request, "Registered Successfully!", "success")
            return redirect("home:home")
        return render(request, self.template_name, {"form":form})


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = "account/user_login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in!", "info")
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form":form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd["email"], password=cd["password"])
            if user is not None:
                login(request, user)
                messages.success(request, "Login Successfully!", "success")
                return redirect("home:home")
            messages.error(request, "username or password is wrong!", "warning")
        return render(request, self.template_name, {"form":form})


class UserLogoutView(LoginRequiredMixin, View):
    #@method_decorator(login_required)
    #login_url = "/account/login/"
    def get(self, request):
        logout(request)
        messages.success(request, "Logout Successfully!", "success")
        return redirect("home:home")


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        posts = Post.objects.filter(user=user)
        return render(request, "account/user_profile.html", {"user":user, "posts":posts})