from __future__ import unicode_literals

from django.conf import settings
from django.urls import reverse_lazy
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.authtoken import views

from core.views import (
    RecordEventView,
    ListCampaignEventsView,
    send_test_notification,
    CampaignEventViewSet,
    DashboardView
)
from users.views import UserViewSet, RegisterUserView, UserInfoView
from core.views import CampaignViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'campaigns', CampaignViewSet)

campaign_events_router = SimpleRouter()
campaign_events_router.register(r'events', CampaignEventViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^api/v1/', include('authentication.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/record-event/(?P<campaign>[-\w]+)/(?P<event_id>[-\w]+)/$', RecordEventView.as_view()),
    url(r'^api/v1/events/(?P<campaign>[-\w]+)/$', ListCampaignEventsView.as_view()),
    url(r'^api/v1/campaigns/(?P<campaign>[-\w]+)/', include(campaign_events_router.urls)),
    url(r'^api/v1/dashboard/$', DashboardView.as_view()),

    url(r'^api/v1/register/$', RegisterUserView.as_view()),
    url(r'^api/v1/login/$', views.obtain_auth_token),
    url(r'^api/v1/userinfo/$', UserInfoView.as_view()),

    url(r'^send-test-notification/(?P<recorded_event_token_id>\d+)/$', send_test_notification, name='send-test-notification'),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    url(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
