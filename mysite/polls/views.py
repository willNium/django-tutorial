from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.db.models import Count

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    is_admin = False

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        cookies = request.headers['Cookie']
        if 'sessionid' in cookies:
            self.is_admin = True

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.is_admin == True:
            return (Question.objects
                    .filter(pub_date__lte=timezone.now())
                    .order_by('-pub_date')[:5]
                    )
        else:
            """Return the last five published questions."""
            return (Question.objects
                .filter(pub_date__lte=timezone.now())
                .annotate(num_choices=Count('choice'))
                .filter(num_choices__gt=0)
                .order_by('-pub_date')[:5]
            )


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    is_admin = False

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if 'sessionid' in request.COOKIES:
            self.is_admin = True

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """

        if self.is_admin == True:
            return Question.objects.filter(pub_date__lte=timezone.now())
        else:
            return (Question.objects
                .filter(pub_date__lte=timezone.now())
                .annotate(num_choices=Count('choice'))
                .filter(num_choices__gt=0)
            )

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'
    is_admin = False

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if 'sessionid' in request.COOKIES:
            self.is_admin = True

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """

        if self.is_admin == True:
            return Question.objects.filter(pub_date__lte=timezone.now())
        else:
            return (Question.objects
                    .filter(pub_date__lte=timezone.now())
                    .annotate(num_choices=Count('choice'))
                    .filter(num_choices__gt=0)
                    )

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
      selected_choice = question.choice_set.get(pk= request.POST["choice"])

    except (KeyError, Choice.DoesNotExist):
      return render(request, 'polls/detail.html', {
        'question': question,
        'error_message': "You didn't select a choice."
      })
    else:
      selected_choice.votes += 1
      selected_choice.save()

      return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
