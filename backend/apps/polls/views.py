from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Poll, PollOption, PollVote
from .serializers import PollSerializer, PollCreateSerializer
from apps.main.models import Post


class PollCreateView(generics.CreateAPIView):
    serializer_class = PollCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.request.data.get('post_id')
        post = None

        if post_id:
            post = get_object_or_404(
                Post, id=post_id, author=self.request.user)
            Poll.objects.filter(post=post).delete()

        poll = serializer.save(post=post)
        return poll

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        poll = self.perform_create(serializer)
        return Response(
            PollSerializer(poll, context={'request': request}).data,
            status=201
        )


class PollVoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, poll_id):
        poll = get_object_or_404(Poll, id=poll_id)

        option_ids = request.data.get('option_ids', [])
        if not option_ids:
            return Response({'error': 'Вкажіть варіант'}, status=400)

        if not poll.is_multiple and len(option_ids) > 1:
            return Response({'error': 'Оберіть лише один варіант'}, status=400)

        options = PollOption.objects.filter(id__in=option_ids, poll=poll)
        if options.count() != len(option_ids):
            return Response({'error': 'Невірний варіант'}, status=400)

        PollVote.objects.filter(option__poll=poll, user=request.user).delete()
        PollVote.objects.bulk_create([
            PollVote(option=option, user=request.user)
            for option in options
        ])

        return Response(PollSerializer(poll, context={'request': request}).data)

    def delete(self, request, poll_id):
        poll = get_object_or_404(Poll, id=poll_id)
        PollVote.objects.filter(option__poll=poll, user=request.user).delete()
        return Response(PollSerializer(poll, context={'request': request}).data)
