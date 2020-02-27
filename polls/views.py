import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from django.forms import formset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

from polls.models import Answer, Poll, Question


# Create your views here.
def my_login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # next_url = request.POST.get('next_url')
            # if next_url:
            #     return redirect(next_url)
            return redirect('index')
        else:
            context['username'] = username
            context['password'] = password
            context['error'] = 'Wrong username or password!'
    # next_url = request.GET.get('next')
    # if next_url:
    #     context['next_url'] = next_url
    return render(request, template_name='login.html', context=context)

def my_logout(request):
    logout(request)
    return redirect('login')

@login_required
def change_password(request):
    context = {}
    if request.method == 'POST':
        user = request.user
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        # check that the passwords match
        if password1 == password2:
            # reset password
            u = User.objects.get(username=user)
            u.set_password(password1)
            u.save()
            return redirect('login')
        else:
            context['password1'] = password1
            context['password2'] = password2
            context['error'] = 'Passwords are not same!'
    return render(request, template_name='change_password.html', context=context)

@login_required
def index(request):
    search = request.GET.get('search', '')
    poll_list = Poll.objects.filter(
        del_flag=False, title__icontains=search
    ).annotate(question_count=Count('question')) # COUNT(*) GROUP BY
    context = {
        'poll_list': poll_list,
        'search': search
    }
    return render(request, template_name='polls/index.html', context=context)

@login_required
@permission_required('polls.view_poll')
def detail(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    return render(request, 'polls/detail.html', { 'poll': poll })

@login_required
@permission_required('polls.add_poll', login_url='/polls/index/')
def create(request):
    context = {}
    if request.method == 'POST' and request.FILES['picture']:
        poll = Poll.objects.create(
            title= request.POST.get('title'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            picture=request.FILES['picture'],
        )
        poll.save()
        return redirect('index')
    return render(request, template_name='polls/create.html', context=context)
