from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from .decorators import *
from django.core.mail import send_mail
from random import randint
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from .models import OTP
from django.utils import timezone
from datetime import timedelta

@unautheticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authentifier l'utilisateur
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:  # Vérifier si l'utilisateur est un superuser
                # Générer un OTP unique
                otp_code = str(randint(100000, 999999))

                # Stocker ou mettre à jour l'OTP dans la base de données
                otp, created = OTP.objects.update_or_create(
                    user=user,
                    defaults={'otp_code': otp_code, 'created_at': now(), 'is_verified': False},
                )

                # Envoyer l'OTP par e-mail
                send_mail(
                    'Votre code OTP',
                    f'Bonjour {user.username}, votre code OTP est {otp_code}. Ce code est valide pendant 5 minutes.',
                    'secupharmacy@gmail.com',  # Remplacez par votre adresse e-mail
                    [user.email],
                    fail_silently=False,
                )

                # Stocker l'ID utilisateur dans la session
                request.session['otp_user_id'] = user.id
                print(f"Session après stockage de l'ID utilisateur: {request.session['otp_user_id']}")
                
                # Rediriger vers la page de vérification de l'OTP
                return redirect('verify_otp')

            # Si ce n'est pas un superuser, continuer le processus normal
            # login(request, user)
            return redirect('/')  # Redirection après une connexion réussie

        else:
            messages.error(request, "Identifiants de connexion invalides !")
            return redirect('login')  # Si l'utilisateur n'est pas trouvé, retourner à la page de login

    return render(request, 'login.html')


def verify_otp(request):
    print(f"Vérification de l'OTP - Session actuelle: {request.session.get('otp_user_id')}")

    # Si l'utilisateur n'est pas connecté ou l'ID de session est introuvable
    if not request.session.get('otp_user_id'):
        messages.error(request, "Session expirée. Veuillez vous reconnecter.")
        return redirect('login')

    # Récupérer l'OTP et l'utilisateur lié à la session
    user_id = request.session.get('otp_user_id')
    otp = get_object_or_404(OTP, user_id=user_id)

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')

        # Vérifier si l'OTP est valide et non expiré
        otp_expiration_time = otp.created_at + timedelta(minutes=5)  # 5 minutes de validité
        if otp.otp_code == otp_code and timezone.now() <= otp_expiration_time:
            # Marquer l'OTP comme vérifié
            otp.is_verified = True
            otp.save()

            # Connecter l'utilisateur
            user = otp.user
            login(request, user)
            messages.success(request, "Connexion réussie.")
            return redirect('/')  # Vous pouvez rediriger l'utilisateur vers la page d'accueil ou une autre page.

        else:
            messages.error(request, "Code OTP invalide ou expiré.")
            return redirect('verify_otp')

    return render(request, 'verify_otp.html')


def logoutUser(request):
    logout(request)
    return redirect('login')









































# from django.contrib.auth import authenticate, login, logout
# from django.http import HttpResponseRedirect, HttpResponse
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .decorators import *
# from django.core.mail import send_mail
# from random import randint
# from django.utils.timezone import now
# from django.shortcuts import get_object_or_404
# from .models import OTP

# @unautheticated_user
# def loginPage(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         # Authentifier l'utilisateur
#         user = authenticate(request, username=username, password=password)
#         if user:
#             if user.is_superuser:  # Vérifier si l'utilisateur est un superuser
#                 # Générer un OTP unique
#                 otp_code = str(randint(100000, 999999))

#                 # Stocker ou mettre à jour l'OTP dans la base de données
#                 otp, created = OTP.objects.update_or_create(
#                     user=user,
#                     defaults={'otp_code': otp_code, 'created_at': now(), 'is_verified': False},
#                 )

#                 # Envoyer l'OTP par e-mail
#                 send_mail(
#                     'Votre code OTP',
#                     f'Bonjour {user.username}, votre code OTP est {otp_code}. Ce code est valide pendant 5 minutes.',
#                     'secupharmacy@gmail.com',  # Remplacez par votre adresse e-mail
#                     [user.email],
#                     fail_silently=False,
#                 )

#                 # Rediriger vers la page de vérification de l'OTP
#                 request.session['otp_user_id'] = user.id  # Stocker l'ID utilisateur dans la session
#                 return redirect('verify_otp')  # Cette ligne redirige vers la page de vérification de l'OTP

#             # Si ce n'est pas un superuser, continuer le processus normal
#             login(request, user)
#             return redirect('/')  # Redirection après une connexion réussie

#         else:
#             messages.error(request, "Identifiants de connexion invalides !")
#             return redirect('login')  # Si l'utilisateur n'est pas trouvé, retourner à la page de login

#     return render(request, 'login.html')



# def verify_otp(request):
#     if request.method == 'POST':
#         otp_code = request.POST.get('otp_code')
#         user_id = request.session.get('otp_user_id')  # Récupérer l'ID utilisateur de la session

#         if not user_id:
#             messages.error(request, "Session expirée. Veuillez vous reconnecter.")
#             return redirect('login')

#         otp = get_object_or_404(OTP, user_id=user_id)

#         # Vérifier si l'OTP est valide et non expiré
#         otp_expiration_time = otp.created_at + timedelta(minutes=5)  # 5 minutes de validité
#         if otp.otp_code == otp_code and timezone.now() <= otp_expiration_time:
#             # Marquer l'OTP comme vérifié
#             otp.is_verified = True
#             otp.save()

#             # Connecter l'utilisateur
#             user = otp.user
#             login(request, user)
#             messages.success(request, "Connexion réussie.")
#             return redirect('/')

#         else:
#             messages.error(request, "Code OTP invalide ou expiré.")
#             return redirect('verify_otp')

#     return render(request, 'verify_otp.html')



# def logoutUser(request):
#     logout(request)
#     return redirect('login')




















# @unautheticated_user
# def loginPage(request):
    
#     if request.method == 'POST':
#         username=request.POST.get('username')
#         password=request.POST.get('password')

#         user=authenticate(request,username=username,password=password)
#         if user != None:
#             login(request, user)
#             user_type = user.user_type
#             if user_type == '1':
#                 return redirect('/')
                
#             elif user_type == '2':
#                 return redirect('pharmacist_home')

#             elif user_type == '3':
#                 return redirect('doctor_home')
#             elif user_type == '4':
#                 return redirect('clerk_home')
#             elif user_type == '5':
#                 return redirect('patient_home')
                
           
#             else:
#                 messages.error(request, "Invalid Login!")
#                 return redirect('login')
#         else:
#             messages.error(request, "Invalid Login Credentials!")
#             return redirect('login')
    
#     return render(request,'login.html')


