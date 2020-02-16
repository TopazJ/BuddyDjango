from django.shortcuts import render, redirect, reverse, resolve_url
from matching.models import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth import authenticate
import requests
import json
# Create your views here.


@csrf_exempt
def user_request(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        first_name = 'Richard'
        last_name = 'Lee'
        phone = data['phone']
        if not Client.objects.all().filter(phone='+1'+phone).exists():
            print("SHAMEZ DEBUG HERE!!!")
            client = Client.objects.create(first_name=first_name, last_name=last_name, phone='+1'+phone)
            print("SHAMEZ DEBUG HERE AGAIN!!!")
            return staff_call(client)
        else:
            client = Client.objects.get(phone='+1'+phone)
            return call_match(client)


def call_match(client):
    for call in Call.objects.filter(client=client, rating__gt=7.5).order_by('-rating'):
        if call.volunteer.available:
            return submit_call(call.volunteer, client)
    potential_matches = {}
    for interest in ClientInterest.objects.filter(owner=client):
        matching_volunteer_interests = VolunteerInterest.objects.filter(interest=interest.interest)
        for volunteer_interest in matching_volunteer_interests:
            if volunteer_interest.owner.available:
                if volunteer_interest.owner.id in potential_matches.keys():
                    potential_matches[volunteer_interest.owner.id] = potential_matches[volunteer_interest.owner.id] + interest.rating
                else:
                    potential_matches[volunteer_interest.owner.id] = interest.rating
    if potential_matches:
        v = list(potential_matches.values())
        k = list(potential_matches.keys())
        best_volunteer_id = k[v.index(max(v))]
        best_volunteer = Volunteer.objects.get(id=best_volunteer_id)
        if not Call.objects.all().filter(volunteer=best_volunteer, client=client).exists():
            call = Call.objects.create(volunteer=best_volunteer, client=client)
            call.save()
        return submit_call(best_volunteer, client)
    else:
        return staff_call(client)


def staff_call(client):
    staff = Volunteer.objects.get(staff=True, available=True)
    if not Call.objects.all().filter(volunteer=staff, client=client).exists():
        call = Call.objects.create(volunteer=staff, client=client)
        call.save()
    return submit_call(staff, client)


@csrf_exempt
def call_result(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        client = Client.objects.get(phone=data['client-phone'])
        volunteer = Volunteer.objects.get(phone=data['volunteer-phone'])
        call = Call.objects.get(client=client, volunteer=volunteer)
        call.volunteer.available = True
        call.save()
        # client_difference = data['client-end'] - data['client-begin']
        # client_rating = data['client-rating']
        client_rating = int(data['client-rating'])
        # volunteer_rating = data['volunteer-rating']
        # transcript = data['transcript']
        # results = parse_transcript(transcript)
        # average_sentiment = results['sentiment']
        # entities = results['entities']
        entities = ['video games', 'laptops', 'stress', 'school', 'friends', 'baseball', 'basketball']
        if call.volunteer.staff:
            return user_interests(call.client, entities, 10)
        else:
            # rating = abs(client_rating - volunteer_rating) * client_difference * average_sentiment
            rating = client_rating
            call.rating = (rating + (call.rating * call.counter)) / (call.counter + 1)
            call.counter += 1
            call.save()
            return user_interests(call.client, entities, rating)


def parse_transcript(transcript):
    # TODO get entity, proper nouns, and sentiment values from Google API using transcript
    return {'sentiment': '', 'entities': []}


def user_interests(client, entities, rating):
    if rating > 7:
        uncovered_interests = ClientInterest.objects.all().filter(owner=client)
        covered_interests = ClientInterest.objects.none()
        for entity in entities:
            was_covered = uncovered_interests.filter(interest=entity)
            if was_covered.exists():
                covered_interests = covered_interests | was_covered
                for interest in was_covered:
                    interest.rating = interest.rating + 1
                    interest.save()
            else:
                ClientInterest.objects.create(owner=client, interest=entity, rating=6)
        uncovered_interests = ClientInterest.objects.exclude(id__in=covered_interests)
        for interest in uncovered_interests:
            interest.rating = interest.rating - 1
            interest.save()
    response = HttpResponse()
    response.status_code = 200
    return response


def submit_call(volunteer, client):
    # volunteer.available = False
    # volunteer.save()
    post_data = {
        "to": {
            "name": volunteer.first_name + volunteer.last_name,
            "number": volunteer.phone
        },

        "from": {
            "name": client.first_name + client.last_name,
            "number": client.phone
        }
    }
    requests.post('https://krul.ca/api/sms/callrequest',  json=post_data, verify=False)
    response = HttpResponse()
    response.status_code = 200
    return response


def signup_volunteer(request):
    return render(request, 'matching/signup.html')


def create_volunteer(request):
    if request.method == 'POST':
        if User.objects.filter(email=request.POST['Email']).exists():
            return render(request, 'matching/signup.html', {'email': True})
        elif Volunteer.objects.filter(phone=request.POST['PhoneNum']).exists():
            return render(request, 'matching/signup.html', {'phone': True})
        else:
            user = User.objects.create(username=request.POST['Email'], password=request.POST['password'],
                                       email=request.POST['Email'])
            user.save()
            volunteer = Volunteer.objects.create(first_name=request.POST['FName'], last_name=request.POST['LName'],
                                     phone='+1'+request.POST['PhoneNum'], user=user, province=request.POST['Province'],
                                     city=request.POST['City'])
            volunteer.save()
            i = 0
            interests = []
            while 'mytext['+str(i)+']' in request.POST.keys():
                interests.append(request.POST['mytext['+str(i)+']'])
                i += 1
            for interest in interests:
                vi = VolunteerInterest.objects.create(interest=str(interest).lower(), owner=volunteer)
                vi.save()
    return render(request, 'thanks.html')

# TODO WIP - Users can change their info.
# def login_volunteer(request):
#     if request.method == 'POST':
#         user = authenticate(username=request.POST['Email'], password=request.POST['password'])
#         return redirect('/modify/')
#     return redirect('/')
#
#
# def volunteer_modify(request):
#     if request.user.is_authenticated:
#         user = Volunteer.objects.all().get(user=request.user)
#         user_details = {'email': user.email}
#         return render(request, 'matching/modify.html', user_details)
#     else:
#         return redirect('/')


def main_page(request):
    return render(request, 'index.html')
