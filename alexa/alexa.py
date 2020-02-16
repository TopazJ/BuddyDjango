from django.http import HttpResponse
from django.http import JsonResponse


def index(request):
    # return HttpResponse("<h1>Hello world!</h1><p>You look like you're searching for the API endpoint</p>")
    return JsonResponse({"response": "Hello world, this works"})
