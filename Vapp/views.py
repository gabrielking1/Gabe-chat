from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login,authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.http import Http404
from  .forms import RegForm
# from Vendor.models import Vendor, Product
# from Customer.models import Customer
from verify_email.email_handler import send_verification_email
from datetime import timedelta
from django.utils import timezone
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.decorators import login_required
# from .filters import ProductFilter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from Vendor.forms import PupdateProfileForm
# from Customer.forms import UpdateProfileForm
# from Vendor.models import Wallet
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from .models import Messages, CustomOrder

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import CustomOrder, Messages


import json
from django.contrib import messages
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import CustomOrder, Messages



def login(request):
    if request.user.is_authenticated and request.user.is_active:
        messages.info(request, 'you are logged in already')
        return redirect('index')
    
    users = User.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            usera = User.objects.filter(username=username, is_active=False)
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('/login/')
        
        user = authenticate(request, username=username, password=password)

        if usera.exists():
            messages.error(request, 'Verify your account or request for verification.')
            messages.info(request, 'Please request for a new verification link.')
            return redirect('/login/')
        elif user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('/login/')
    else:
        form = AuthenticationForm()
        return render(request, 'signin.html', {'form': form, 'users': users})


# def login(request):

#     # if request.user.is_authenticated:
#     #     messages.info(request, 'you are logged in already')
#     #     return redirect('index')
#     users = User.objects.all()
#     if request.method == 'POST':
#         # usera = User.select().where(User.email == resp.email).first()
#         username = request.POST['username']
#         password = request.POST['password']
#         usera = User.objects.filter(username=username, is_active =False)
#         user = authenticate(request, username =username, password = password)
#         if usera:
#             messages.error(request, 'Verify your account or request for verification ')
#             messages.infoy(request, 'please request for new verification link ')
#             # return redirect('http://127.0.0.1:8000//verification/user/verify-email/request-new-link/')
#             return redirect('/login/')
#         elif user is not None:
            
#             auth.login(request,user)
#             return redirect('index')
        
#         else:
#             messages.error(request,'invalid login credentials')
#             return redirect('/login/')
     
#     else:
#         form = AuthenticationForm()
#         return render(request, 'signin.html', {'form':form,  'users':users})
    
def logout(request):
    auth.logout(request)
    messages.info(request, 'Come back soon')
    return redirect('/login/')

def register(request):
 
    if request.user.is_authenticated:
        return redirect('index')
     
    if request.method == 'POST':
        form = RegForm(request.POST)
 
        if form.is_valid():
            form.save()
            inactive_user = send_verification_email(request, form)
            messages.info(request, " account created successfully ")
            messages.info(request,'please check your email to verify your account')

            # username = form.cleaned_data['username']
            # password = form.cleaned_data['password1']
            # user = authenticate(request=request,username = username,password = password)
            # auth.login(request, user)
            return redirect('/login/')
         
        else:
            return render(request,'signup.html',{'form':form})
     
    else:
        form = RegForm()
        return render(request,'signup.html',{'form':form})
    

def order(request):
    
    if CustomOrder.objects.filter(user=request.user):
        order = CustomOrder.objects.filter(user=request.user)
        return render(request, 'orders.html', {'order': order})
    elif CustomOrder.objects.filter(store__vendor=request.user):
        order = CustomOrder.objects.filter(store__vendor=request.user)
        return render(request, 'orders.html', {'order': order})
    else:
    

        return render(request, 'orders.html')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import CustomOrder, Messages

def chat(request, order_id):
    order = get_object_or_404(CustomOrder, id=order_id)

    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        message_content = request.POST.get('message')

        if not receiver_id or not message_content:
            messages.error(request, "Receiver and message content are required.")
            return redirect('chat', order_id=order_id)

        if receiver_id != order.user.id and receiver_id != order.store.vendor.user.id:
            messages.error(request, "Invalid receiver.")
            return redirect('chat', order_id=order_id)

        message = Messages.objects.create(
            order=order,
            sender=request.user,
            receiver_id=receiver_id,
            message=message_content
        )

        # Debug: Print message to console
        print(f"Message created: {message}")

        messages.success(request, "Message sent successfully!")
        return redirect('chat', order_id=order_id)

    messages_list = Messages.objects.filter(order=order).order_by('-timestamp')

    return render(request, 'chat.html', {
        'order': order,
        'messages': messages_list
    })


