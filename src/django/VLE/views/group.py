"""
group.py.

In this file are all the group api requests.
"""
from rest_framework import viewsets
# from rest_framework.decorators import action

import VLE.serializers as serialize
import VLE.views.responses as response
from VLE.models import Course, Group
import VLE.permissions as permissions
import VLE.utils.generic_utils as utils
import VLE.factory as factory


class GroupView(viewsets.ViewSet):
    serializer_class = serialize.GroupSerializer

    def create(self, request):
        """Create a new course group.

        Arguments:
        request -- the request that was send with
            name -- name of the course group
            cID -- course ID of the course
            lti_id -- (optional) lti_id to link the course to

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            forbidden -- when the user has no permission to create new groups
        On success, with the course group.
        """
        user = request.user
        if not user.is_authenticated:
            return response.unauthorized()

        try:
            name, cID = utils.required_params(request.data, "name", "cID")
            lti_id = utils.optional_params(request.data, 'lti_id')
        except KeyError:
            return response.keyerror("name", "cID")

        # TODO Look for which permission check is better
        # role = permissions.get_role(user, cID)
        # if not role.can_add_course_user_group:
        #     return response.forbidden("You have no permissions to create a course group.")
        perm = permissions.get_permissions(request.user)
        if not perm['can_add_course_group']:
            return response.forbidden('You have no permissions to create a course.')

        try:
            course = Course.objects.get(pk=cID)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        if Group.objects.get(name=name, course=course):
            return response.bad_request('Course group already exists')
        else:
            course_group = factory.make_course_group(name, course, lti_id)

        return response.created(payload={'course': serialize.group_to_dict(course_group)})

    def partial_update(self, request, *args, **kwargs):
        """Update an existing course group.

        Arguments:
        request -- request data
        data -- the new data for the course group
        pk -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exists
            forbidden -- when the user is not in the course
            unauthorized -- when the user is unauthorized to edit the course
            bad_request -- when there is invalid data in the request
        On success:
            success -- with the new course data
        """
        pk = kwargs.get('pk')
        # TODO: Check if its a partcipation with the correct rights
        if not request.user.is_authenticated or \
           not request.user.participations.filter(pk=pk):
            return response.unauthorized()

        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return response.not_found('course')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not in this course.')
        elif not role.can_edit_course_group:
            return response.unauthorized('You are unauthorized to edit this course group.')

        if Group.objects.get(name=request.data['name'], course=course):
            return response.bad_request('Course group already exists')

        serializer = self.serializer_class(course, data=request.data, partial=True)
        if not serializer.is_valid():
            response.bad_request()
        serializer.save()
        return response.success({'group': serializer.data})

        def destroy(self, request, *args, **kwargs):
            """Delete an existing course group.

            Arguments:
            request -- request data
            pk -- course ID

            Returns:
            On failure:
                not found -- when the course does not exists
                unauthorized -- when the user is not logged in
                forbidden -- when the user is not in the course
            On success:
                success -- with a message that the course group was deleted
            """
            if not request.user.is_authenticated:
                return response.unauthorized()
            pk = kwargs.get('pk')

            try:
                course = Course.objects.get(pk=pk)
            except Course.DoesNotExist:
                return response.not_found('course')

            role = permissions.get_role(request.user, pk)
            if role is None:
                return response.unauthorized(description="You are unauthorized to view this course.")
            elif not role.can_delete_course:
                return response.forbidden(description="You are unauthorized to delete this course group.")

            try:
                group = Group.objects.get(name=request.data['name'], course=course)
            except Group.DoesNotExist:
                response.not_found('group')

            group.delete()
            return response.success(description='Sucesfully deleted course group.')
