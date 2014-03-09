from django.conf.urls import patterns, url

from uploads import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^mkacct$', views.mkacct, name='mkacct'),
    url(r'^login$',  views.login,  name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^about$', views.about, name='about'),
    url(r'^submit$', views.submit, name='submit'),
    url(r'^compile_code$', views.compile_code, name='compile_code'),
    url(r'^users/(?P<username>\w+)/edit$', views.edituser, name='edituser'),
    url(r'^users/(?P<username>\w+)/$', views.showuser, name='showuser'),
    url(r'^paste/(?P<hash_id>\w+)/$', views.viewpaste, name='viewpaste'),
    url(r'^paste/(?P<hash_id>\w+)/fork$', views.forkpaste, name='forkpaste'),
    url(r'^paste/(?P<hash_id>\w+)/raw$', views.rawpaste, name='rawpaste'),
)
