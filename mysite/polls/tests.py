import datetime
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Question, Choice

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_choice(choice_text, question_id):
    """
    Create a choice for a question
    """

    return Choice.objects.create(choice_text=choice_text, question_id=question_id)

class QuestionModelTests(TestCase):
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

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")

    def test_question_no_choice(self):
        question = create_question("how old is this question?", -30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")

    def test_question_no_choice_is_admin(self):
        question = create_question("how old is this question?", -30)
        self.client.cookies.load({ 'sessionid': '123' })
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )

    def test_past_question(self):
        question = create_question("how old is this question?", -30)
        create_choice("its so new", question.id)
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
        create_choice("its so new", old_question.id)
        create_question("is it new?", 30)

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [old_question]
        )

    def test_multiple_future_and_past_questions(self):
        old_question = create_question("is it old?", -30)
        create_choice("its so new", old_question.id)
        old_question_2 = create_question("is it old?", -32)
        create_choice("its so new", old_question_2.id)
        create_question("is it new?", 30)
        create_question("is it new?", 31)

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [old_question, old_question_2]
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question("cant see it", 30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question("can see it", -30)
        create_choice("yerp", past_question.id)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)

    def test_past_question_no_choice(self):
        past_question = create_question("can see it", -30)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_past_question_no_choice_is_admin(self):
        past_question = create_question("can see it", -30)
        url = reverse('polls:detail', args=(past_question.id,))
        self.client.cookies.load({ 'sessionid': '123' })
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)

class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question("cant see it", 30)
        create_choice("dont look", future_question.id)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question("can see it", -30)
        create_choice("see look", past_question.id)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)

    def test_past_question_no_choice(self):
        past_question = create_question("can see it", -30)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
