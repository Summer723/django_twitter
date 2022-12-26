from rest_framework.pagination import PageNumberPagination
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