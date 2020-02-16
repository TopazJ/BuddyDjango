from django.shortcuts import render, redirect, reverse, resolve_url
from matching.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
# Create your views here.


def call_match(client):
    for call in Call.objects.filter(cli=client, rating__gt=7.5).order_by('-rating'):
        if call.volunteer.available:
            submit_call(call.id, call.volunteer, client)
            return
    potential_matches = {}
    for interest in ClientInterest.objects.filter(owner=client):
        matching_volunteer_interests = VolunteerInterest.objects.filter(interest=interest)
        for volunteer_interest in matching_volunteer_interests:
            if volunteer_interest.owner.available:
                if volunteer_interest.owner.id in potential_matches.keys():
                    potential_matches[volunteer_interest.owner.id] = interest.rating
                else:
                    potential_matches[volunteer_interest.owner.id] = potential_matches[volunteer_interest.owner.id] + \
                                                                     interest.rating
    if potential_matches:
        v = list(potential_matches.values())
        k = list(potential_matches.keys())
        best_volunteer_id = k[v.index(max(v))]
        best_volunteer = Volunteer.objects.get(id=best_volunteer_id)
        call = Call.objects.create(vol=best_volunteer, cli=client)
        call.save()
        submit_call(call.id, best_volunteer, client)
    else:
        staff_call(client)


def staff_call(client):
    staff = Volunteer.objects.get(staff=True, available=True)
    call = Call.objects.create(vol=staff, cli=client)
    call.save()
    submit_call(call.id, staff, client)


def call_result(data):
    call_id = data['call-id']
    call = Call.objects.get(id=call_id)
    call.volunteer.available = True
    call.save()
    client_difference = data['client-end'] - data['client-begin']
    client_rating = data['client-rating']
    volunteer_rating = data['volunteer-rating']
    transcript = data['transcript']
    results = parse_transcript(transcript)
    average_sentiment = results['sentiment']
    entities = results['entities']
    if call.volunteer.staff:
        user_interests(call.client, entities, 10)
    else:
        rating = abs(client_rating - volunteer_rating) * client_difference * average_sentiment
        call.rating = (rating + (call.rating * call.counter)) / (call.counter + 1)
        call.counter += 1
        call.save()
        user_interests(call.client, entities, rating)


def parse_transcript(transcript):
    # TODO get entity, proper nouns, and sentiment values from Google API using transcript
    return {'sentiment': '', 'entities': []}


def user_interests(client, entities, rating):
    if rating > 7:
        uncovered_interests = ClientInterest.objects.all().filter(client=client)
        for entity in entities:
            was_covered = uncovered_interests.filter(interest=entity)
            if was_covered.exists():
                for interest in was_covered:
                    interest.rating = interest.rating + 1
                    interest.save()
            else:
                ClientInterest.objects.create(interest=entity, rating=5)
            uncovered_interests.exclude(interest=entity)
        for interest in uncovered_interests:
            interest.rating = interest.rating - 1
            interest.save()


def create_call(volunteer, client):
    call = Call.objects.create(vol=volunteer, cli=client)
    call.save()
    return call.id


def submit_call(call_id, volunteer, client):
    volunteer.available = False
    volunteer.save()
    # TODO construct JSON to Evan & Layla here.
    pass


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
                                     phone=request.POST['PhoneNum'], user=user, province=request.POST['Province'],
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


def login_volunteer(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['Email'], password=request.POST['password'])
        return redirect('/modify/')
    return redirect('/')


def volunteer_modify(request):
    if request.user.is_authenticated:
        user = Volunteer.objects.all().get(user=request.user)
        user_details = {'email': user.email}
        return render(request, 'matching/modify.html', user_details)
    else:
        return redirect('/')


def main_page(request):
    return render(request, 'index.html')
