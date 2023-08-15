from django.shortcuts import redirect


def redirector(request):
    if request.user.is_authenticated:
        return redirect('chat:lobby')
    else:
        return redirect('account:login')
