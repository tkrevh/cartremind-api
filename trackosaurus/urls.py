from __future__ import unicode_literals

from django.conf import settings
from django.urls import reverse_lazy
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from core.views import RecordEventView, ListCampaignEventsView, send_test_notification
from users.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^api/v1/', include('authentication.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/record-event/(?P<campaign>[-\w]+)/(?P<code>[-\w]+)/$', RecordEventView.as_view()),
    url(r'^api/v1/events/(?P<campaign>[-\w]+)/$', ListCampaignEventsView.as_view()),
    url(r'^send-test-notification/(?P<recorded_event_id>\d+)/$', send_test_notification, name='send-test-notification'),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    url(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
