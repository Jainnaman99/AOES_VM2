import mimetypes
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserRole, ApplicationUser
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.views.generic import View
from Onboarding.models import Resource
from TimeEntry.models import Attendance
import datetime
from calendar import monthrange, month_name, monthcalendar
import os
import pandas as pd
from Middlewares.auth import auth_middleware
from django.views.decorators.cache import never_cache

base_dir = settings.BASE_DIR

def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.user.is_authenticated:
        appuser = request.user.appusers
        print()
        if (request.user.is_superuser):
            return redirect('admin_home')
        elif(appuser.roles.filter(name="User").exists()):
            return redirect('user_home')
        # elif(appuser.roles.filter(name="Admin").exists()):
        #     return redirect('reconTAE')
        else:
            return redirect('login')
        
    if request.method == 'POST':
        if (not request.user.is_authenticated):
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if (user is not None):
                login(request, user)
                # it will fetch the corresponding user from the ApplicationUser model
                appuser = user.appusers
                if (appuser.reset == False):
                    return redirect('reset_password')
                if (appuser.roles.filter(name="Admin").exists()):
                    return redirect('admin_home')
                elif (appuser.roles.filter(name="User").exists()):
                    return redirect('user_home')
                else:
                    return HttpResponse('No roles matched')

            else:
                return render(request, 'login.html', {'error_message':'Failed To Authenticate'})
        else:
            return HttpResponse('User Already Authenticated')
    else:
        return render(request, 'login.html')


from django.contrib.auth.views import PasswordResetConfirmView


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        # call the form_valid method of the parent class
        response = super().form_valid(form)
        # update the reset field of the user's ApplicationUser model
        self.user.appusers.reset = True
        self.user.appusers.save()
        return response

