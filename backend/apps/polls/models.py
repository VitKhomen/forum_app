from django.db import models
from django.conf import settings


class Poll(models.Model):
    post = models.OneToOneField(
        'main.Post', on_delete=models.CASCADE,
        related_name='poll', null=True, blank=True
    )
    question = models.CharField(max_length=500)
    is_multiple = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'polls'

    @property
    def total_votes(self):
        return PollVote.objects.filter(option__poll=self).count()


class PollOption(models.Model):
    poll = models.ForeignKey(
        Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'poll_options'
        ordering = ['order']

    @property
    def votes_count(self):
        return self.votes.count()


class PollVote(models.Model):
    option = models.ForeignKey(
        PollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'poll_votes'
        unique_together = ('option', 'user')
