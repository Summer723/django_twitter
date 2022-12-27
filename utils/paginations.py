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
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    def to_html(self):
        pass

    # def paginate_queryset(self, queryset, request, view=None):
    #     if 'created_at__gt' in request.query_params:
    #         created_at__gt = request.query_params["created_at__gt"]
    #         queryset = queryset.filter(created_at__gt=created_at__gt)
    #         self.has_next_page = False
    #         return queryset.order_by('-created_at')
    #
    #     if 'created_at__lt' in request.query_params:
    #         created_at_lt = request.query_params["created_at__lt"]
    #         queryset = queryset.filter(created_at__lt=created_at_lt)
    #
    #     queryset = queryset.order_by("-created_at")[:self.page_size + 1]
    #     self.has_next_page = len(queryset) > self.page_size
    #     return queryset[:self.page_size]
    def paginate_queryset(self, queryset, request, view=None):
        if 'created_at__gt' in request.query_params:
            # created_at__gt 用于下拉刷新的时候加载最新的内容进来
            # 为了简便起见，下拉刷新不做翻页机制，直接加载所有更新的数据
            # 因为如果数据很久没有更新的话，不会采用下拉刷新的方式进行更新，而是重新加载最新的数据
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page = False
            return queryset.order_by('-created_at')

        if 'created_at__lt' in request.query_params:
            # created_at__lt 用于向上滚屏（往下翻页）的时候加载下一页的数据
            # 寻找 created_at < created_at__lt 的 objects 里按照 created_at 倒序的前
            # page_size + 1 个 objects
            # 比如目前的 created_at 列表是 [10, 9, 8, 7 .. 1] 如果 created_at__lt=10
            # page_size = 2 则应该返回 [9, 8, 7]，多返回一个 object 的原因是为了判断是否
            # 还有下一页从而减少一次空加载。
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



