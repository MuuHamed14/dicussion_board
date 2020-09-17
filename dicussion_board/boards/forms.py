from django import forms
from .models import Topic, Post


class NewTopicForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'What is on your mind?'}),
                              help_text='The Max length of text is 4000', max_length=4000)

    class Meta:
        model = Topic
        fields = ['subject', 'message']


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['message']