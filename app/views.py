from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistroForm
from .models import Persona
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if not user:
            try:
                rut_limpio = username.upper().replace(".", "").replace("-", "").replace(" ", "")
                
                persona = Persona.objects.get(rut=rut_limpio)
                
                user = authenticate(request, username=persona.user.username, password=password)
            except Persona.DoesNotExist:
                pass
        
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Credenciales inválidas.')
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home_view(request):
    return render(request, 'home.html', {
        'user': request.user,
    })