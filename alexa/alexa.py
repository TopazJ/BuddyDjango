from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):
    response = {
      "version": "string",
      "sessionAttributes": {
        "key": "value"
      },
      "response": {
        "outputSpeech": {
          "type": "PlainText",
          "text": "Hi I'm buddy",
          "playBehavior": "REPLACE_ENQUEUED"
        },
        # "card": {
        #   "type": "Standard",
        #   "title": "Title of the card",
        #   "text": "Text content for a standard card",
        #   "image": {
        #     "smallImageUrl": "https://url-to-small-card-image...",
        #     "largeImageUrl": "https://url-to-large-card-image..."
        #   }
        # },
        "reprompt": {
          "outputSpeech": {
            "type": "PlainText",
            "text": "Hi this is buddy reprompt",
            "playBehavior": "REPLACE_ENQUEUED"
          }
        },
        "directives": [
          {
            "type": "InterfaceName.Directive"
            # (...properties depend on the directive type)
          }
        ],
        "shouldEndSession": True
      }
    }
    return JsonResponse(response)
