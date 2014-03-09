from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'source_dot_code.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^uploads/', include('uploads.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
