import base64

from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError

from rest_framework import permissions, status
from rest_framework.decorators import (api_view,
                                       authentication_classes,
                                       permission_classes,
                                       throttle_classes,)
from rest_framework.response import Response
from rest_framework_expiring_authtoken.authentication import (ExpiringTokenAuthentication,)
from rest_framework.throttling import UserRateThrottle

from accounts.permissions import HasVerifiedEmail
from base.utils import paginated_queryset
from .models import (ChallengeHost,
                     ChallengeHostTeam,)
from .serializers import (ChallengeHostSerializer,
                          ChallengeHostTeamSerializer,
                          HostTeamDetailSerializer,)

SECRET_KEY = "thetinggoesskrraapapakakaka"

def ENCODE_DATA(data):
    """
    Turn `data` into a hash and an encoded string, suitable for use with `DECODE_DATA`.
    """
    encoded = []
    for i in data:
        encoded.append(base64.encodestring(i).split("=")[0])
    return encoded


def DECODE_DATA(data):
    """
    The inverse of `ENCODE_DATA`.
    """
    decoded = []
    for i in data:
        decoded.append(base64.decodestring(i+"=="))
    return decoded


@throttle_classes([UserRateThrottle])
@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticated, HasVerifiedEmail))
@authentication_classes((ExpiringTokenAuthentication,))
def challenge_host_team_list(request):

    if request.method == 'GET':
        challenge_host_team_ids = ChallengeHost.objects.filter(user=request.user).values_list('team_name', flat=True)
        challenge_host_teams = ChallengeHostTeam.objects.filter(id__in=challenge_host_team_ids)
        paginator, result_page = paginated_queryset(challenge_host_teams, request)
        serializer = HostTeamDetailSerializer(result_page, many=True)
        response_data = serializer.data
        return paginator.get_paginated_response(response_data)

    elif request.method == 'POST':
        serializer = ChallengeHostTeamSerializer(data=request.data,
                                                 context={'request': request})
        if serializer.is_valid():
            serializer.save()
            response_data = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@throttle_classes([UserRateThrottle])
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes((permissions.IsAuthenticated, HasVerifiedEmail))
@authentication_classes((ExpiringTokenAuthentication,))
def challenge_host_team_detail(request, pk):
    try:
        challenge_host_team = ChallengeHostTeam.objects.get(pk=pk)
    except ChallengeHostTeam.DoesNotExist:
        response_data = {'error': 'ChallengeHostTeam does not exist'}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    if request.method == 'GET':
        serializer = HostTeamDetailSerializer(challenge_host_team)
        response_data = serializer.data
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:

        if request.method == 'PATCH':
            serializer = ChallengeHostTeamSerializer(challenge_host_team,
                                                     data=request.data,
                                                     context={'request': request},
                                                     partial=True)
        else:
            serializer = ChallengeHostTeamSerializer(challenge_host_team,
                                                     data=request.data,
                                                     context={'request': request})
        if serializer.is_valid():
            serializer.save()
            response_data = serializer.data
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        challenge_host_team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@throttle_classes([UserRateThrottle])
@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticated, HasVerifiedEmail))
@authentication_classes((ExpiringTokenAuthentication,))
def challenge_host_list(request, challenge_host_team_pk):

    try:
        challenge_host_team = ChallengeHostTeam.objects.get(pk=challenge_host_team_pk)
    except ChallengeHostTeam.DoesNotExist:
        response_data = {'error': 'ChallengeHostTeam does not exist'}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    if request.method == 'GET':
        challenge_host_status = request.query_params.get('status', None)
        filter_condition = {
            'team_name': challenge_host_team,
            'user': request.user
        }
        if challenge_host_status:
            challenge_host_status = challenge_host_status.split(',')
            filter_condition.update({'status__in': challenge_host_status})

        challenge_host = ChallengeHost.objects.filter(**filter_condition)
        paginator, result_page = paginated_queryset(challenge_host, request)
        serializer = ChallengeHostSerializer(result_page, many=True)
        response_data = serializer.data
        return paginator.get_paginated_response(response_data)

    elif request.method == 'POST':
        serializer = ChallengeHostSerializer(data=request.data,
                                             context={'challenge_host_team': challenge_host_team,
                                                      'request': request})
        if serializer.is_valid():
            serializer.save()
            response_data = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@throttle_classes([UserRateThrottle])
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes((permissions.IsAuthenticated, HasVerifiedEmail))
@authentication_classes((ExpiringTokenAuthentication,))
def challenge_host_detail(request, challenge_host_team_pk, pk):
    try:
        challenge_host_team = ChallengeHostTeam.objects.get(pk=challenge_host_team_pk)
    except ChallengeHostTeam.DoesNotExist:
        response_data = {'error': 'ChallengeHostTeam does not exist'}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    try:
        challenge_host = ChallengeHost.objects.get(pk=pk)
    except ChallengeHost.DoesNotExist:
        response_data = {'error': 'ChallengeHost does not exist'}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    if request.method == 'GET':
        serializer = ChallengeHostSerializer(challenge_host)
        response_data = serializer.data
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        if request.method == 'PATCH':
            serializer = ChallengeHostSerializer(challenge_host,
                                                 data=request.data,
                                                 context={'challenge_host_team': challenge_host_team,
                                                          'request': request},
                                                 partial=True)
        else:
            serializer = ChallengeHostSerializer(challenge_host,
                                                 data=request.data,
                                                 context={'challenge_host_team': challenge_host_team,
                                                          'request': request})
        if serializer.is_valid():
            serializer.save()
            response_data = serializer.data
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        challenge_host.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@throttle_classes([UserRateThrottle])
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, HasVerifiedEmail))
@authentication_classes((ExpiringTokenAuthentication,))
def create_challenge_host_team(request):

    serializer = ChallengeHostTeamSerializer(data=request.data,
                                             context={'request': request})
    if serializer.is_valid():
        serializer.save()
        response_data = serializer.data
        challenge_host_team = serializer.instance
        challenge_host = ChallengeHost(user=request.user,
                                       status=ChallengeHost.SELF,
                                       permissions=ChallengeHost.ADMIN,
                                       team_name=challenge_host_team)
        challenge_host.save()
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@throttle_classes([UserRateThrottle, ])
@api_view(['DELETE', ])
@permission_classes((permissions.IsAuthenticated, HasVerifiedEmail))
@authentication_classes((ExpiringTokenAuthentication, ))
def remove_self_from_challenge_host_team(request, challenge_host_team_pk):
    """
    A user can remove himself from the challenge host team.
    """
    try:
        ChallengeHostTeam.objects.get(pk=challenge_host_team_pk)
    except ChallengeHostTeam.DoesNotExist:
        response_data = {'error': 'ChallengeHostTeam does not exist'}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
    try:
        challenge_host = ChallengeHost.objects.filter(user=request.user.id, team_name__pk=challenge_host_team_pk)
        challenge_host.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except:
        response_data = {'error': 'Sorry, you do not belong to this team.'}
        return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)


