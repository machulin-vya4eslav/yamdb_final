from rest_framework import routers
from django.urls import include, path

from .views import (
    CategoryViewsSet,
    GenreViewsSet,
    TitleViewsSet,
    CommentViewSet,
    ReviewViewSet,
    UserViewSet,
    SignupView,
    TokenView
)


app_name = 'reviews'

v1_router = routers.DefaultRouter()
v1_router.register(r'categories', CategoryViewsSet)
v1_router.register(r'genres', GenreViewsSet)
v1_router.register(r'titles', TitleViewsSet, basename='titles')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
    r'/comments',
    CommentViewSet,
    basename='comments'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register('users', UserViewSet, basename='users')

register_url_patterns = [
    path('auth/signup/', SignupView.as_view()),
    path('auth/token/', TokenView.as_view()),
]

urlpatterns = [
    path('v1/', include(register_url_patterns)),
    path('v1/', include(v1_router.urls)),
]
