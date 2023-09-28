import datetime
import json

from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from robots.models import Robot
from orders.models import Order


@method_decorator(csrf_exempt, name='dispatch')
class RobotView(View):
    
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        valid_result = self.validate(data=data)
        if not valid_result[0]:
            return JsonResponse(data=valid_result[1], status=400)
        Robot.objects.create(**{
            'serial': f'{data.get("model")}-{data.get("version")}',
            'model': data.get('model'),
            'version': data.get('version'),
            'created': data.get('created'),
        })
        data = {
            'message': 'Робот добавлен в базу данных'
        }
        return JsonResponse(data=data, status=201)

    
    def validate(self, data):
        if (not data.get('model') 
            or not data.get('version') 
            or not data.get('created')):
            return (False, {
                'message': 'Отсутствует одно из обязательных полей model, version, created.'
            })
        if (len(data.get('model')) != 2
            or len(data.get('version')) != 2):
            return (False, {
                'message': 'Значение полей model и version должно быть равно двум символам.'
            })
        try:
            date = datetime.datetime.fromisoformat(data.get('created'))
            if date > datetime.datetime.now():
                return (False, {
                    'message': 'Дата не может быть больше текущей'
                })
        except ValueError as err:
            return (False, {
                'message': 'Дата должна быть в формате YYYY-MM-dd HH:mm:ss'
            })
        return (True, data)
    

@receiver(post_save, sender=Robot)
def message_sender(sender, instance, **kwargs):
    order = Order.objects.get(robot_serial=instance.serial)
    if order:
        send_mail(
            subject='Робот в наличии',
            message=(f'Добрый день!\n'
                f'Недавно вы интересовались нашим роботом модели '
                f'{instance.model}, версии {instance.version}.\n' 
                f'Этот робот теперь в наличии. Если вам подходит этот вариант'
                f' - пожалуйста, свяжитесь с нами.\n'),
            from_email='test@example.com',
            recipient_list=[order.customer.email],
        )
