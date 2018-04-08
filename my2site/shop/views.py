from .models import Product, Provider, Category, Guest, Product_in_cart, Photo
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from django.views import View
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from .forms import ImageFieldForm
from django.core.validators import validate_image_file_extension
from django.shortcuts import render
from django.urls import reverse
import json


def my_response_404(clas, obj_id):
    error1 = {"status": "404"}
    error1["source"] = {"pointer": "/data/" + str(clas) + "/obj_id"}
    error1["detail"] = 'Object With Identifier = ' + str(obj_id) + ' Does Not Exist.'
    out = {"errors": [error1]}
    return HttpResponseNotFound(json.dumps(out), content_type="application/json")


def wrap_products(list_p):
    if not list_p:
        return {"data": []}
    done = []
    for prod in list_p:
        done.append({"name": prod.name, "id": prod.id, "price": prod.price,
                     "incoming_date": prod.incoming_date.strftime('%Y.%m.%d-%H:%M:%S')})
    return {"category" : prod.category.name, "data": done}


def not_app_json(request):
    if request.content_type != "application/json":
        error1 = {"status": "400"}
        error1["source"] = {"pointer": "/post/content_type/application_json"}
        error1["title"] = 'Wrong POST attempt.'
        error1["detail"] = "Content-Type: application/json."
        out = {"errors": [error1]}
        return out
    return None


def check_user(request, body):
    user = request.user
    if not request.user.is_authenticated:
        error1 = {"status": "403"}
        error1["source"] = {"pointer": "/user/login"}
        try:
            err = 'username'
            username = body['username']
            err = 'password'
            password = body['password']
            err = 'email'
            email = body['email']
        except (KeyError):
            if err != 'email':
                error1["title"] = 'Forbidden. Fields username and password must be present.'
                error1["detail"] = "No field " + err
                out = {"errors": [error1]}
                return {"user": None, "error": out}
            else:
                email = ''
        user = authenticate(request, username=username, password=password)
        if user is None:
            error1["title"] = 'Forbidden.' # Only staff, not Guest
            error1["detail"] = "The login or password is wrong."
            out = {"errors": [error1]}
            return {"user": {"username": username, "password": password, "email": email}, "error": out}
        else:
            login(request, user)
    # request.session.set_expiry(600)
    return {"user": user, "error": None}


class LoginGuestView(View): # registration or login of guest
    model = Guest

    def post(self, request):
        not_json = not_app_json(request)
        if not_json:
            return HttpResponseBadRequest(content=json.dumps(not_json), content_type="application/json")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        answer =  check_user(request, body)
        error1 = answer["error"]
        user = answer["user"]
        if user == None:
            return HttpResponseForbidden(content=json.dumps(error1), content_type="application/json")
        if not isinstance(user, dict): # if login allready
            return JsonResponse({"user": user.username, "login": "ok"})
        username = user["username"]
        password = user["password"]
        email = user["email"]
        try:  # Check if username exist
            obj = Guest.objects.get(username=username)
        except Guest.DoesNotExist:
            g = Guest.objects.create_user(username, email, password)
            done = [
                {"username": g.username, "password": password, "date_joined": g.date_joined.strftime('%Y.%m.%d-%H:%M:%S'), "guest": "created",
                 "email": email}] # , "is_superuser": g.is_superuser, "is_staff": g.is_staff
            return JsonResponse({"data": done})
        error1["title"] = "Wrong login post attempt."
        error1["detail"] = "This username already exist."
        out = {"errors": [error1]}
        return HttpResponseBadRequest(content=json.dumps(out), content_type="application/json")


class IndexView(View):
    model = Category

    def get(self, request):
        list_c = Category.objects.order_by('name')
        done = []
        for cat in list_c:
            done.append({"name": cat.name, "id": cat.id})
        return JsonResponse({"data": done})


