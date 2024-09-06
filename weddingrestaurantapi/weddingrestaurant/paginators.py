from rest_framework import pagination


class BasePaginator(pagination.PageNumberPagination):
    page_size = 5


class HallPaginator(pagination.PageNumberPagination):
    page_size = 4


class FoodDrinkServicePaginator(pagination.PageNumberPagination):
    page_size = 6
