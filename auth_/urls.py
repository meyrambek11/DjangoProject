from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from .views import auth, UserRegisterView, SellerRegisterView, ProfileUpdate
urlpatterns = [
    path('', obtain_jwt_token),
    path('token', auth),
    # register simple user
    path('signup/', UserRegisterView.as_view()),
    # register seller
    path('create_shop/', SellerRegisterView.as_view()),
    path('update_profile/', ProfileUpdate.as_view({'put': 'put', 'delete': 'delete'})),

]
