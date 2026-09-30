from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.context_processors import request
from django.views import View
from .models import Post, Comment, Vote
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import PostCreateUpdateForm, CommentCreateForm, CommentReplyForm, PostSearchForm
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, RedirectView, ListView, DetailView, FormView, CreateView, DeleteView
from django.urls import reverse_lazy, reverse


class HomeView(ListView):
    form_class = PostSearchForm
    template_name = "home/index.html"
    #model = Post #object_list
    #queryset = Post.objects.filter(id__lte=200)
    # ordering = "created"
    context_object_name = "posts"
    allow_empty = True

    def get_queryset(self):
        result = Post.objects.all()
        if self.request.GET.get("search"):
            result = result.filter(body__icontains=self.request.GET["search"])
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context



class Home2View(View):
    form_class = PostSearchForm
    http_method_names = ["get", "options"]

    def get(self, request):
        posts = Post.objects.all()
        if request.GET.get("search"):
            posts = posts.filter(body__icontains=request.GET["search"])
        return render(request, "home/index.html", {"posts": posts, "form": self.form_class()})

    def options(self, request, *args, **kwargs):
        response = super().options(request, *args, **kwargs)
        response.headers["host"] = "localhost"
        response.headers["user"] = request.user
        return response

    def http_method_not_allowed(self, request, *args, **kwargs):
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, "method_not_allowed.html", status=405)

#
# class PostDetailView(DetailView):
#     model = Post #object | Post
#     template_name = "home/detail.html"
#     #context_object_name = "anything"
#     pk_url_kwarg = "post_id"
#     slug_url_kwarg = "post_slug"
#     #slug_field = "body"
#     #queryset = Post.objects.filter(id__lte=3)
#
#     def get_queryset(self):
#         if self.request.user.is_staff:
#             return Post.objects.filter(id=self.kwargs["post_id"])
#         else:
#             return Post.objects.none()
#     context_object_name = "post"
#     def get_object(self, queryset=None):
#         return Post.objects.get(title = self.kwargs["title"])
#     zamani ke nemikhay ba slug va id kar koni aslan




class PostDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, id=kwargs["post_id"], slug=kwargs["post_slug"])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        comments = self.post_instance.pcomments.filter(is_reply=False)
        has_liked = False
        if request.user.is_authenticated and self.post_instance.has_user_liked(request.user):
            has_liked = True

        return render(request, "home/detail.html", {"post": self.post_instance,
                                                    "comments": comments,"form": self.form_class(),
                                                    "reply_form": self.form_class_reply(),
                                                    "has_liked": has_liked})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = self.post_instance
            new_comment.save()
            messages.success(request, "Comment Saved Successfully!", "success")
            return redirect("home:post_detail", self.post_instance.id, self.post_instance.slug)



class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post #<model>_confirm_delete.html
    success_url = reverse_lazy("home:home")
    template_name = "home/delete.html"
    pk_url_kwarg = "post_id"

    def form_valid(self, form):
        if self.object.user.id != self.request.user.id:
            messages.error(self.request, "You can't delete this post!", "danger")
            return redirect("home:home")
        return super().form_valid(form)




class PostDelete2View(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if post.user.id == request.user.id:
            post.delete()
            messages.success(request, "Post Deleted Successfully!", "success")
        else:
            messages.error(request, "You can't delete this post!", "danger")
        return redirect("home:home")


class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs["post_id"])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if post.user.id != request.user.id:
            messages.error(request, "You can't update this post!", "danger")
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, "home/update.html", {"form": form})

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.slug = slugify(form.cleaned_data["body"][:30])
            updated_post.save()
            messages.success(request, "Post Updated Successfully!", "success")
            return redirect("home:post_detail", updated_post.id, updated_post.slug)




class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["body"]
    template_name = "home/create.html"

    def form_valid(self, form):
        form.instance.slug = slugify(form.cleaned_data["body"][:30])
        form.instance.user = self.request.user

        messages.success(self.request, "Post Created Successfully!", "success")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "home:post_detail",
            kwargs={
                "post_id": self.object.id,
                "post_slug": self.object.slug
            }
        )



class PostCreate3View(LoginRequiredMixin, FormView):
    template_name = "home/create.html"
    form_class = PostCreateUpdateForm

    def form_valid(self, form):
        self.object = self._create_post(form)
        return super().form_valid(form)

    def _create_post(self, form):
        post = form.save(commit=False)
        post.slug = slugify(form.cleaned_data["body"][:30])
        post.user = self.request.user
        post.save()
        messages.success(self.request, "Post Created Successfully!", "success")
        return post

    def get_success_url(self):
        return reverse("home:post_detail",
                       kwargs={
                           "post_id": self.object.id,
                           "post_slug": self.object.slug
                                                   }
                       )





class PostCreate2View(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def get(self, request, *args, **kwargs):
        return render(request, "home/create.html", {"form": self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data["body"][:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, "Post Created Successfully!", "success")
            return redirect("home:post_detail", new_post.id, new_post.slug)




class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            is_reply = True
            reply.save()
            messages.success(request, "Reply Added Successfully!", "success")
        return redirect("home:post_detail", post.id, post.slug)


class PostLikeView(LoginRequiredMixin, View):

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like = Vote.objects.filter(post=post, user=request.user)
        if like.exists():
            messages.error(request, "You have already liked this post!", "warning")
        else:
            Vote.objects.create(post=post, user=request.user)
            messages.success(request, "Liked Successfully!", "success")
        return redirect("home:post_detail", post.id, post.slug)


class AboutView(TemplateView):
    template_name = "home/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user.username
        return context


class ContactView(RedirectView):
    #url = "https://mongard.ir/"
    # url = "/about/%(id)i/%(name)s/"
    pattern_name = "home:about"
    permanent = True
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        print("="*90)
        print(kwargs["id"], kwargs["name"])
        kwargs.pop("id")
        kwargs.pop("name")
        return super().get_redirect_url(*args, **kwargs)