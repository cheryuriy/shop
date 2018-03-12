from .models import Product, Provider, Category
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.http import HttpResponseBadRequest
import json


def wrap_products(list_p):
    done = []
    for prod in list_p:
        done.append({"name": prod.name, "category" : prod.category.name,
                     "incoming_date": prod.incoming_date.strftime('%Y.%m.%d-%H:%M:%S')})
    return {"data": done}


class DetailView(View):
    model = Product

    def get(self, request, product_id):
        s = get_object_or_404(Product, pk=product_id)
        return JsonResponse(wrap_products([s]))


class CategoryView(View):
    model = Product

    def get(self, request, category_id):
        cat = get_object_or_404(Category, pk=category_id)
        all = Product.objects.filter(category = cat) # need pagination
        return JsonResponse(wrap_products(all))

    def post(self, request, category_id):
        error1 = {"status":"400"}
        if request.content_type != "application/json":
            error1["source"] = {"pointer": "/post/content_type/application_json"}
            error1["detail"] = 'Wrong POST attempt. "Content-Type: application/json".'
            out = {"errors": [error1]}
            return HttpResponseBadRequest(content = json.dumps(out), content_type = "application/json")
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            err = 'name'
            product_name = body['name']
            # err = 'description'
            # description = body['description']
            category_name = get_object_or_404(Category, pk=category_id)
            s = Product.objects.create(name = product_name, category = category_name) # description = description
            wr = wrap_products([s])
            # wr["data"][0]["saved"] = 'Ok'
            return JsonResponse(wr)
        except (KeyError):
            error1["source"] = {"pointer": "/data/" + err}
            error1["detail"] = 'Wrong POST attempt. Field "name" must be present.'
            out = {"errors": [error1]}
            return HttpResponseBadRequest(content = json.dumps(out), content_type="application/json")

# curl -i -H "Content-Type: application/json" -X POST -d '{"name": "1_Post"}' http://127.0.0.1:8000/shop/1/


class IndexView(View):
    model = Category

    def get(self, request):
        list_c = Category.objects.order_by('-name')
        done = []
        for cat in list_c:
            done.append({"name": cat.name})
        return JsonResponse({"data": done})



