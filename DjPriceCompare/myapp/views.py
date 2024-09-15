import json
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from .utils import *
from django.conf import settings
from operator import itemgetter
from django.contrib.auth.decorators import login_required
# Create your views here.


def home(request):
    return render(request, "home.html", locals())


def about(request):
    return render(request, "about.html", locals())


def contact(request):
    return render(request, "contact.html", locals())


def register(request):
    if request.method == "POST":
        re = request.POST
        rf = request.FILES
        user = User.objects.create_user(
            username=re['username'], first_name=re['first_name'], last_name=re['last_name'], password=re['password'])
        register = Register.objects.create(
            user=user, address=re['address'], mobile=re['mobile'], image=rf['image'])
        messages.success(request, "Registration Successful")
        return redirect('signin')
    return render(request, "signup.html", locals())


def update_profile(request):
    if request.method == "POST":
        re = request.POST
        rf = request.FILES
        try:
            image = rf['image']
            data = Register.objects.get(user=request.user)
            data.image = image
            data.save()
        except:
            pass
        user = User.objects.filter(id=request.user.id).update(
            username=re['username'], first_name=re['first_name'], last_name=re['last_name'])
        register = Register.objects.filter(user=request.user).update(
            address=re['address'], mobile=re['mobile'])
        messages.success(request, "Updation Successful")
        return redirect('update_profile')
    return render(request, "update_profile.html", locals())


def signin(request):
    if request.method == "POST":
        re = request.POST
        user = authenticate(username=re['username'], password=re['password'])
        if user:
            login(request, user)
            messages.success(request, "Logged in successful")
            return redirect('home')
    return render(request, "signin.html", locals())


def admin_signin(request):
    if request.method == "POST":
        re = request.POST
        user = authenticate(username=re['username'], password=re['password'])
        if user.is_staff:
            login(request, user)
            messages.success(request, "Logged in successful")
            return redirect('home')
    return render(request, "admin_signin.html", locals())


def change_password(request):
    if request.method == "POST":
        re = request.POST
        user = authenticate(username=request.user.username,
                            password=re['old-password'])
        if user:
            if re['new-password'] == re['confirm-password']:
                user.set_password(re['confirm-password'])
                user.save()
                messages.success(request, "Password changed successfully")
                return redirect('home')
            else:
                messages.success(request, "Password mismatch")
        else:
            messages.success(request, "Wrong password")
    return render(request, "change_password.html", locals())


def logout_user(request):
    logout(request)
    messages.success(request, "Logout Successfully")
    return redirect('home')


@login_required(login_url='/signin')
def search_product(request):
    product = []
    dictobj = {'object': []}
    if request.method == "POST":
        re = request.POST
        name = re['search']
        flipkart_price, flipkart_name, flipkart_image, flipkart_link = flipkart(
            name)
        amazon_price, amazon_name, amazon_image, amazon_link = amazon(name)
        croma_price, croma_name, croma_image, croma_link = croma(name)
        gadgetsnow_price, gadgetsnow_name, gadgetsnow_image, gadgetsnow_link = gadgetsnow(
            name)
        reliance_price, reliance_name, reliance_image, reliance_link = reliance(
            name)
        dictobj["object"].append({'logo': '/static/assets/' + 'img/' + 'flipkart-logo.png', 'price': convert(
            flipkart_price), 'name': flipkart_name, 'link': flipkart_link, 'image': flipkart_image})
        dictobj["object"].append({'logo': '/static/assets/' + 'img/' + 'amazon-logo.png', 'price': convert(
            amazon_price), 'name': amazon_name, 'link': amazon_link, 'image': amazon_image})
        dictobj["object"].append({'logo': '/static/assets/' + 'img/' + 'croma-logo.png', 'price': convert(
            croma_price), 'name': croma_name, 'link': croma_link, 'image': croma_image})
        dictobj["object"].append({'logo': '/static/assets/' + 'img/' + 'gadgetsnow-logo.png', 'price': convert(
            gadgetsnow_price), 'name': gadgetsnow_name, 'link': gadgetsnow_link, 'image': gadgetsnow_image})
        dictobj["object"].append({'logo': '/static/assets/' + 'img/' + 'reliance-logo.png', 'price': convert(
            reliance_price), 'name': reliance_name, 'link': reliance_link, 'image': reliance_image})
        data = dictobj['object']
        data = sorted(data, key=itemgetter('price'))
        history = History.objects.create(user=request.user, product=dictobj)
        # messages.success(request, "History Saved")
    return render(request, "search_product.html", locals())

@login_required(login_url='/signin')
def my_history(request):
    history = History.objects.filter(user=request.user)
    if request.user.is_staff:
        history = History.objects.filter()
    return render(request, "my_history.html", locals())

@login_required(login_url='/signin')
def all_user(request):
    data = Register.objects.filter()
    return render(request, "all_user.html", locals())

@login_required(login_url='/signin')
def history_detail(request, pid):
    history = History.objects.get(id=pid)
    product = (history.product).replace("'", '"')
    product = json.loads(str(product))
    product = product['object']
    product = sorted(product, key=itemgetter('price'))
    try:
        user = Register.objects.get(user=history.user)
    except:
        pass
    return render(request, "history_detail.html", locals())

@login_required(login_url='/signin')
def delete_user(request, pid):
    user = User.objects.get(id=pid)
    user.delete()
    messages.success(request, "User Deleted")
    return redirect('all_user')

@login_required(login_url='/signin')
def delete_history(request, pid):
    data = History.objects.get(id=pid)
    data.delete()
    messages.success(request, "History Deleted")
    return redirect('my_history')
