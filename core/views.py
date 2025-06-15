#Django imports
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
import random, time

def custom_logout_view(request):
    logout(request)
    return redirect("/accounts/login/")  # O a donde desees redirigir después del logout

def notLoggedIn(request):
    return JsonResponse({"ok":False,"message": "You are not logged in", "data":[]})

class HelloWord(View):
    def get(self, request):
        return JsonResponse({"ok":True,"message": "Core. Hello world", "data":[]})

class LoginView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            username=request.user.username
            return JsonResponse({"ok":True,"message": "The user {0} already is authenticated".format(username), "data":[{'username':request.user.username}]})

        username=request.POST.get('username')
        password=request.POST.get('password')
        print('Logiranje uporabnika: ',username,' - ',password)
        user = authenticate(username=username, password=password)
        if user:
            login(request,user)#introduce into the request cookies the session_id,
                    # and in the auth_sessions the session data. This way, 
                    # in followoing requests, know who is the user and if
                    # he is already authenticated. 
                    # The coockies are sent in the response header on POST requests
            return JsonResponse({"ok":True,
                                 "message": "User {0} logged in".format(username), 
                                 "data":[{
                                    "username": username,
                                    "groups": list(user.groups.values_list("name", flat=True))
                                    }]
                                })
        else:
            # To make thinks difficult to hackers, you make a random delay,
            # between 0 and 1 second
            seconds=random.uniform(0, 1)
            time.sleep(seconds)
            return JsonResponse({"ok":False,"message": "Wrong user or password", "data":[]})

class LogoutView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        username=request.user.username
        logout(request) #removes from the header of the request
                            #the the session_id, stored in a cookie
        return JsonResponse({"ok":True,"message": "The user {0} is now logged out".format(username), "data":[]})


class IsLoggedIn(View):
    def post(self, request, *args, **kwargs):
        print(request.user.username)
        print(request.user.is_authenticated)
        if request.user.is_authenticated:
            return JsonResponse({"ok":True,"message": "You are authenticated", "data":[{'username':request.user.username}]})
        else:
            return JsonResponse({"ok":False,"message": "You are not authenticated", "data":[]})

            
class CheckLoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return JsonResponse({
                "ok": True,
                "message": "User is authenticated",
                "data": [{
                    "username": request.user.username,
                    "groups": list(request.user.groups.values_list("name", flat=True))
                }]
            })
        else:
            return JsonResponse({
                "ok": False,
                "message": "User is not authenticated",
                "data": []
            })