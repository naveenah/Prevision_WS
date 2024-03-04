from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

# Create your views here.
def register(request):
    print("Request received" + str(request.method))
    if request.method == 'POST':
        print("Request received is POST")
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            print("Success!!")
            return redirect('iread-home')
    else:
        form = UserCreationForm()
    return render(request, 'UserApp/register.html', {'form': form})
