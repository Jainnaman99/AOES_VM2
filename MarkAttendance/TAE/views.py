from math import floor

import pandas as pd
import glob
import mimetypes
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages

from Middlewares.auth import auth_middleware
from .models import TAESheet, MasterTAE
from .forms import TAEUploadForm
from Onboarding.models import Resource
from TimeEntry.models import Attendance
from django.views.decorators.cache import cache_control
from .forms import TAEUploadMultiForm
from django.template.defaulttags import register
from django.views.decorators.cache import never_cache
from django.db import connection
from openpyxl import load_workbook

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

base_dir = settings.BASE_DIR
# Create your views here.
@auth_middleware
def TAEUpload(request):
    if request.method == "POST":
        form = TAEUploadForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = TAESheet(docfile = request.FILES['docfile'])
            newdoc.save()
            messages.success(request, "File upload Success")
    else:
        form = TAEUploadForm()
        
    return render(request, 'TAEupload.html', {'form' : form,'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin"})

@auth_middleware
def upload_multiple(request):

    if request.method == "POST":
        try:
            form = TAEUploadMultiForm(request.POST, request.FILES)
            docfiles = request.FILES.getlist('docfile')
            # print(docfiles)
            if form.is_valid():
                # print(docfiles)
                for f in docfiles:
                    # f.protection.disable()
                    newdoc = TAESheet(docfile=f)

                    # print("ok here")
                    if not f.name.endswith('xlsx'):
                        print("inside EXCELDATA ends with xlsx")
                        return render(request, 'MultiTAE.html', {'isValid': False, 'role': "user" if (request.user.appusers.roles.filter(name="User").exists()) else "admin"})
                    # else:
                    
                    newdoc.save()
                # context = {'msg' : '<span style="color: green;">File successfully uploaded</span>'}
                # return render(request, "MultiTAE.html", context)
    # =====================================================================================================
                path = str(base_dir) + "/media/documents/TAE"
                file_list = glob.glob(path+"/*.xlsx")
                

                excl_list = []
                # print(file_list)
                for file in file_list:
                    # print("ok")
                    excl_list.append(pd.read_excel(file))
                    # print("ok")

                # excl_merged = pd.DataFrame()

                # for excl_file in excl_list:
                #     excl_merged = excl_merged.append(excl_file, ignore_index=True)
                # print(excl_list)
                excl_merged = pd.concat(excl_list, ignore_index=True)
                

                excl_merged.to_excel(
                    str(base_dir)+"/media/TAE_Merged.xlsx", index=False)
                masterTAE = open(str(base_dir)+"/media/TAE_Merged.xlsx", 'rb')
                empexceldata = pd.read_excel(masterTAE)
                dbframe = empexceldata

                for dbframe in dbframe.itertuples():
                    # print(dbframe)
                    # if MasterTAE.objects.filter(User_Name=dbframe._1, Date=dbframe.Date):
                    #     if MasterTAE.objects.filter(User_Name=dbframe._1, Date=dbframe.Date, Activity=dbframe.Activity):
                    #         obj = MasterTAE.objects.filter(User_Name=dbframe._1, Date=dbframe.Date)
                    #     # print(obj)
                    #     # print("Deleted !")
                    #         obj.delete()
                        

                    if not MasterTAE.objects.filter(User_Name=dbframe._1, Date=dbframe.Date, Activity=dbframe.Activity):
                        obj = MasterTAE.objects.create(User_Name=dbframe._1, Location=dbframe.Location, Date=dbframe.Date,
                                                        Project=dbframe.Project, Project_Task=dbframe._5, Activity=dbframe.Activity,
                                                        Role=dbframe.Role, Internal_Note=dbframe._8, Bill_Rate=dbframe._9, Bill_Hrs=dbframe._10,
                                                        NB_Hrs=dbframe._11, Total_Hrs=dbframe._12, Revenue_Reason=dbframe._13)
                        # print("Saved !")
                        obj.save()
                    # if MasterTAE.objects.filter(User_Name=dbframe._1, Date=dbframe.Date, Activity=dbframe.Activity):
                    #     obj = MasterTAE.objects.filter(User_Name=dbframe._1, Location=dbframe.Location, Activity=dbframe.Activity)
                    #     # print(obj)
                    #     obj.delete()
                        # print("Deleted!")
                        # if MasterTAE.objects.filter(User_Name=dbframe._1, Date=dbframe.Date):
                            # obj=MasterTAE.objects.filter(User_Name=dbframe._1, Date=dbframe.Date)
                            # print(obj)
                            # obj = MasterTAE.objects.get(User_Name=dbframe._1, Location=dbframe.Location, Date=dbframe.Date,
                            #                             Project=dbframe.Project, Project_Task=dbframe._5, Activity=dbframe.Activity,
                            #                             Role=dbframe.Role, Internal_Note=dbframe._8, Bill_Rate=dbframe._9, Bill_Hrs=dbframe._10,
                            #                             NB_Hrs=dbframe._11, Total_Hrs=dbframe._12, Revenue_Reason=dbframe._13)
                            # obj.delete()

                        # else:
                        #     obj = MasterTAE.objects.create(User_Name=dbframe._1, Location=dbframe.Location, Date=dbframe.Date,
                        #                                 Project=dbframe.Project, Project_Task=dbframe._5, Activity=dbframe.Activity,
                        #                                 Role=dbframe.Role, Internal_Note=dbframe._8, Bill_Rate=dbframe._9, Bill_Hrs=dbframe._10,
                        #                                 NB_Hrs=dbframe._11, Total_Hrs=dbframe._12, Revenue_Reason=dbframe._13)
                        #     obj.save()

                downloadfile = str(base_dir)+"/media/TAE_Merged.xlsx"

                # deleting residue files

                files = TAESheet.objects.all()
                for file in files:
                    file.docfile.delete()
                    file.delete()
    # ======================================================================================================
                return render(request, "download_merged.html", {'file': downloadfile, 'role': "user" if (request.user.appusers.roles.filter(name="User").exists()) else "admin"})
            else:
                return render(request, 'MultiTAE.html', {'isValid': False, 'role': "user" if (request.user.appusers.roles.filter(name="User").exists()) else "admin"})
        except Exception as e :
            print("In except block",e)
            files = TAESheet.objects.all()
            for file in files:
                file.docfile.delete()
                file.delete()
            # template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            # print(template.format(type(e).__name__, e.args))
            return render(request, 'MultiTAE.html', {'isValid': False, 'role': "user" if (request.user.appusers.roles.filter(name="User").exists()) else "admin"})

    else:
        form = TAEUploadMultiForm()
    return render(request, 'MultiTAE.html', {'form': form, 'role': "user" if (request.user.appusers.roles.filter(name="User").exists()) else "admin"})

@auth_middleware
@never_cache
def deleteTAE(request):
    # files = TAESheet.objects.all()
    # for file in files:
    #     file.docfile.delete()
    #     file.delete()

    # return HttpResponse("Files removed successfully")
    if (request.user.is_authenticated):
        appuser = request.user.appusers
        if (appuser.roles.filter(name="Admin").exists()):
            role = 'admin'
        else:
            role = 'user'
    emplist_code = []
    emplist_name = []
    employees_final_list = []
    for es in Resource.objects.raw(f'select distinct id, EmpCode from Onboarding_resource where Status = "Active" group by EmpCode order by EmpName'):
        for emp in Resource.objects.filter(EmpCode=es.EmpCode):
            emplist_name.append(emp.EmpName)
            emplist_code.append(emp.EmpCode)
            employees_final_list.append(
                str(emp.EmpName) + "-" + str(emp.EmpCode))

    # print(emplist_name)
    # print(emplist_code)
    # print(employees_final_list)
    if (request.method == 'POST'):
        if 'empid'not in request.POST:
            return redirect('delete_TAE')
        else:
            emp = request.POST['empid']
            new_emp = emp.split("-")
            # print(new_emp)
            emp1 = (new_emp[0])
            month = str(request.POST['month'])
            month = month.zfill(2)
            year = int(request.POST['year'])
            print(emp1,month,year)
            # print(request.POST.get('calendar_save'))
            try:
                # selection = MasterTAE.objects.raw(f"select * from TAE_mastertae where User_Name='{emp1}' and Date like '%{year}-{month}%'")
                # print(selection)
                with connection.cursor() as cursor:
                    cursor.execute(f"delete from TAE_mastertae where User_Name='{emp1}' and Date like '%{year}-{month}%'")
                    print("deleted")
                    # if(e != None):
                    #     obj=MasterTAE.objects.filter(e)
                    #     obj.delete()
                    # else:
                    #     print("No more TAE entries")
                    
                # MasterTAE.objects.filter(User_Name=emp1, Date like )
                # print(count)
                return render(request, 'delete_TAE.html', {'role': role, 'month': month, 'year': year, 'emp': emp, 'ename': emplist_name, 'ecode': emplist_code, 'empfinal': employees_final_list})
            except:
                print("In Except Block")
                return render(request, 'delete_TAE.html', {'role': role,  'month': month, 'year': year, 'emp': emp, 'ename': emplist_name, 'ecode': emplist_code, 'empfinal': employees_final_list})
                
    return render(request, 'delete_TAE.html', {'role': role, 'ename': emplist_name, 'ecode': emplist_code, 'empfinal': employees_final_list})



def downloadTAE(request):
    filename = 'TAE_Merged.xlsx'
    file_path = settings.MEDIA_ROOT+'/'+filename

    fl = open(file_path,'rb')
    mime_type, _ = mimetypes.guess_type(file_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['X-Sendfile'] = file_path
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


@auth_middleware
def summaryTAE(request):
    ls = {}
    for sql in MasterTAE.objects.raw(
            "select distinct id, User_Name, sum(Total_Hrs) as Total_Sum from TAE_mastertae group by 2"):
        ls[sql.User_Name] = sql.Total_Sum if sql.Total_Sum < 160 else 160

    return render(request, "summaryTAE.html",
                  {'ls': ls, 'role': "user" if (request.user.appusers.roles.filter(name="User").exists()) else "admin"})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reconTAE(request, year, month):
    if request.user.is_authenticated:
        res = Resource.objects.distinct()

        yr = str(year)
        selected_activities = []
        if month < 10:
            mn = "0"+str(month)
        else:
            mn = str(month)
        activities_set = MasterTAE.objects.values_list('Activity').distinct()
        activities = list(activities_set)
        activities.sort()
        # print(activities)

        my_activities = []
        # print('my print: ',activities)
        for i in activities:
            my_activities.append(i[0])
        # my_activities.remove("Holiday")
        # my_activities.remove("Leave")
        # my_activities.remove("Leave of Absence")
        # my_activities.remove("Sick")
        if request.method == 'POST':
            # print(str(request.POST))
            for i in request.POST.getlist('activities'):
                selected_activities.append(i)
            # print(len(selected_activities))
                # print(type(i))
        # for _ in activities:
        #     print(type(_))
        # out_list = []
        # out_list = [re.sub('[^a-zA-Z0-9]+','', _) for _ in my_activities]
        # print(out_list)
        # l = ['(',')',',',"'"]
        # out_list = []
        # for x in activities:
        #     for y in l:
        #         if y in x:
        #             x = x.replace(y,'')
        #             out_list.append(x)
        #             print(out_list)
        #             break
        
        # print(activities)
        # print(len(activities))
        # print(activities)
        reatt_working = {}
        reatt_leaves = {}
        retae_working = {}
        retae_leaves = {}
        reatt = {}
        retae = {}
        total_hrs = 0
        # print(len(selected_activities))
        # query_list = 'activity = '+selected_activities[]
        # for i in range(1, len(selected_activities)):
        #     query_list += ' or activity = '+selected_activities[i]
        # print(query_list)
        # for tae in MasterTAE.objects.raw(
        #     f'select distinct id, User_Name, sum(Total_Hrs) as Total_Sum from TAE_mastertae where activity = "{i}" and Date like "{yr}-{mn}%" group by 2'):
        #     for r in res:
        #         user_name = tae.User_Name
        #         total_hrs = tae.Total_Sum
        #         # user_name = user_name.split(", ")
        #         # user_name = user_name[1] + ' ' + user_name[0]
        #         if r.EmpName == user_name:
        #             th = int(total_hrs/8)
        #             retae_working[user_name] = th

        
        for tae in MasterTAE.objects.raw(
                f'select distinct id, User_Name, sum(Total_Hrs) as Total_Sum from TAE_mastertae where (activity not like "Leave%"' +

                f'and activity not like "Sick%"' +

                f'and activity not like "Holiday") and Date like "{yr}-{mn}%" group by 2'):
            for r in res:
                user_name = tae.User_Name
                total_hrs = tae.Total_Sum
                # user_name = user_name.split(", ")
                # user_name = user_name[1] + ' ' + user_name[0]
                if r.EmpName == user_name:
                    th = int(total_hrs/8)
                    retae_working[user_name] = th

        for tae in MasterTAE.objects.raw(

                f'select distinct id, User_Name, sum(Total_Hrs) as Total_Sum from TAE_mastertae where (activity like "Leave%"' +

                f'or activity like "Sick%"' +

                f'or activity like "Holiday") and Date like "{yr}-{mn}%" group by 2'):
            for r in res:
                user_name = tae.User_Name
                total_hrs = tae.Total_Sum
                # user_name = user_name.split(", ")
                # user_name = user_name[1] + ' ' + user_name[0]
                if r.EmpName == user_name:
                    th = int(total_hrs/8)
                    retae_leaves[user_name] = th

        for key, value in retae_working.items():
            # print(retae_leaves.get(key), retae_leaves.get(value))
            
            rel = retae_leaves.get(key)
            if not rel:
                retae[key] = value
            else:
                retae[key] = value + rel

        if (len(selected_activities)!=0):
            # for tae in MasterTAE.objects.raw(
            #         f'select distinct id, User_Name, sum(Total_Hrs) as Total_Sum from TAE_mastertae where (activity not like "Leave%"' +

            #         f'and activity not like "Sick%"' +

            #         f'and activity not like "Holiday") and Date like "{yr}-{mn}%" group by 2'):
            #     for r in res:
            #         user_name = tae.User_Name
            #         total_hrs = tae.Total_Sum
            #         # user_name = user_name.split(", ")
            #         # user_name = user_name[1] + ' ' + user_name[0]
            #         if r.EmpName == user_name:
            #             th = int(total_hrs/8)
            #             retae_working[user_name] = th
            # print(len(selected_activities))
            query_list = 'activity = "'+selected_activities[0]+'"'
            for i in range(1, len(selected_activities)):
                query_list += ' or activity = "'+selected_activities[i]+'"'
            # print(query_list)
            # print(yr,mn)
            query_string = f'select distinct id, User_Name, sum(Total_Hrs) as Total_Sum from TAE_mastertae where ('+query_list+') and Date like "'+yr+'-'+mn+'%" group by 2'
            # print(query_string)
            names = []
            for tae in MasterTAE.objects.raw(query_string):
                # print("OK")
                
                for r in res:
                    user_name = tae.User_Name
                    total_hrs = tae.Total_Sum
                    

                    # print(retae_working)
                    # print(tae.User_Name)
                    # user_name = user_name.split(", ")
                    # user_name = user_name[1] + ' ' + user_name[0]
                    if r.EmpName == user_name:
                        # print(names)
                        if user_name not in names :
                            names.append(user_name)
                        print(names)
                        th = int(total_hrs/8)
                        retae_working[r.EmpName] = th

                    if r.EmpName not in names:
                        retae_working[r.EmpName] = 0
                    # else :
                    #     # print(user_name)
                    #     retae_working[r.EmpName] = 0
        # for tae in MasterTAE.objects.raw(

        #         f'select distinct id, User_Name, sum(Total_Hrs) as Total_Sum from TAE_mastertae where (activity like "Leave%"' +

        #         f'or activity like "Sick%"' +

        #         f'or activity like "Holiday") and Date like "{yr}-{mn}%" group by 2'):
        #     for r in res:
        #         user_name = tae.User_Name
        #         total_hrs = tae.Total_Sum
        #         # user_name = user_name.split(", ")
        #         # user_name = user_name[1] + ' ' + user_name[0]
        #         if r.EmpName == user_name:
        #             th = int(total_hrs/8)
        #             retae_leaves[user_name] = th
        # print(retae)
        # for key, value in retae_working.items():
        #     # print(retae_leaves.get(key), retae_leaves.get(value))
            
        #     rel = retae_leaves.get(key)
        #     if not rel:
        #         retae[key] = value
        #     else:
        #         retae[key] = value + rel

        for tim in Attendance.objects.raw(
                f"select distinct id, EmpCode, count(Status) as Attendance from TimeEntry_attendance where (Status like 'C' or  Status = 'W') and Date like '%{month}-{yr}%' group by 2"):
            for r in res:
                emp_code = str(tim.EmpCode)
                # print(emp_code+count(Status))
                if str(r.EmpCode) == emp_code:
                    # print(emp_code+"="+str(tim.Attendance))
                    ta = tim.Attendance
                    reatt_working[r.EmpName] = ta

        for tim in Attendance.objects.raw(
                f"select distinct id, EmpCode, count(Status) as Attendance from TimeEntry_attendance where (Status like 'L') and Date like '%{str(month)}-{str(yr)}%' group by 2"):
            for r in res:
                emp_code = str(tim.EmpCode)
                if str(r.EmpCode) == emp_code:
                    # print(emp_code+"="+str(tim.Attendance))
                    ta = tim.Attendance
                    reatt_leaves[r.EmpName] = ta

        for key, value in reatt_working.items():
            rel = reatt_leaves.get(key)
            if not rel:
                reatt[key] = value
            else:
                reatt[key] = value + rel

        context = {'retae_working': retae_working,
                   'retae_leaves': retae_leaves,
                   'reatt_working': reatt_working,
                   'reatt_leaves': reatt_leaves,
                   'reatt': reatt,
                   'retae': retae,
                   'year': year,
                   'month': month,
                   'activities':my_activities}
    else:
        return redirect('login')
    return render(request, "reconciliation.html", context)