@auth_middleware
def register_view(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            user = User.objects.create_user(username=username, password=password)
            user.save()

            if (user is not None):
                appuser = ApplicationUser(user=user)
                role = UserRole.objects.get(name="User")
                print('Roles getting succesfull', role)
                appuser.save()
                appuser.roles.add(role)
                appuser.save()

                login(request, user)
                return HttpResponse("logged in sucessfully")
            else:
                return HttpResponse('failed to authenticate')
        except Exception as e:
            print(e)
            return HttpResponse(e)
    else:
        return render(request, 'register.html')

@auth_middleware
def logout_view(request):
    if (request.user.is_authenticated):
        logout(request=request)
        return redirect('login')
    else:
        return redirect('login')

@auth_middleware
@never_cache
def admin_home(request):
    if (request.user.is_authenticated):

        appuser = request.user.appusers
        data = {
            'role': 'admin'
        }
        if (appuser.roles.filter(name="Admin").exists()):
            data['role'] = 'admin'
        else:
            data['role'] = 'user'
        project_name="All"
        session="reload"
        # mn = datetime.date.today().month
        if request.method == 'POST':
            session="no_reload"
            mn = request.POST.get('month_')
            yr = request.POST.get('year_')
            project_name = request.POST.get('project_name_')
            # print(mn)
            # print(yr)
            # print(project_name)
            print(str(request.POST))
            if ((mn == None) and request.POST.get('monthn') != None):
                mn = request.POST['monthn']
                yr = request.POST['yearn']
                project_name = request.POST['project_namen']
                # print(str(request.POST)+"next")
            elif ((mn == None) and request.POST.get('month') != None):
                mn = request.POST['month']
                yr = request.POST['year']
                project_name = request.POST['project_namep']
                # print(str(request.POST))
            mn = int(mn)
            yr = int(yr)
            # print(request.POST)


            # print(emp_project_name)
            # if 'project-name' not in request.POST:
            #     return redirect('admin_home')
            # elif 'project-name'=='JOSYS':
            #     print("JOSYS")
        else:
            mn = datetime.date.today().month
            yr = datetime.date.today().year
        
        week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekstart = monthrange(yr, mn)[0]
        numdays = monthrange(yr, mn)[1]
        weekdays = [str(month_name[mn])+str(yr)]
        while numdays > 0:
            weekdays.append(week[weekstart])
            weekstart += 1
            if (weekstart > 6):
                weekstart = 0
            numdays -= 1
        weekdays.append(" ")
        numdays = monthrange(yr, mn)[1]
        days = [x for x in range(1, numdays+1)]
        header = []
        header.append("User")
        header.extend(days)
        header.append("Workday")
        # header.append("Project")
        head = []
        
        head.append(weekdays)
        head.append(header)
        # print(head)
        calendar = []
        row = []
        projects=["JOSYS", "SG:SFDF"]
        working_count = 0

        if project_name == "All":
            query = f'select distinct id, EmpCode, Project from Onboarding_resource where Status = "Active" group by EmpCode order by Project ,EmpName'

        else :
            query = f'select distinct id, EmpCode, Project from Onboarding_resource where Status = "Active" and Project ="{project_name}" group by EmpCode order by Project ,EmpName'

        for es in Resource.objects.raw(query):
            for emp in Resource.objects.filter(EmpCode=es.EmpCode):
                row.append(emp.EmpName)
            for dt in Attendance.objects.raw(f'select id, Date, Status from TimeEntry_attendance where EmpCode = {es.EmpCode} and Date like "%{mn}-{yr}%" order by strftime(date,Date) asc'):
                row.append(dt.Status)
                if (dt.Status == "W" or dt.Status == "C"):
                    working_count += 1
                elif (dt.Status == "HL"):
                    working_count += 0.5
            if (working_count > 20):
                working_count = 20
            if (len(row) == 1):
                for i in range(0, numdays):
                    row.append('-')
            row.append(working_count)
            # for emp_project in Resource.objects.filter(EmpCode=es.EmpCode):
                # print(emp_project.Project)
                # if emp_project.Project not in projects:
                #     projects.append(emp_project.Project)
                # row.append(emp_project.Project)
            calendar.append(row)
            row = []
            working_count = 0
        # print(projects)
        array = []
        array.append(head[0])
        array.append(head[1])
        array.extend(calendar)
        # print(array)

        # Generating Excel
        filepath = str(base_dir)+'/media/'
        result = pd.DataFrame(array)
        result.to_excel(filepath+'TimeReport.xlsx', index=False, header=False)
        downloadFile = filepath+'TimeReport.xlsx'

        return render(request, 'admin_home.html', {'role': data['role'], 'header': head, 'month_name': month_name[mn], 'mn': mn, 'yr': yr, 'calendar': calendar, 'df': downloadFile, 'projects':projects, 'session':session})
    else:
        return redirect('login')

@auth_middleware
def user_home(request):

    if (request.user.is_authenticated):
        if(request.user.appusers.reset == False):
            return redirect("reset_password")
        appuser = request.user.appusers
        # print((appuser.user.value))
        print(appuser)
        # # app_code = appuser.user.value
        app_code = (request.user.username)
        print(app_code)
        for emp in Resource.objects.filter(EmpCode = (app_code)):
            emp_name = emp.EmpName
        # print(name_emp)
        data = {
            'role': 'admin',
            'reset': appuser.reset,
            'person':emp_name
        }
        if (appuser.roles.filter(name="Admin").exists()):
            data['role'] = 'admin'
        else:
            data['role'] = 'user'
        return render(request, 'user_home.html', {'role': data['role'], 'reset': data['reset'], 'person':emp_name})
    else:
        return redirect('login')


class ResetPasswordView(View):  
    def get(self, request):
        form = PasswordChangeForm(request.user)
        if (request.user.appusers.reset == True):
            return redirect('user_home')
        else:
            return render(request, 'reset_password.html', {'form': form})
        
    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password2')
            print(new_password)
            if new_password != 'Per@1234':
                print("Inside if")
                user = form.save()
                if (request.user.appusers.reset == False):
                    request.user.appusers.reset = True
                    request.user.appusers.save()
                    request.user.save()
                update_session_auth_hash(request, user)  # Important!
                return redirect('/logout')
            else:
                form.errors['password1'] = form.error_class(["Password cannot be default"])
        else:
            print(form.errors)
            
        return render(request, 'reset_password.html', {'form': form})
@auth_middleware        
def downloadTR(request):
    filename = 'TimeReport.xlsx'
    file_path = settings.MEDIA_ROOT+'/'+filename

    fl = open(file_path,'rb')
    mime_type, _ = mimetypes.guess_type(file_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['X-Sendfile'] = file_path
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    os.remove(file_path)
    return response

@auth_middleware
def calendarEdit(request):
    if(request.user.is_authenticated):
        appuser = request.user.appusers
        if (appuser.roles.filter(name="Admin").exists()):
            role = 'admin'
        else:
            role = 'user'
    emplist_code = []
    emplist_name = []
    employees_final_list = []
    for es in Resource.objects.raw(f'select distinct id, EmpCode from Onboarding_resource where Status = "Active" group by EmpCode order by EmpName'):
        for emp in Resource.objects.filter(EmpCode = es.EmpCode):
            emplist_name.append(emp.EmpName)
            emplist_code.append(emp.EmpCode)
            employees_final_list.append(str(emp.EmpName) +"-"+ str(emp.EmpCode))
    
    # print(emplist_name)
    # print(emplist_code)
    # print(employees_final_list)
    if(request.method == 'POST'):
        if 'empid'not in request.POST:
            return redirect('admincalendar')
        else:
            emp = request.POST['empid']
            new_emp = emp.split("-")
            # print(new_emp)
            emp1 = int(new_emp[1])
            month = int(request.POST['month'])
            year = int(request.POST['year'])
            # print(request.POST.get('calendar_save'))
            ls = []
            cal = monthcalendar(year, month)

            for e in Attendance.objects.raw(f"select id, Status from TimeEntry_attendance where EmpCode={emp1} and Date like '%{month}-{year}%'"):
                ls.append(e.Status)
            
            return render(request,'admincalendar.html',{
                'ls':ls,
                'cal':cal,
                'role':role,
                'empid': emp1,
                'month': month,
                'year': year,
                'ename':emplist_name,
                'ecode':emplist_code,
                'empfinal':employees_final_list,
                'emp':emp
            })
    return render(request, 'admincalendar.html', {'role': role,'ename':emplist_name,'ecode':emplist_code,'empfinal':employees_final_list})

@auth_middleware
def saveEmpCalendar(request):
    res = request.POST
    user = request.POST['empidsave']
    month = request.POST['monthsave']
    year = request.POST['yearsave']
    for key, status in res.items():
            if(key not in ['csrfmiddlewaretoken', 'empidsave', 'monthsave', 'yearsave']):
                attendance = Attendance()
                date = f'{key}-{month}-{year}'
                if not Attendance.objects.filter(EmpCode = user, Date = date).exists():
                    attendance.EmpCode = str(user)
                    attendance.Date = date
                    attendance.Status = status
                    attendance.save()
                else:
                    rec = Attendance.objects.filter(EmpCode = user, Date = date).first()
                    rec.Status = status
                    rec.save()
    return render(request, 'admincalendar.html', {'role': 'admin'})
