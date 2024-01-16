
from django.shortcuts import render, redirect
from django.views.generic import View
from .models import Post
from .forms import PostForm

# これを使用することでログインが必須になる
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q
from functools import reduce
from operator import and_


class IndexView(View):
    # 最初に呼ばれる関数
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.order_by('-id')
        return render(request, 'app/index.html', {
            'post_data': post_data
        })


class PostDetailView(View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        return render(request, 'app/post_detail.html', {
            'post_data': post_data
        })


class CreatePostView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)
        return render(request, 'app/post_form.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)

        if form.is_valid():
            # バリテーションがokの場合
            # form.cleaned_dataにバリテーション検証済みデータが格納される
            post_data = Post()
            post_data.auther = request.user
            post_data.title = form.cleaned_data['title']

            category = form.cleaned_data['category']
            category_data = Category.objects.get(name=category)
            post_data.category = category_data

            post_data.content = form.cleaned_data['content']

            post_data.content = form.cleaned_data['content']

            if request.FILES:
                post_data.image = request.FILES.get('image')

            post_data.save()
            return redirect('post_detail', post_data.id)

        return render(request, "app/post_form.html", {
            'form': form
        })


class PostEditView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        form = PostForm(request.POST or None,
                        initial={
                            'title': post_data.title,
                            'content': post_data.content,
                            'category': post_data.category,
                            'image': post_data.image,
                        })
        return render(request, 'app/post_form.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)

        if form.is_valid():
            post_data = Post.objects.get(id=self.kwargs['pk'])
            post_data.auther = request.user
            post_data.title = form.cleaned_data['title']
            category = form.cleaned_data['category']
            category_data = Category.objects.get(name=category)
            post_data.category = category_data
            post_data.content = form.cleaned_data['content']
            if request.FILES:
                post_data.image = request.FILES.get('image')

            post_data.save()
            return redirect('post_detail', self.kwargs['pk'])

        return render(request, "app/post_form.html", {
            'form': form
        })


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        return render(request, 'app/post_delete.html', {
            'post_data': post_data
        })

    def post(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        post_data.delete()
        return redirect('index')


class CategoryView(View):
    def get(self, request, *args, **kwargs):
        category_data = Category.objects.get(name=self.kwargs['category'])
        post_data = Post.objects.order_by('-id').filter(category=category_data)
        return render(request, 'app/index.html', {
            'post_data': post_data
        })


class SearchView(View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.order_by('-id')
        keyword = request.GET.get('keyword')

        if keyword:
            exclusion_list = {' ', '　'}
            query_list = ''
            for word in keyword:
                if not word in exclusion_list:
                    query_list += word

            query = reduce(and_, [Q(title__icontains=q) | Q(content__icontains=q) for q in query_list])
            post_data = post_data.filter(query)

        return render(request, 'app/index.html', {
            'keyword': keyword,
            'post_data': post_data
        })