def confirm(request, id):
    order = get_object_or_404(CustomOrder, id=id)
    # Get the latest message for this order
    message = Messages.objects.filter(order=order).last()
    if request.method == "POST":
        proposed = request.POST.get('proposed')
        counter = request.POST.get('counter')
        if order.proposed_price is None and request.user is order.store.vendor:
            order.proposed_price = proposed
            if counter is not None:
                order.counter_offer = True
            else:
                order.counter_offer = False
            Messages.objects.create(
                order = order,
                sender = request.user,
                message = f"{request.user.username} proposed price({proposed}) has been sent",
                receiver = order.user
                )
            order.save()
            messages.success(request, f'Your proposed price({proposed}) has been sent ')

            return redirect(request.META.get('HTTP_REFERER'))
        elif order.proposed_price is not None and order.counter_offer is True and request.user == order.user:
            proposed = request.POST.get('counter_proposed')
            order.proposed_price = proposed
            Messages.objects.create( 
              order = order,
                sender = request.user,
                message = f"{request.user.username} countered proposed new price {proposed}",
                receiver = order.store.vendor
            )
            order.save()
            return redirect(request.META.get('HTTP_REFERER'))
        
        elif order.proposed_price is not None and order.counter_offer is False and request.user == order.user and order.order_status == "Pending":
            print("this is order customer offer ", order.counter_offer)
            accept = request.POST.get('accept_proposed')
            
            decline = request.POST.get('decline_proposed')
            print(f"this is {accept} and this is {decline} here ")
            if accept is not None:
                order.price = accept
                order.accept_status ="Yes"
                order.order_status = "Completed"
                Messages.objects.create( 
                order = order,
                sender = request.user,
                message = f"{request.user.username} accepted the proposed price {accept}",
                receiver = order.store.vendor
                )
                order.save()
                messages.success(request, f'You accepted {accept} has been accepted')

                return redirect(request.META.get('HTTP_REFERER'))
            else:
                order.accept_status ="No"
                order.order_status = "Cancelled"
                Messages.objects.create( 
                order = order,
                sender = request.user,
                message = f"{request.user.username} declined the proposed price {order.proposed_price}",
                receiver = order.store.vendor
                )
                order.save()
                messages.success(request, f'You accepted {order.proposed_price} has been accepted')

                return redirect(request.META.get('HTTP_REFERER'))
                
        
        
        elif order.proposed_price is not None and order.accept_status =="Pending":
            accept = request.POST.get('accept_customer_proposed')
            
            decline = request.POST.get('reject_customer_proposed')
            print(f"this is {accept} and this is {decline}")
            if accept is not None:
                order.price = accept
                order.accept_status ="Yes"
                order.order_status = "Completed"
                Messages.objects.create( 
                order = order,
                sender = request.user,
                message = f"{request.user.username} accepted the proposed price {accept}",
                receiver = order.user
                )
                order.save()
                messages.success(request, f'You accepted {accept} has been accepted')

                return redirect(request.META.get('HTTP_REFERER'))
            else:
                order.accept_status ="No"
                order.order_status = "Cancelled"
                Messages.objects.create( 
                order = order,
                sender = request.user,
                message = f"{request.user.username} declined the proposed price {order.proposed_price}",
                receiver = order.user
                )
                order.save()
                messages.success(request, f'You accepted {order.proposed_price} has been accepted')

                return redirect(request.META.get('HTTP_REFERER'))
                
       

        else:
            messages.error(request, f'wahala don happem')
            return redirect(request.META.get('HTTP_REFERER'))
            

