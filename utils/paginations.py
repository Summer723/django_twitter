from rest_framework.pagination import PageNumberPagination,BasePagination
from rest_framework.response import Response

class MyPagination(PageNumberPagination):
    # how many items on a page
    page_size = 20
    # set page_size as a parameter
    page_size_query_param = 'page_size'
    # the maximum entries on a page
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })

class EndlessPagination(BasePagination):

    page_size = 20
    def __int__(self):
        super().__init__()
        self.has_next_page = False

    def to_html(self):
        pass


    def paginate_queryset(self, queryset, request, view=None):
        if 'created_at__gt' in request.query_params:
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page = False
            return queryset.order_by('-created_at')

        if 'created_at__lt' in request.query_params:
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        self.has_next_page = len(queryset) > self.page_size
        return queryset[:self.page_size]

    def get_paginated_response(self, data):
        return Response({
            'results': data,
            "has_next_page": self.has_next_page,
        })



