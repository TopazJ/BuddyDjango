from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json


@csrf_exempt
def index(request):
    # debug_data = {
    #     # 'META': request.META,
    #     # 'headers': request.headers,
    #     'method': str(request.method),
    #     'content_type': request.content_type,
    #     'body': json.loads(request.body),
    #     # 'POST': str(request.POST),
    # }
    # print("!!! request is: ", request.META)
    # print("headers", request.headers)
    # print("method", request.method)
    # print("body", request.body)
    # print("POST", request.POST)
    # print('-----------------------------------------')
    # welcome_progressive_response(request)

    req_body = json.loads(request.body)
    req_type = req_body['request']['type']
    if req_type == "SessionEndedRequest":
        print("I received a SessionEndedRequest. Bye bye!")
        return JsonResponse({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Goodbye.",
                }
            }
        })

    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                # "text": "Hi. Welcome to buddy. One moment while I search for someone to chat with.",
                "text": "Welcome to buddy.",
            },
            # "shouldEndSession": True,
        },
    }

    print("!!! RICHARD debug 8:39 am, response: ", response)

    return JsonResponse(response)


# def welcome_progressive_response(request):
#     ssml = "<speak>Hi! Let's chat. Please wait a moment while I search for people to chat with.</speak>"
#     post_progressive_response(request, ssml)
#
#
# def post_progressive_response(request, ssml):
#     request_body = json.loads(request.body)
#     request_System = request_body['context']['System']
#
#     request_id = request_body['request']['requestId']
#     api_access_token = request_System['apiAccessToken']
#     api_endpoint = request_System['apiEndpoint']
#     full_api_endpoint = api_endpoint + "/v1/directives"
#     application_id = request_System['application']['applicationId']
#
#     headers = {
#         "Authorization": "Bearer " + api_access_token,
#         "Content-Type": "application/json",
#     }
#
#     body = {
#         "header": {
#             "requestId": request_id
#         },
#         "directive": {
#             "type": "VoicePlayer.Speak",
#             "speech": ssml
#         }
#     }
#
#     resp = requests.post(full_api_endpoint, headers=headers, data=body)
#
#     if resp.status_code != 204:
#         print("ERROR! Progressive response has failed!")
#         print("Alexa request: ", request, "SSML: ", ssml)
#     print("resp: ", resp.status_code, resp.text)
#
