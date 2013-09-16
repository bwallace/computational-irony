from django.conf.urls import patterns, include, url

from irony import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'annotatr.views.home', name='home'),
    # url(r'^annotatr/', include('annotatr.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    # ex: /irony/5/
    url(r'^(?P<comment_id>\d+)/$', views.show_comment, name='show_comment'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'})
)
