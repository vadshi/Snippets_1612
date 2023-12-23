from django.http import Http404
from django.shortcuts import render, redirect
from MainApp.forms import SnippetForm, UserRegistrationForm
from django.core.exceptions import ObjectDoesNotExist
from MainApp.models import Snippet
from django.contrib import auth
from django.contrib.auth.decorators import login_required


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


@login_required
def my_snippets(request):
    snippets = Snippet.objects.filter(user=request.user)
    context = {
        'pagename': 'Мои сниппеты',
        'snippets': snippets,
        }
    return render(request, 'pages/view_snippets.html', context)


@login_required
def add_snippet_page(request):
    if request.method == "GET":
        form = SnippetForm()
        context = {
            'pagename': 'Добавление нового сниппета',
            'form': form
            }
        return render(request, 'pages/add_snippet.html', context)
    
    if request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            if request.user.is_authenticated:
                snippet.user = request.user
                snippet.save()
            return redirect("snippets-list")
        return render(request,'add_snippet.html', {'form': form})


def snippets_page(request):
    snippets = Snippet.objects.filter(public=True)
    context = {
        'pagename': 'Просмотр сниппетов',
        'snippets': snippets,
        }
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, snippet_id):
    try:
        snippet = Snippet.objects.get(id=snippet_id)
    except ObjectDoesNotExist:
        raise Http404
    context = {
        'pagename': 'Просмотр сниппета',
        'snippet': snippet,
        "type": "view",
        }
    return render(request, 'pages/snippet_detail.html', context)


def snippet_edit(request, snippet_id):
    try:
        snippet = Snippet.objects.get(id=snippet_id)
    except ObjectDoesNotExist:
        raise Http404
    # Хотим получить страницу данных сниппета
    if request.method == "GET":
        context = {
            'pagename': 'Просмотр сниппета',
            'snippet': snippet,
            "type": "edit",
            }
        return render(request, 'pages/snippet_detail.html', context)
    
    # Хотим использовать данные из формы и сохранить изменения в БД
    if request.method == "POST":
        data_form = request.POST
        snippet.name = data_form["name"]
        snippet.code = data_form["code"]
        snippet.creation_date = data_form["creation_date"]
        snippet.public = data_form.get("public", False)
        snippet.save()
        return redirect("snippets-list")


def snippet_delete(request, snippet_id):
    snippet = Snippet.objects.get(id=snippet_id)
    snippet.delete()
    return redirect("snippets-list")


def create_user(request):
    context = {'pagename': "Регистрация пользователя"}
    # Пустая форма для заполнения данных
    if request.method == "GET":
        form = UserRegistrationForm()
        context['form'] = form
        return render(request, 'pages/registration.html', context)
    
    # Используем данные из формы
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
        context['form'] = form
        return render(request,'pages/registration.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
        else:
            context = {
                'pagename': "PythonBin",
                'errors': ["wrong username or password"]
            }
            return render(request, 'pages/index.html', context)
    return redirect('home')


def logout(request):
    auth.logout(request)
    return redirect("home")

