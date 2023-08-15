from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from .models import User, Otp
from django.db.models import Q
from .email_module import send_email
from random import randint
from uuid import uuid4


class LoginView(View):
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('chat:lobby')
        else:
            return render(request, 'account_app/auth.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 200, 'username': user.username})
            else:
                return JsonResponse({'status': 401})
        return JsonResponse({'status': 400})


class RegisterView(View):
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('chat:lobby')
        return redirect('account:login')

    def post(self, request):
        data = request.POST
        if all(data.values()) and None not in data.values():
            if data['password'] != data['confirm_pass']:
                return JsonResponse({'status': 400, 'message': 'passwords conflict'})
            elif User.objects.filter(Q(username=data['username']) | Q(email=data['email'])).exists():
                return JsonResponse({'status': 409})
            else:
                random_code = randint(100000, 999999)
                email_sent = send_email(random_code, data['email'])
                if email_sent:
                    token = str(uuid4())
                    Otp.objects.create(
                        username=data['username'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        email=data['email'],
                        password=data['password'],
                        code=random_code,
                        token=token,
                    )
                    return JsonResponse({'status': 200, 'token': token})
                else:
                    return JsonResponse({
                        'status': 500,
                        'message': 'Service OTP encountered an error. Please try again. If the error is not resolved, contact support'
                    })
        return JsonResponse({'status': 400, 'message': 'missed info'})


@login_required
def user_logout(request):
    logout(request)
    return redirect('account:login')


class CheckOtp(View):
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('chat:lobby')
        return redirect('account:login')

    def post(self, request):
        token = request.POST.get('token')
        code = request.POST.get('code')

        if token and code:
            try:
                new_user = Otp.objects.get(token=token, code=code)
                user = User.objects.create_user(
                    username=new_user.username,
                    first_name=new_user.first_name,
                    last_name=new_user.last_name,
                    email=new_user.email,
                    password=new_user.password
                )
                login(request, user)
                new_user.delete()
                return JsonResponse({'status': 200, 'username': user.username})
            except:
                return JsonResponse({'status': 400, 'message': 'Invalid code'})
        else:
            return JsonResponse({'status': 400, 'message': 'missed info'})


# class ForgotPasswordView(View):
#     def get(self, request):
#         code = request.GET.get('code')
#         if code and code.isdigit():
#             try:
#                 user = User.objects.get(one_time_password=code)
#             except:
#                 return JsonResponse({'status': 401, 'err': 'کد وارد شده نادرست است !'})
#
#             login(request, user)
#             request.session.set_expiry(60 * 60 * 24 * 2)
#             user.one_time_password = 0
#             user.save()
#             return JsonResponse({'status': 200, 'firstName': user.first_name, 'lastName': user.last_name})
#         else:
#             return JsonResponse({'status': 400, 'err': 'کد نامعتبر است!'})
#
#     def post(self, request):
#         form = ForgotPasswordForm(request.POST)
#         if form.is_valid():
#             user_email = form.cleaned_data['email']
#             try:
#                 user = User.objects.get(email=user_email)
#             except:
#                 return JsonResponse({'status': 401})
#
#             random_code = randint(10000, 99999)
#             user.one_time_password = random_code
#             user.save()
#
#             email = send_email.delay(random_code, user_email)
#             if not email:
#                 return JsonResponse({'status': 400, 'err': 'خطا در ارسال ایمیل !'})
#             return JsonResponse({'status': 200})
#         else:
#             return JsonResponse({'status': 400, 'err': 'فرم معتبر نمی باشد !'})
