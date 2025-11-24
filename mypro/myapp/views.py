import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from mypro.firebase_connection import database
firebase_key ="AIzaSyCZAFn21FZT4zh5qyN18_KuUH_hdSTg7Ow"
import  requests

# Create your views here.
def index(r):
    return render(r,"myapp/index.html")
def register(r):
    if r.method == "POST":
        a  = r.POST.get("name")
        b  = r.POST.get("email")
        c  = r.POST.get("pswd")
        d  = int(r.POST.get("num"))

        if not a or not b or not c or not d:
            messages.error(r,"All Fields Are Required")
            return redirect("reg")

        if len(c) < 6:
            messages.error(r, "Password Should be Greater than 6")
            return redirect("reg")

        if d < 18:
            messages.error(r, "Age Should be Greater than 17")
            return redirect("reg")

        url=f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_key}"
        jao = {
            "email" : b,
            "password" : c,
            "returnSecureToken" : True
        }

        resp = requests.post(url,jao)

        if resp.status_code == 200:

            user_Data = resp.json()
            print(user_Data)
            # Email Send
            id = user_Data.get("idToken")

            email_url =f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={firebase_key}"
            email_data = {
                "requestType":"VERIFY_EMAIL",
                "idToken" : id
            }

            email_send = requests.post(email_url , email_data)
            if email_send.status_code == 200:
                database.collection("registered_user").add({
                    "Name" : a,
                    "Email" : b,
                    "Age" : d,
                    "Created_at" : datetime.datetime.utcnow()
                })
                messages.success(r,"User Create Successfully and Email has been sent")
                return redirect("reg")
            else:
                error = resp.json().get("error", {}).get("messages", "Not Found")
                print(error)
                messages.error(r, f"Error : {error}")
                return redirect("reg")
        else:
            error = resp.json().get("error",{}).get("message","Not Found")
            print(error)
            messages.error(r,f"Error : {error}")
            return redirect("reg")
    return render(r,"myapp/register.html")