@throttle_classes([UserRateThrottle])
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, HasVerifiedEmail))
@authentication_classes((ExpiringTokenAuthentication,))
def email_invite_host_to_team(request, pk):
    try:
        challenge_host_team = ChallengeHostTeam.objects.get(pk=pk)
    except ChallengeHostTeam.DoesNotExist:
        response_data = {'error': 'ChallengeHostTeam does not exist'}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        response_data = {'error': 'User does not exist with this email address!'}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    if email == request.user.email:
        response_data = {'error': 'A host cannot invite himself'}
        return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    team_hash, email_hash = ENCODE_DATA([str(pk), email])
    unique_hash = (team_hash + "/" + email_hash)
    url = request.data['url'].split("team")[0]
    full_url = url + "invitation/" + unique_hash
    team_name = challenge_host_team.team_name
    body = "You've been invited to join the host team {}. " \
           "Click the bottom link to accept the " \
           "invitation and to participate in challenges. \n{}"
    message = body.format(team_name, full_url)
    subject = "You have been invited to join the {} host team at CloudCV!".format(team_name)
    try:
        send_mail(subject,
                  message,
                  "admin@CloudCV.com",
                  [email],
                  fail_silently=False,)
        response_message = "{} has been invited to join the host team {}".format(email, team_name)
        response_data = {'message': response_message}
        return Response(response_data, status=status.HTTP_202_ACCEPTED)
    except BadHeaderError:
        response_data = {'error': 'There was some error while sending the invite.'}
        return Response(response_data, status=status.HTTP_417_EXPECTATION_FAILED)


@throttle_classes([UserRateThrottle])
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, HasVerifiedEmail))
@authentication_classes((ExpiringTokenAuthentication,))
def invitation_accepted(request, team_hash, email_hash):
    pk, accepted_user_email = DECODE_DATA([team_hash, email_hash])
    current_user_email = request.user.email
    challenge_host_team = ChallengeHostTeam.objects.get(pk=pk)
    if current_user_email == accepted_user_email:
        ChallengeHost.objects.get_or_create(user=User.objects.get(email=accepted_user_email),
                                                           status=ChallengeHost.ACCEPTED,
                                                           team_name=challenge_host_team,
                                                           permissions=ChallengeHost.WRITE)
        response_data = {'message': 'You have been successfully added to the host team!'}
        return Response(response_data, status=status.HTTP_202_ACCEPTED)
    response_data = {'error': 'You aren\'t authorized!'}
    return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
