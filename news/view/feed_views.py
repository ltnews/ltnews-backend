from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from news.serializer.serializers import FeedSerializer, FeedFormSerializer
from news.service.feed_services import get_feed, all_feeds_link, delete_feed, get_feeds_by_user


class FeedList(APIView):
    @staticmethod
    def get(request):
        feeds = get_feeds_by_user(request.user.id)
        return Response(FeedSerializer(feeds, many=True).data)

    @staticmethod
    def post(request):
        request.data['user_id'] = request.user.id
        serializer = FeedFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedDetail(APIView):
    @staticmethod
    def get(request, feed_id):
        feed = get_feed(feed_id, request.user)
        serializer = FeedSerializer(feed)
        return Response(serializer.data)

    @staticmethod
    def delete(request, feed_id):
        delete_feed(feed_id, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FeedMoreDetail(APIView):
    @staticmethod
    def get(request):
        links = all_feeds_link(request.user.id)
        return Response(links)