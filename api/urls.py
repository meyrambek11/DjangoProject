from django.urls import path
from rest_framework import routers

from .views import ProductViewSet, CommentView, Orders, ProfileBasket, CategoryView, category_products

router = routers.SimpleRouter()
router.register('products', ProductViewSet)
router.register('my_orders', Orders)
router.register('my_basket', ProfileBasket)
urlpatterns = [
    path('product/<int:pk>/comments', CommentView.as_view()),
    path('category/', CategoryView.as_view()),
    path('category/<int:pk>/', category_products),
]
urlpatterns += router.urls
