from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import Board, Topic, Post
from django.contrib.auth.models import User
from .forms import NewTopicForm, PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView, ListView, DeleteView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse_lazy


# def home(request):
#     boards = Board.objects.all()
#     # boards_names = []
#     # for board in boards:
#     #     boards_names.append(board.name)
#     # print(boards_names)
#     # response_html = '<br>'.join(boards_names)
#     return render(request, 'home.html', {'boards': boards})


# other way from method home :)
class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


def board_topics(request, id):
    # try:
    #     board = Board.objects.get(id=id)
    # except Board.DoesNotExist:
    #     raise Http404
    board = get_object_or_404(Board, id=id)
    print(board)
    queryset = board.topics.order_by('-created_dt').annotate(comments=Count('posts'))
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 3)
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)
    return render(request, 'topics.html', {'board': board, 'topics': topics})


# def new_topic(request, id):
#     board = get_object_or_404(Board, id=id)
#     if request.method == 'POST':
#         subject = request.POST['subject']
#         message = request.POST['message']
#         user = User.objects.first()
#         topic = Topic.objects.create(
#             subject=subject,
#             board=board,
#             created_by=user
#         )
#         post = Post.objects.create(
#             message=message,
#             topic=topic,
#             created_by=user
#         )
#         return redirect('board_topics', id=board.id)
#     return render(request, 'new_topic.html', {'board': board})

# other way from new_topic :)
@login_required
def new_topic(request, id):
    board = get_object_or_404(Board, id=id)
    # user = User.objects.first()
    form = NewTopicForm(request.POST or None)
    if form.is_valid():
        topic = Topic(subject=form.cleaned_data['subject'], board=board, created_by=request.user)
        topic.save()
        post = Post(message=form.cleaned_data['message'], topic=topic, created_by=request.user)
        post.save()
        return redirect('board_topics', id=board.id)
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request, id, topic_id):
    topic = get_object_or_404(Topic, board__id=id, id=topic_id)
    session_key = 'view_topics_{}'.format(topic.id)
    if not request.session.get(session_key,False):
        topic.views += 1
        topic.save()
        request.session[session_key] = True
    return render(request, 'topic_posts.html', {'topic': topic})


@login_required
def reply_post(request, id, topic_id):
    topic = get_object_or_404(Topic, board__id=id, id=topic_id)
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.message = form.cleaned_data['message']
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.updated_by = request.user
            topic.updated_dt = timezone.now()
            topic.save()

            return redirect('topic_posts', id=id, topic_id=topic_id)
        else:
            form = PostForm()
    return render(request, 'reply_post.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    pk_url_kwarg = 'post_id'
    template_name = 'edit_post.html'
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_dt = timezone.now()
        post.save()
        return redirect('topic_posts', post.topic.board.id, post.topic.id)


class UserDeleteView(DeleteView):
    model = Post
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    template_name = 'delete_post.html'
    success_url = reverse_lazy('home')



