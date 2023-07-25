import re
from django.shortcuts import render
from django.urls import reverse
from . models import Post , Tag , Comment, Newsletter
from . forms import CommentForm
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.views.generic import RedirectView
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib import messages
from django.contrib.sites.models import Site

current_site = Site.objects.get_current()
domain = current_site.domain


User = get_user_model()


class BlogSearchView(RedirectView):
    """
    Blog Search View
    """
    template = 'blog/search_blog.html'
    def search(self, search_id):
        context={}
        filter_blogs = Post.objects.all()
        if search_id:
            filter_blogs = filter_blogs.filter(Q(subtitle__icontains=search_id)|Q(tags__name__icontains = search_id)).distinct()
        context['filter_blogs'] = filter_blogs
        return context
     
    def get(self, *args, **kwargs):
        context={}
        search_id = self.request.GET.get('search_id')
        context = self.search(search_id)
        
        return render(self.request,self.template,context)


def is_ajax(request):
    """
    This utility function is used, as `request.is_ajax()` is deprecated.

    This implements the previous functionality. Note that you need to
    attach this header manually if using fetch.
    """
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


class BlogHome(View):    
    template_name = 'blog/blog_home.html'
    def get(self, request):
        tags = request.GET.get('tags')
        tags_list = request.GET.get('tags_list')
        all_tags = Tag.objects.all()
        if tags_list:
            tags_list = str(tags_list).replace('[','').replace(']','').replace('\'','').replace('\"','').replace(',','').split()
            queryset = Post.objects.filter(
                tags__name__in=tags_list,published=1
                ).distinct().order_by('-created_at')
            context = {"queryset":queryset}
        if tags:
            queryset = Post.objects.filter(published=1, tags__name=tags).order_by('-created_at')  
            context = {"queryset":queryset,'all_tags':all_tags}
        else:
            queryset = Post.objects.filter(published=1).order_by('-created_at') 
            context = {"queryset":queryset, 'all_tags':all_tags}
        paginator = Paginator(queryset, per_page=2)
        page_num = int(request.GET.get("page", 1))
        if page_num > paginator.num_pages:
            raise Http404
        queryset = paginator.page(page_num)
        if is_ajax(request):
            return render(request, 'blog/search_blog.html', {'filter_blogs': queryset})
        return render(request, self.template_name, context)
    


def BlogHomeFunction(request):
    return render(request, 'blog/blog_home.html')

def BlogView(request , blog_slug):
    try:
        blog = Post.objects.get(slug=blog_slug)
        previous_post = Post.objects.filter(id=blog.id-1).first()
        next_post = Post.objects.filter(id=blog.id+1).first()
        comments = Comment.objects.filter(post=blog, approved=True)
        latest_posts = Post.objects.all().exclude(slug=blog_slug).order_by('-id')[:3]
        all_tags = Tag.objects.all()
        related_posts = Post.objects.filter(tags__in=blog.tags.all()).distinct().exclude(slug=blog_slug)[:2]
        if request.method == 'POST' and "comment_form" in request.POST:
            text = request.POST.get('text')
            comment_obj = Comment(author=request.user, post_id=blog.id, text=text)
            comment_obj.save()
        elif request.method == 'POST' and "subscribe_blog" in request.POST:
            email = request.POST.get("user_email")
            if email:
                try:
                    newsletter_obj = Newsletter(email = email)
                    newsletter_obj.save()
                    return HttpResponseRedirect(reverse("thankyou"))
                except:
                    messages.success(request, 'You have already subscribed to the newsletters!')
            
        elif request.method == 'POST' and "reply_comment" in request.POST:
            if request.user.is_authenticated:
                comment_id = request.POST.get("comment_id")
                comment = request.POST.get("reply_comment")
                comment_obj = Comment(post_id=blog.id, author=request.user, text=comment,parent_id=comment_id )
                comment_obj.save()
                return HttpResponseRedirect(reverse("blog_view", args=(blog_slug,)))
            else:
                return HttpResponseRedirect("/accounts/login")
        else:
            comment_form = CommentForm()
        page_url = f'{domain}/blog/{blog_slug}'
        return render(request, 'blog/blog_view.html', {'blog':blog,'latest_posts':latest_posts, 'comments':comments,'all_tags':all_tags,'related_posts':related_posts,"previous_post":previous_post,"next_post":next_post, 'page_url':page_url})
    except Post.DoesNotExist:
        return HttpResponseRedirect(reverse("blog_home"))
    except Exception as error:
        raise error
        return HttpResponseRedirect(reverse("blog_view", args=(blog_slug,)))
