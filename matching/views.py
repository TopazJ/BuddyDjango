from django.shortcuts import render, redirect
from matching.models import *
# Create your views here.


def call_match(client):

    for call in Call.objects.filter(client=client, rating__gt=7.5).order_by('-rating'):
        if call.volunteer.available:
            submit_call(call.id, call.volunteer, client)
            return

    potential_matches = {}
    for interest in ClientInterest.objects.filter(owner=client):
        matching_volunteers = VolunteerInterest.objects.filter(interest=interest)
        for volunteer in matching_volunteers:
            if volunteer.available:
                if volunteer.id in potential_matches.keys():
                    potential_matches[volunteer.id] = interest.rating
                else:
                    potential_matches[volunteer.id] = potential_matches[volunteer.id] + interest.rating
    if potential_matches:
        v = list(potential_matches.values())
        k = list(potential_matches.keys())
        best_volunteer_id = k[v.index(max(v))]
        best_volunteer = Volunteer.objects.get(id=best_volunteer_id)
        call = Call.objects.create(volunteer=best_volunteer, client=client)
        call.save()
        submit_call(call.id, best_volunteer, client)
    else:
        staff_call(client)


def staff_call(client):
    staff = Volunteer.objects.get(staff=True, available=True)
    call = Call.objects.create(volunteer=staff, client=client)
    call.save()
    submit_call(call.id, staff, client)


def call_result(data):
    call_id = data['call-id']
    client_difference = data['client-end'] - data['client-begin']
    client_rating = data['client-rating']
    volunteer_rating = data['volunteer-rating']
    transcript = data['transcript']
    results = parse_transcript(transcript)
    average_sentiment = results['sentiment']
    entities = results['entities']
    rating = abs(client_rating-volunteer_rating) * client_difference * average_sentiment
    call = Call.objects.get(id=call_id)
    call.rating = (rating + (call.rating * call.counter))/(call.counter + 1)

    if call.volunteer.staff:
        user_interests(call.client, entities, 10)
    else:
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
    call = Call.objects.create(volunteer=volunteer, client=client)
    return call.id


def submit_call(call_id, volunteer, client):
    volunteer.available = False
    # TODO construct JSON to Evan & Layla here.
    pass


def signup_volunteer(request):
    return render(request, 'matching/signup.html')


def create_volunteer(request):
    if request.method == 'POST':
        print(request.POST)
    return render(request, 'index.html')


def main_page(request):
    return render(request, 'index.html')
