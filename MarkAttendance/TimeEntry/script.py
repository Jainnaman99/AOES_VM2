import datetime

today = datetime.date.today()
year = today.year
month = today.month
today.weekday()

import calendar
print(calendar.monthcalendar(year,month))
# print(calendar.month(year, month)) #Best for calendar representation in shell.

today = datetime.date.today()
year = today.year
month= today.month
num_days = calendar.monthrange(year, month)[1]
days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
print(days)
days_list = []
for days in days:
    days_str = days.strftime('%d')
    days_list.append(days_str)

