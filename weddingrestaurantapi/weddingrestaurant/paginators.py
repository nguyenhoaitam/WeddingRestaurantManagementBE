from rest_framework.response import Response
from rest_framework import pagination


class BasePaginator(pagination.PageNumberPagination):
    page_size = 5

    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


class HallPaginator(pagination.PageNumberPagination):
    page_size = 4

    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


class FoodDrinkServicePaginator(pagination.PageNumberPagination):
    page_size = 6

    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })