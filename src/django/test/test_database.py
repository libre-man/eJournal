import datetime
from django.test import TestCase
from VLE.models import *


class DataBaseTests(TestCase):
    def test_foreignkeys(self):
        """
        Testing the foreign keys in de database.
        """
        user_test = User(email='lers@uva.nl', username='lers',
                         password='lers123', lti_id='a')
        course_test = Course(name='tname', abbreviation='XXXX',
                             startdate=datetime.date.today())
        user_test.save()
        course_test.save()
        course_test.author = user_test
        ass_test = Assignment(name='tcolloq', description='description')
        ass_test.save()
        ass_test.courses.add(course_test)
        journ_test = Journal(user=user_test, assignment=ass_test)
        journ_test.save()
        entr_test = Entry(journal=journ_test,
                          datetime=datetime.datetime.today(), late=True)
        entr_test.save()

        self.assertEquals(entr_test.journal.pk, journ_test.pk)
        self.assertEquals(journ_test.user.pk, user_test.pk)
        self.assertEquals(journ_test.assignment.pk, ass_test.pk)
        self.assertEquals(course_test.author.pk, user_test.pk)