class DetailView(View):
    model = Product

    def get(self, request, product_id):
        try:
            obj = Product.objects.get(pk = product_id)
        except Product.DoesNotExist:
            return my_response_404(Product, product_id)
        wrap_obj = wrap_products([obj])
        if obj.description != '':
            wrap_obj["data"][0]["description"] = obj.description
        return JsonResponse(wrap_obj)


    def post(self, request, product_id): # Add Product_in_cart
        not_json = not_app_json(request)
        if not_json:
            return HttpResponseBadRequest(content = json.dumps(not_json), content_type = "application/json")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        answer = check_user(request, body)
        error1 = answer["error"]
        if error1:
            return HttpResponseForbidden(content=json.dumps(error1), content_type="application/json")
        user = answer["user"]
        try:
            err = 'quantity'
            quantity = body['quantity']
        except (KeyError):
            if err == 'quantity':
                quantity = 1  #  ignoring quantity
            # else:
            #     error1 = {"status": "400"}
            #     error1["source"] = {"pointer": "/data/" + err}
            #     error1["title"] = "Wrong Post attempt."
            #     error1["detail"] = "No field " + err
            #     out = {"errors": [error1]}
            #     return HttpResponseBadRequest(content=json.dumps(out), content_type="application/json")
        try:
            prod = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return my_response_404(Product, product_id)
        pic = Product_in_cart.objects.create(product  = prod, quantity = quantity)
        guest = Guest.objects.get(username = user.username)
        guest.products_cart.add(pic)
        wr = wrap_products([prod])
        wr["data"][0]["quantity"] = quantity
        wr["data"][0]["in_cart"] = 'Ok'
        wr["username"] = user.username
        return JsonResponse(wr)


class CategoryView(View):
    model = Product

    def get(self, request, category_id, page=1, size=5):
        try:
            cat = Category.objects.get(pk = category_id)
        except Category.DoesNotExist:
            return my_response_404(Category, category_id)
        all = Product.objects.filter(category = cat).order_by('id')
        p = Paginator(all, size)
        return JsonResponse(wrap_products(p.page(page)))


    def post(self, request, category_id):  # Adding of product
        not_json = not_app_json(request)
        if not_json:
            return HttpResponseBadRequest(content = json.dumps(not_json), content_type = "application/json")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        answer = check_user(request, body)
        error1 = answer["error"]
        if error1:
            return HttpResponseForbidden(content=json.dumps(error1), content_type="application/json")
        user = answer["user"]
        if not user.is_staff:
            error1 = {"status": "403"}
            error1["source"] = {"pointer": "/post/user/permissions"}
            error1["title"] = 'Forbidden. Method Post.'
            error1["detail"] = "User have no rights to add products."
            out = {"errors": [error1]}
            return HttpResponseForbidden(content=json.dumps(out), content_type="application/json")
        login(request, user)

        error1 = {"status": "400"}
        try:
            err = 'name'
            product_name = body['name']
            err = 'price'
            price = int(body['price'])
            err = 'provider'
            provider_name = body['provider']
            err = 'description'
            description = body['description']
        except (KeyError):
            if err == 'description':
                description = ''  #  ignoring description
            else:
                error1["source"] = {"pointer": "/data/" + err}
                error1["title"] = "Wrong Post attempt. Product's name, provider and price must be present."
                error1["detail"] = "No field " + err
                out = {"errors": [error1]}
                return HttpResponseBadRequest(content=json.dumps(out), content_type="application/json")
        try:
            cat = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return my_response_404(Category, category_id)
        try:
            provider = Provider.objects.get(name = provider_name)
        except Provider.DoesNotExist:
            return my_response_404(Provider, provider_name)
        p = Product.objects.create(name=product_name, category=cat, price=price, description = description)
        p.providers.add(provider)
        wr = wrap_products([p])
        wr["data"][0]["provider"] = provider_name
        # wr["data"][0]["saved"] = 'Ok'
        return JsonResponse(wr)



