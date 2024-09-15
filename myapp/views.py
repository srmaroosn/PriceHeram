import json
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from .utils import *
from django.conf import settings
from operator import itemgetter
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
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

@login_required(login_url ='/signin/')
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

@login_required(login_url ='/signin/')
def my_history(request):
    history = History.objects.filter(user=request.user)
    if request.user.is_staff:
        history = History.objects.filter()
    return render(request, "my_history.html", locals())

@login_required(login_url ='/signin/')
def all_user(request):
    data = Register.objects.filter()
    return render(request, "all_user.html", locals())

@login_required(login_url ='/signin/')
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


def delete_user(request, pid):
    user = User.objects.get(id=pid)
    user.delete()
    messages.success(request, "User Deleted")
    return redirect('all_user')


def delete_history(request, pid):
    data = History.objects.get(id=pid)
    data.delete()
    messages.success(request, "History Deleted")
    return redirect('my_history')




# def get_price_from_history(history_id):
#     try:
#         history_instance = History.objects.get(id=history_id)
#         # Deserialize the JSON data stored in the 'product' field
#         print('price')
#         product_data = json.loads(history_instance.product)
#         # Access the 'price' value from the JSON data
#         price = product_data.get("price")

#         return price
#     except History.DoesNotExist:
#         return None
# def get_prices_from_history(user_id):
#     try:
#         # Retrieve all History instances associated with the user
#         history_instances = History.objects.filter(user_id=user_id)

#         # Initialize an empty list to store prices
#         prices = []

#         # Loop through each History instance and extract the price
#         for history_instance in history_instances:
#             product_data = json.loads(history_instance.product)
#             price = product_data.get("price")
#             if price is not None:
#                 prices.append(price)

#         return prices
#     except History.DoesNotExist:
#         return []


# def get_product_data_from_history(user_id):
#     try:
#         # Retrieve all History instances associated with the user
#         history_instances = History.objects.filter(user_id=user_id)

#         # Initialize an empty list to store product data strings
#         product_data_list = []

#         # Loop through each History instance and extract the product data
#         for history_instance in history_instances:
#             # Retrieve the product data as a string
#             product_data = history_instance.product
#             # Append the product data string to the list
#             product_data_list.append(product_data)

#         return product_data_list
#     except History.DoesNotExist:
#         return None


# def get_product_data_from_history(user_id):
#     try:
#         # Retrieve all History instances associated with the user
#         history_instances = History.objects.filter(user_id=user_id)

#         # Initialize an empty list to store product data strings
#         product_data_list = []

#         # Loop through each History instance and extract the product data
#         for history_instance in history_instances:
#             # Retrieve the product data as a string
#             product_data = history_instance.product
#             # Append the product data string to the list
#             product_data_list.append(product_data)

#         return product_data_list
#     except History.DoesNotExist:
#         return None


def arrange_data(raw_data):
    arranged_data = []

    # Loop through each item in the raw_data list
    for item in raw_data:
        try:
            # Replace single quotes with double quotes to make it valid JSON
            item = item.replace("'", "\"")
            item_dict = json.loads(item)

            # Append the item dictionary to the 'object' key in the result dictionary
            arranged_data.extend(item_dict.get('object', []))
        except json.JSONDecodeError:
            # Handle any errors that may occur during JSON parsing
            pass

    # Create a final dictionary with the 'object' key and the arranged data
    prices = []
    names = []

    # Iterate through the 'object' list and extract 'price' and 'name'
    for item in arranged_data:
        prices.append(item.get('price', 0))
        names.append(item.get('name', ''))

    # Create a dictionary with 'price' and 'name' as keys
    result_dict = {'price': prices, 'name': names}

    # 'result_dict' now contains prices and names as a dictionary
    return result_dict


# Assuming you have already retrieved the data from the database and stored it in 'old_price'
old_price = [
    "{'object': [{'logo': '/static/assets/img/flipkart-logo.png', 'price': 0, 'name': '0', 'link': '0', 'image': '0'}]}",
    "{'object': [{'logo': '/static/assets/img/amazon-logo.png', 'price': 0, 'name': '0', 'link': '0', 'image': '0'}]}"
]
arranged_data = arrange_data(old_price)

# 'arranged_data' now contains the data in the desired format


def get_product_data_from_history(user_id):
    try:
        # Retrieve all History instances associated with the user
        history_instances = History.objects.filter(user_id=user_id)

        # Initialize an empty list to store product data strings
        product_data_list = []

        # Loop through each History instance and extract the product data
        for history_instance in history_instances:
            # Retrieve the product data as a string
            product_data = history_instance.product
            # Append the product data string to the list
            product_data_list.append(product_data)

        return arrange_data(product_data_list)
    except History.DoesNotExist:
        return None


# Assuming you have already retrieved the data from the database and stored it in 'old_price'


# 'arranged_data' now contains the data in the desired format

@login_required(login_url ='/signin/')
def send_alert(request):

    if request.method == 'POST':
        # Assuming you have a 'price' parameter in the POST request
        price = request.POST.get('price')
        name = request.POST.get('name')
        # Replace with the recipient's email address
        receiver_email = request.POST.get('email')
        # Send an email alert if the condition is met (e.g., price increased)
        if 100000 <= int(price) <= 500000:
            send_alert_sms(price, receiver_email,name)
            return HttpResponse('Alert sent successfully')
        else:
            return HttpResponse('You will get notified when the price gets updated to your desired price.')

    elif request.method == 'GET':
        # Render the alert.html template for GET requests
        return render(request, 'alert.html')

    else:
        return HttpResponse('Invalid request method', status=400)


def send_alert_sms(price, receiver_email,name):
    try:
        subject = 'Price Alert'
        message = f'Great news! The price of the {name} youve been keeping an eye on has been updated to  {price}. Its time to make your purchase and enjoy the savings!'
        from_email = 'vr302916@gmail.com'  # Replace with your email address

        send_mail(subject, message, from_email, [
                  receiver_email], fail_silently=False)
        return True  # Email sent successfully
    except Exception as e:
        # Handle any errors that may occur during email sending
        print(f"Error sending email: {str(e)}")
        return False  # Email sending failed
