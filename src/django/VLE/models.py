# Database file
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class User(AbstractUser):
    """
    User is an entity in the database with the following features:
    - email: email of the user.
    - USERNAME_FIELD: username of the username.
    - password: the hash of the password of the user.
    - lti_id: the DLO id of the user.
    """
    email = models.EmailField(
        null=True,
        blank=True,
        unique=True,
    )
    lti_id = models.TextField(
        null=True,
        unique=True,
    )
    profile_picture = models.TextField(
        default='/static/oh_no/oh_no.jpeg'
    )
    grade_notifications = models.BooleanField(
        default=False
    )
    comment_notifications = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.username


class Course(models.Model):
    """
    A Course entity has the following features:
    - name: name of the course.
    - author: the creator of the course.
    - abbrevation: a max three letter abbrevation of the course name.
    - startdate: the date that the course starts.
    """
    name = models.TextField()
    abbreviation = models.TextField(
        max_length=4,
        default='XXXX',
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True
    )
    participations = models.ManyToManyField(
        User,
        related_name='participations',
        through='Participation',
        through_fields=('course', 'user'),
    )

    startdate = models.DateField(
        null=True,
    )
    lti_id = models.TextField(
        # TODO Change if all courses should be linked to a canvas course.
        null=True,
        unique=True,
    )

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    A role defines the permissions of a user group within a course.
    - name: name of the role
    - list of permissions (can_...)
    """
    name = models.TextField()

    can_edit_grades = models.BooleanField(default=False)
    can_view_grades = models.BooleanField(default=False)
    can_edit_assignment = models.BooleanField(default=False)
    can_view_assignment = models.BooleanField(default=False)
    can_submit_assignment = models.BooleanField(default=False)


class Participation(models.Model):
    """
    A participation defines the way a user interacts within a certain course.
    The user is now linked to the course, and has a set of permissions
    associated with it's role.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.ForeignKey(
        Role,
        null=True,
        on_delete=models.SET_NULL,
        related_name='role',
    )


