from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .models import Todo
from .forms import Todoform
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        return redirect(currentodo)
    else:
        return render(request, 'todo/homepage.html')

def signupuser(request):
    if request.method == "GET":
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user=user)
                return redirect('currentodo')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Username not available'})
        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Passwords doesn\'t match'})

def loginuser(request):
    if request.method == "GET":
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Wrong Username and Password combination'})
        else:
            login(request, user)
            return redirect('currentodo')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def currentodo(request):
    todos = Todo.objects.filter(author=request.user, date_completed__isnull=True)
    totaltodos = len(todos)
    notempty = bool(totaltodos)
    return render(request, 'todo/currenttodos.html', {'todos': todos, 'notempty': notempty, 'totaltodos': totaltodos})


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': Todoform()})
    else:
        form = Todoform(request.POST)
        try:
            t = form.save(commit=False)
            t.author = request.user
            t.save()
            return redirect('currentodo')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': form, 
            'error': 'bad data sent over'})

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(author=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, "todo/completedtodos.html", {'todos': todos})  

@login_required
def viewtodo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, author=request.user)
    if request.method == 'GET':
        return render(request, 'todo/viewtodo.html', {'form': Todoform(instance=todo), 'pk': pk, 'todo': todo})
    else:
        form = Todoform(request.POST, instance=todo)
        try:
            t = form.save()
            return redirect('currentodo')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'form': Todoform(instance=form), 'pk': pk, 
            'error': 'bad data sent over'})

@login_required        
def completodo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, author=request.user)
    todo.date_completed = timezone.now()
    todo.save()
    return redirect("currentodo")

@login_required
def deletetodo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, author=request.user)
    todo.delete()
    return redirect("currentodo")