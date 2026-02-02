from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReedViewSet, UsageSessionViewSet, QualitySnapshotViewSet, 
    ModificationViewSet, ThreadViewSet, StapleViewSet
)

router = DefaultRouter()
router.register(r'reeds', ReedViewSet, basename='reed')
router.register(r'usage-sessions', UsageSessionViewSet, basename='usagesession')
router.register(r'quality-snapshots', QualitySnapshotViewSet, basename='qualitysnapshot')
router.register(r'modifications', ModificationViewSet, basename='modification')
router.register(r'threads', ThreadViewSet, basename='thread')
router.register(r'staples', StapleViewSet, basename='staple')

urlpatterns = [
    path('', include(router.urls)),
]
