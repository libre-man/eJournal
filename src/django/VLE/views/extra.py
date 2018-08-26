"""
extra.py.

In this file are all the extra api requests.
This includes:
    /names/ -- to get the names belonging to the ids
"""
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

import VLE.views.responses as response
from VLE.models import Course, Journal, Assignment, Template
import VLE.permissions as permissions
import VLE.lti_launch as lti

import datetime
import json
import jwt

# VUE ENTRY STATE
BAD_AUTH = '-1'

NO_USER = '0'
LOGGED_IN = '1'

NO_COURSE = '0'
NO_ASSIGN = '1'
NEW_COURSE = '2'
NEW_ASSIGN = '3'
FINISH_T = '4'
FINISH_S = '5'
GRADE_CENTER = '6'


@api_view(['GET'])
def names(request, course_id, assignment_id, journal_id):
    """Get names of course, assignment, journal.

    Arguments:
    request -- the request that was sent
        course_id -- optionally the course id
        assignment_id -- optionally the assignment id
        journal_id -- optionally the journal id

    Returns a json string containing the names of the set fields.
    course_id populates 'course', assignment_id populates 'assignment', tID populates
    'template' and journal_id populates 'journal' with the users' name.
    """
    if not request.user.is_authenticated:
        return response.unauthorized()

    result = {}
    try:
        if course_id:
            course = Course.objects.get(pk=course_id)
            role = permissions.get_role(request.user, course)
            if role is None:
                return response.forbidden('You are not allowed to view this course.')
            result['course'] = course.name
        if assignment_id:
            assignment = Assignment.objects.get(pk=assignment_id)
            if not (assignment.courses.all() & request.user.participations.all()):
                return response.forbidden('You are not allowed to view this assignment.')
            result['assignment'] = assignment.name
        if journal_id:
            journal = Journal.objects.get(pk=journal_id)
            if not (journal.user == request.user or permissions.has_assignment_permission(request.user,
                    journal.assignment, 'can_view_assignment_participants')):
                return response.forbidden('You are not allowed to view journals of other participants.')
            result['journal'] = journal.user.first_name + " " + journal.user.last_name

    except (Course.DoesNotExist, Assignment.DoesNotExist, Journal.DoesNotExist, Template.DoesNotExist):
        return response.not_found('Course, Assignment, Journal or Template does not exist.')

    return response.success({'names': result})


@api_view(['GET'])
def get_lti_params_from_jwt(request, jwt_params):
    """Handle the controlflow for course/assignment create, connect and select.

    Returns the data needed for the correct entry place.
    """
    if not request.user.is_authenticated:
        return response.unauthorized()

    user = request.user
    lti_params = jwt.decode(jwt_params, settings.LTI_SECRET, algorithms=['HS256'])
    roles = json.load(open('config.json'))
    lti_roles = dict((roles[k], k) for k in roles)
    role = lti_roles[lti_params['roles']]

    payload = dict()
    course = lti.check_course_lti(lti_params, user, role)
    if course is None:
        if role == 'Teacher':
            payload['state'] = NEW_COURSE
            payload['lti_cName'] = lti_params['context_title']
            payload['lti_abbr'] = lti_params['context_label']
            payload['lti_cID'] = lti_params['context_id']
            payload['lti_aName'] = lti_params['resource_link_title']
            payload['lti_aID'] = lti_params['resource_link_id']

            if 'custom_canvas_assignment_points_possible' in lti_params:
                payload['lti_points_possible'] = lti_params['custom_canvas_assignment_points_possible']

            return response.success(payload={'params': payload})
        else:
            return response.not_found(description='The assignment you are looking for cannot be found. \
                <br>Note: it might still be reachable through the assignment section')

    assignment = lti.check_assignment_lti(lti_params)
    if assignment is None:
        if role == 'Teacher':
            payload['state'] = NEW_ASSIGN
            payload['cID'] = course.pk
            payload['lti_aName'] = lti_params['resource_link_title']
            payload['lti_aID'] = lti_params['resource_link_id']

            if 'custom_canvas_assignment_points_possible' in lti_params:
                payload['lti_points_possible'] = lti_params['custom_canvas_assignment_points_possible']

            return response.success(payload={'params': payload})
        else:
            return response.not_found(description='The assignment you are looking for cannot be found. \
                <br>Note: it might still be reachable through the assignment section')

    journal = lti.select_create_journal(lti_params, user, assignment, roles)
    jID = journal.pk if journal is not None else None
    state = FINISH_T if jID is None else FINISH_S

    payload['state'] = state
    payload['cID'] = course.pk
    payload['aID'] = assignment.pk
    payload['jID'] = jID
    return response.success(payload={'params': payload})


@api_view(['POST'])
def lti_launch(request):
    """Django view for the lti post request.

    handles the users login or sned to a creation page.
    """
    secret = settings.LTI_SECRET
    key = settings.LTI_KEY

    authenticated, err = lti.OAuthRequestValidater.check_signature(
        key, secret, request)

    if authenticated:
        roles = json.load(open('config.json'))
        params = request.POST.dict()
        user = lti.check_user_lti(params, roles)

        params['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        lti_params = jwt.encode(params, secret, algorithm='HS256').decode('utf-8')

        if user is None:
            q_names = ['state', 'lti_params']
            q_values = [NO_USER, lti_params]

            if 'lis_person_name_full' in params:
                fullname = params['lis_person_name_full']
                splitname = fullname.split(' ')
                firstname = splitname[0]
                lastname = fullname[len(splitname[0])+1:]
                q_names += ['firstname', 'lastname']
                q_values += [firstname, lastname]

            if 'lis_person_sourcedid' in params:
                q_names.append('username')
                q_values.append(params['lis_person_sourcedid'])

            if 'lis_person_contact_email_primary' in params:
                q_names.append('email')
                q_values.append(params['lis_person_contact_email_primary'])

            return redirect(lti.create_lti_query_link(q_names, q_values))

        refresh = TokenObtainPairSerializer.get_token(user)
        access = refresh.access_token
        return redirect(lti.create_lti_query_link(['lti_params', 'jwt_access', 'jwt_refresh', 'state'],
                                                  [lti_params, access, refresh, LOGGED_IN]))

    return redirect(lti.create_lti_query_link(['state'], [BAD_AUTH]))
