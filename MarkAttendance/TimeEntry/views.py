from django.shortcuts import redirect, render
from calendar import monthcalendar

from Middlewares.auth import auth_middleware
from .models import Attendance
from Onboarding.models import Resource
from django.utils.decorators import method_decorator
# import json

# Create your views here.

# @method_decorator(auth_middleware)
def calendar(request, year, month):
 if request.user.is_authenticated:
    if (month>12): month = 12
    cal = monthcalendar(year, month)
    user = request.user
    person = Resource.objects.filter(EmpCode = str(user))
    person = str(person[0]).split()[0]
    ls = []
    att = Attendance.objects.filter(EmpCode = user)
    for i in att:
        dt = i.Date
        dt = dt.split('-')
        if (dt[1] == str(month) and dt[2] == str(year)):
            print(i.Status)
            ls.append(i.Status)

    # lst = json.dumps(ls)

    
    if request.method == 'POST':
        
        res = request.POST
        print(res)
        for key, status in res.items():
            if(key != 'csrfmiddlewaretoken'):
                attendance = Attendance()
                date = f'{key}-{month}-{year}'
                print(date, status)
                if not Attendance.objects.filter(EmpCode = user, Date = date).exists():
                    attendance.EmpCode = str(user)
                    attendance.Date = date
                    attendance.Status = status
                    attendance.save()
                else:
                    rec = Attendance.objects.filter(EmpCode = user, Date = date).first()
                    rec.Status = status
                    rec.save()
 else:
    return redirect('login')       
 return render(request, "calendar.html" , {'cal':cal, 'year':year, 'month':month, 'lst':ls, 'person':person, 'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin"})

def summary(request):
    user = request.user
    att = Attendance.objects.filter(EmpCode = user)
    sum = 0
    for a in att:
        if a.Status == "W":
            sum+=1
        if a.Status == "HL":
            sum+=0.5
    
    cons = str(sum) + ' / ' + str(len(att))

    return render(request, 'summary.html', {'att': att, 'sum':cons})
