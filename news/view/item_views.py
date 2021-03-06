from rest_framework import status, serializers
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from news.serializers import ItemSerializer
from news.service.item_services import get_item, get_last_items_by_user, get_status_by_user_item, get_item_query, \
    get_item_similarity, get_item_search, get_item_recommend, get_summary, get_item_saved
from news.service.keyword_services import get_item_keywords


class ItemList(APIView):
    serializer_class = ItemSerializer
    pagination_class = PageNumberPagination()

    def get(self, request):
        items = get_last_items_by_user(request.user.id)

        follow = request.GET.get('follow', None)
        if follow is not None:
            for item_id in request.session.get('news_ids', []):
                get_status_by_user_item(request.user.id, item_id).as_view()
        request.session['news_ids'] = [x.id for x in items]

        page = self.pagination_class.paginate_queryset(items, request)
        serializer = self.serializer_class(page, many=True, context={'request': self.request})
        return self.pagination_class.get_paginated_response(serializer.data)


class ItemDetail(APIView):
    @staticmethod
    def get(request, item_id):
        item = get_item(item_id)
        get_status_by_user_item(request.user.id, item_id).as_read()
        serializer = ItemSerializer(item, context={'request': request})
        return Response(serializer.data)

    @staticmethod
    def put(request, item_id):
        item_status = get_status_by_user_item(request.user.id, item_id)

        like = request.data.get('like', None)
        if like is not None:
            if like:
                item_status.as_like()
            else:
                item_status.as_unlike()

        save = request.data.get('saves', None)
        if save is not None:
            if save:
                item_status.as_save()
            else:
                item_status.as_unsave()

        web = request.data.get('web', None)
        if web:
            item_status.as_web()

        return Response(status=status.HTTP_201_CREATED)


class ItemQuery(APIView):
    serializer_class = ItemSerializer
    pagination_class = PageNumberPagination()

    def get(self, request, query):
        items = get_item_query(query, request.user.profile.id)

        page = self.pagination_class.paginate_queryset(items, request)
        serializer = self.serializer_class(page, many=True, context={'request': self.request})
        return self.pagination_class.get_paginated_response(serializer.data)


class ItemRecommend(ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return get_item_recommend(self.request.user.profile.id)


class ItemSimilarity(ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        limit = 3
        return get_item_similarity(self.kwargs['item_id'], limit, self.request.user.id)


class ItemKeywords(APIView):
    @staticmethod
    def get(request, item_id):
        links = get_item_keywords(item_id)
        return Response(links)


class ItemSummary(APIView):
    def get(self, request):
        days = int(self.request.query_params.get('days', 1))
        hours = int(self.request.query_params.get('hours', 0))

        summary = get_summary(request.user.id, days, hours)
        return Response(summary)


class ItemSaved(ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return get_item_saved(self.request.user.id)


class ItemSearch(ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        limit = 24
        query = self.request.query_params.get('query', None)

        if query:
            cleaned_data = query
        else:
            params = ['title', 'creator', 'article']
            cleaned_data = {param: self.request.query_params.get(param, '') for param in params
                            if param in self.request.query_params and self.request.query_params.get(param, '') != ''}

        return get_item_search(cleaned_data, limit, self.request.user.id)
