from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserProfileForm

User = get_user_model()


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        posts = Post.get_published_posts()
        return posts.select_related(
            'author', 'location', 'category').prefetch_related('comments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True)
    posts = Post.get_published_posts().filter(category=category)

    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request, 'blog/category.html', {'category': category,
                                        'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if not request.user.is_authenticated or request.user != post.author:
        post = get_object_or_404(
            Post, id=post_id, is_published=True,
            category__is_published=True, pub_date__lte=timezone.now()
        )

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': post.comments.all(),
        'form': CommentForm(),
    })


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.id])


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        return self.request.user == self.get_object().author


def profile(request, username):
    user = get_object_or_404(User, username=username)

    if request.user == user:
        posts = Post.objects.filter(author=user)
    else:
        posts = Post.get_published_posts().filter(author=user)

    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request, 'blog/profile.html', {'profile': user, 'page_obj': page_obj}
    )


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'registration/registration_form.html', {
        'form': form,
        'is_edit_profile': True,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html', {
        'form': form, 'comment': comment, 'post_id': post_id
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment, 'post_id': post_id
    })
