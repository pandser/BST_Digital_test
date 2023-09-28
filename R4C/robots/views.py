import openpyxl
import datetime

from django.db.models import Count
from django.http import FileResponse

from robots.models import Robot

def weekly_report(request):
    robots = Robot.objects.values_list('model', 'version').annotate(
        total=Count('version')
        ).filter(
            created__range=(datetime.date.today() - datetime.timedelta(days=7),
            datetime.date.today())
            )
    wb = openpyxl.Workbook()
    sheet = None
    count = 0
    for robot in robots:
        if sheet != robot[0]:
            list = wb.create_sheet(robot[0], count)
            sheet = robot[0]
            count += 1
            list.append(('Модель', 'Версия', 'Количество за неделю'))
        list.append(robot)
    wb.save('weekly_report.xlsx')
    return FileResponse(open('weekly_report.xlsx', 'rb'))