class Assignment(models.Model):
    """
    An Assignment entity has the following features:
    - name: name of the assignment.
    - description: description for the assignment.
    - courses: a foreign key linked to the courses this assignment
    is part of.
    - format: a one-to-one key linked to the format this assignment
    holds. The format determines how a students' journal is structured.
    """
    name = models.TextField()
    deadline = models.DateTimeField(
        null=True,
    )
    description = models.TextField(
        null=True,
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True
    )
    points_possible = models.IntegerField(
        'points_possible',
        null=True
    )
    lti_id = models.TextField(
        'lti_id',
        # TODO Change if all assignments should be linked to a canvas course.
        null=True
    )
    courses = models.ManyToManyField(Course)

    format = models.OneToOneField(
        'JournalFormat',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Journal(models.Model):
    """
    A journal is a collection of Nodes that holds the student's
    entries, deadlines and more. It contains the following:
    - assignment: a foreign key linked to an assignment.
    - user: a foreign key linked to a user.
    """
    assignment = models.ForeignKey(
        'Assignment',
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.assignment.name + " from " + self.user.username

    class Meta:
        """
        A class for meta data.
        - unique_together: assignment and user must be unique together.
        """
        unique_together = ('assignment', 'user',)


class Node(models.Model):
    """
    The Node is an EDAG component.
    It can represent many things.
    There are three types of nodes:
    -Progress
        A node that merely is a deadline,
        and contains no entry. This deadline
        contains a 'target point amount'
        which should be reached before the
        deadline has passed.
        This type of node has to be predefined in
        the Format. In the Format it is assigned a
        deadline and a 'target point amount'.
    -Entry
        A node that is merely an entry,
        and contains no deadline. The entry
        can count toward a total
        'received point amount' which is deadlined
        by one or more Progress nodes.
        This type node can be created by the student
        an unlimited amount of times. It holds one
        of the by format predefined 'global templates'.
    -Entrydeadline
        A node that is both an entry and a deadline.
        This node is entirely separate from the
        Progress and Entry node.
        This type of node has to be predefined in
        the Format. In the Format it is assigned a
        deadline and a 'forced template'.
    """
    PROGRESS = 'p'
    ENTRY = 'e'
    ENTRYDEADLINE = 'd'
    TYPES = (
        (PROGRESS, 'progress'),
        (ENTRY, 'entry'),
        (ENTRYDEADLINE, 'entrydeadline'),
    )

    type = models.TextField(
        max_length=4,
        choices=TYPES,
    )

    entry = models.OneToOneField(
        'Entry',
        null=True,
        on_delete=models.CASCADE,
    )

    journal = models.ForeignKey(
        'Journal',
        on_delete=models.CASCADE,
    )

    preset = models.ForeignKey(
        'PresetNode',
        null=True,
        on_delete=models.CASCADE,
    )


class JournalFormat(models.Model):
    """
    Format of a journal.
    The format determines how a students' journal is structured.
    See PresetNodes for attached 'default' nodes.
    - available_templates are those available in 'Entry' nodes.
      'Entrydeadline' nodes hold their own forced template.
    """
    available_templates = models.ManyToManyField(
        'EntryTemplate',
    )

    def __str__(self):
        return str(self.pk)


class PresetNode(models.Model):
    """
    A preset node is a node that has been pre-defined by the teacher.
    It contains the following features:
    - type: the type of the preset node (progress or entrydeadline node).
    - deadline: the deadline for this preset node.
    - forced_template: the template for this preset node - null if PROGRESS node.
    - format: a foreign key linked to a format.
    """
    TYPES = (
        (Node.PROGRESS, 'progress'),
        (Node.ENTRYDEADLINE, 'entrydeadline'),
    )

    type = models.TextField(
        max_length=4,
        choices=TYPES,
    )

    deadline = models.OneToOneField(
        'Deadline',
        on_delete=models.CASCADE,
    )

    forced_template = models.ForeignKey(
        'EntryTemplate',
        on_delete=models.SET_NULL,
        null=True,
    )

    format = models.ForeignKey(
        'JournalFormat',
        on_delete=models.CASCADE
    )


class Deadline(models.Model):
    """A Deadline has the following features:
    - datetime: the date where the deadline closes
    - points: optionally the amount of points required for this deadline.
    """

    datetime = models.DateTimeField(
        default=now
    )
    points = models.IntegerField(
        null=True,
    )

    def __str__(self):
        return str(self.pk)


class Entry(models.Model):
    """An Entry has the following features:
    - journal: a foreign key linked to an Journal.
    - createdate: the date and time when the entry was posted.
    - late: if the entry was posted late or not.
    - TODO: edited_at
    """
    template = models.ForeignKey(
        'EntryTemplate',
        on_delete=models.SET_NULL,
        null=True
    )
    createdate = models.DateTimeField(
        default=now,
    )
    grade = models.IntegerField(
        default=0
    )

    def __str__(self):
        return str(self.pk)


class EntryTemplate(models.Model):
    """
    A template for an Entry.
    """
    name = models.TextField()

    def __str__(self):
        return self.name


class Field(models.Model):
    """
    Defines the fields of an EntryTemplate
    """
    TEXT = 't'
    IMG = 'i'
    FILE = 'f'
    TYPES = (
        (TEXT, 'text'),
        (IMG, 'img'),
        (FILE, 'file'),
    )
    type = models.TextField(
        max_length=4,
        choices=TYPES,
        default=TEXT,
    )
    title = models.TextField()
    location = models.IntegerField()
    template = models.ForeignKey(
        'EntryTemplate',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.template.name + " field: " + self.location


class Content(models.Model):
    """
    Defines the content of an Entry
    """
    entry = models.ForeignKey(
        'Entry',
        on_delete=models.CASCADE
    )
    field = models.ForeignKey(
        'Field',
        on_delete=models.SET_NULL,
        null=True
    )
    data = models.TextField()
