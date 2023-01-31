import datetime
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Question

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionModelTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")

    def test_past_question(self):
        question = create_question("how old is this question?", -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
          response.context['latest_question_list'],
          [question]
        )

    def test_future_question(self):
        question = create_question("how new is this question?", 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_questions(self):
        old_question = create_question("is it old?", -30)
        create_question("is it new?", 30)

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
          response.context['latest_question_list'],
          [ old_question ]
        )

    def test_multiple_future_and_past_questions(self):
        old_question = create_question("is it old?", -30)
        old_question_2 = create_question("is it old?", -32)
        new_question = create_question("is it new?", 30)
        new_question_2 = create_question("is it new?", 31)

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [old_question, old_question_2]
        )

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date= time)
        self.assertIs(old_question.was_published_recently(), False)
        

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), True)
