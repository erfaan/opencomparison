from django.conf.urls.defaults import *

from searchv2 import views

urlpatterns = patterns("",

    url(
        regex   = '^build$',
        view    = views.build_search,
        name    = 'build_search',
    ),    

)