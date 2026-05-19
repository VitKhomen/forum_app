from rest_framework import serializers

from .models import Poll, PollOption, PollVote


class PollOptionSerializer(serializers.ModelSerializer):
    votes_count = serializers.ReadOnlyField()
    vote_percent = serializers.SerializerMethodField()
    has_voted = serializers.SerializerMethodField()

    class Meta:
        model = PollOption
        fields = ['id', 'text', 'order',
                  'votes_count', 'vote_percent', 'has_voted']

    def get_vote_percent(self, obj):
        total = obj.poll.total_votes
        if not total:
            return 0
        return round(obj.votes_count / total * 100, 1)

    def get_has_voted(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.votes.filter(user=request.user).exists()


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    total_votes = serializers.ReadOnlyField()
    user_voted = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = [
            'id', 'question', 'is_multiple',
            'total_votes', 'options', 'user_voted'
        ]

    def get_user_voted(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
        return list(
            PollVote.objects.filter(option__poll=obj, user=request.user)
            .values_list('option_id', flat=True)
        )


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
