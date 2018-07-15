from django.urls import path
#from django.contrib import admin

from app.views import IndexView as AppView

urlpatterns = [
    path('unit/', AppView.as_view()),
    #path('admin/', admin.site.urls),
]
