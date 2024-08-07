from django.urls import path
from .views import UserSignUpView, UserSearchView, UserLoginView

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='user-signup'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('login/', UserLoginView.as_view(), name='user-login'),
]