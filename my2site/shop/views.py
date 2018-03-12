from .models import Product, Provider, Category
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.views import View
from django.http import HttpResponseBadRequest
import json

def my_response_404(clas, obj_id):
    error1 = {"status": "404"}
    error1["source"] = {"pointer": "/data/" + str(clas) + "/obj_id"}
    error1["detail"] = 'Object With Id = ' + str(obj_id) + ' Does Not Exist.'
    out = {"errors": [error1]}
    return HttpResponseNotFound(json.dumps(out), content_type="application/json")


def wrap_products(list_p):
    done = []
    for prod in list_p:
        done.append({"name": prod.name,
                     "incoming_date": prod.incoming_date.strftime('%Y.%m.%d-%H:%M:%S')})
    return {"category" : prod.category.name, "data": done}


class DetailView(View):
    model = Product

    def get(self, request, product_id):
        try:
            obj = Product.objects.get(pk = product_id)
        except Product.DoesNotExist:
            return my_response_404(Product, product_id)
        return JsonResponse(wrap_products([obj]))


class CategoryView(View):
    model = Product

    def get(self, request, category_id):
        try:
            cat = Category.objects.get(pk = category_id)
        except Category.DoesNotExist:
            return my_response_404(Category, category_id)
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
        except (KeyError):
            error1["source"] = {"pointer": "/data/" + err}
            error1["detail"] = 'Wrong POST attempt. Product "name" must be present.'
            out = {"errors": [error1]}
            return HttpResponseBadRequest(content=json.dumps(out), content_type="application/json")
        try:
            cat = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return my_response_404(Category, category_id)
        s = Product.objects.create(name=product_name, category=cat)  # description = description
        wr = wrap_products([s])
        # wr["data"][0]["saved"] = 'Ok'
        return JsonResponse(wr)


# curl -i -H "Content-Type: application/json" -X POST -d '{"name": "1_Post"}' http://127.0.0.1:8000/shop/1/

class IndexView(View):
    model = Category

    def get(self, request):
        list_c = Category.objects.order_by('name')
        done = []
        for cat in list_c:
            done.append({"name": cat.name, "id": cat.id})
        return JsonResponse({"data": done})



