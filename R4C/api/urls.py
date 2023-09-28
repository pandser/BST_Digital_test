from django.urls import include, path

from api.views import RobotView


app_name = 'api'

urlpatterns = [
    path('robot_create/', RobotView.as_view(), name='robot_create')
]
