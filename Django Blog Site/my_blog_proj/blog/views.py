from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm


class AboutView(TemplateView):
    template_name = 'about.html'
    

class PostListView(ListView):
    model = Post
    
    def get_queryset(self):
        """Lets us sort posts in descending order; that is the newest post will appear first"""
        return Post.objects.filter(published_date__lte = timezone.now()).order_by('-published_date')
    
    
class PostDetailView(DetailView):
    model = Post
    
    
class PostCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    
    form_class = PostForm
    
    model = Post
    

class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    
    form_class = PostForm
    
    model = Post
    

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')
    
    
class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'
    
    model = Post
    
    def get_queryset(self):
        """Returns list of post without publication date - these will be called drafts"""
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')
    
    
@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            # Make that comment linked to the post itself
            comment.post = post
            comment.save()
            
            return redirect('post_detail', pk=post.pk)
        
    else:
        form = CommentForm()
    
    return render(request, 'blog/comment_form.html', {'form': form})

@login_required
def approve_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # It calls method set in the Comment model
    comment.approve()
    
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def remove_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Saving pk to another variable to avoid losing the pk required for redirect
    post_pk = comment.post.pk
    
    comment.delete()
    
    return redirect('post_detail', pk=post_pk)

@login_required
def publish_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    post.publish()
    
    return redirect('post_detail', pk=pk)