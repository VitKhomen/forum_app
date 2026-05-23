from rest_framework import serializers
from .models import Poll, PollOption, PollVote


class PollOptionSerializer(serializers.ModelSerializer):
    votes_count = serializers.SerializerMethodField()
    vote_percent = serializers.SerializerMethodField()

    class Meta:
        model = PollOption
        fields = ['id', 'text', 'votes_count', 'vote_percent']

    def get_votes_count(self, obj):
        return obj.votes.count()

    def get_vote_percent(self, obj):
        total = obj.poll.total_votes()
        if total == 0:
            return 0
        return round((obj.votes.count() / total) * 100, 1)


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    user_voted = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ['id', 'question', 'is_multiple',
                  'options', 'user_voted', 'total_votes']

    def get_user_voted(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []

        return list(PollVote.objects.filter(
            option__poll=obj,
            user=request.user
        ).values_list('option_id', flat=True))

    def get_total_votes(self, obj):
        return obj.total_votes()


class PollCreateSerializer(serializers.ModelSerializer):
    options = serializers.ListField(
        child=serializers.CharField(max_length=200),
        min_length=2,
        max_length=10
    )

    class Meta:
        model = Poll
        fields = ['question', 'is_multiple', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data)

        PollOption.objects.bulk_create([
            PollOption(poll=poll, text=text.strip(), order=i)
            for i, text in enumerate(options_data)
        ])
        return poll
