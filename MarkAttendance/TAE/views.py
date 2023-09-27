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
                for f in docfiles:
                        newdoc = TAESheet(docfile=f)
                        if not f.name.endswith('xlsx'):
                            # print("inside EXCELDATA ends with xlsx")
                            return render(request, 'MultiTAE.html', {'isValid': False, 'role': "user" if (request.user.appusers.roles.filter(name="User").exists()) else "admin"})
                        newdoc.save()
                # for f in docfiles:
                #     newdoc = TAESheet(docfile = f)
                #     newdoc.save()
                # context = {'msg' : '<span style="color: green;">File successfully uploaded</span>'}
                # return render(request, "MultiTAE.html", context)
    #=====================================================================================================
                path = str(base_dir) + "/media/documents/TAE"
                file_list = glob.glob(path+"/*.xlsx")

                excl_list = []

                for file in file_list:
                    excl_list.append(pd.read_excel(file))

                # excl_merged = pd.DataFrame()

                # for excl_file in excl_list:
                #     excl_merged = excl_merged.append(excl_file, ignore_index=True)
                excl_merged = pd.concat(excl_list, ignore_index=True)
                
                excl_merged.to_excel(str(base_dir)+"/media/TAE_Merged.xlsx", index=False)
                masterTAE = open(str(base_dir)+"/media/TAE_Merged.xlsx", 'rb')
                empexceldata = pd.read_excel(masterTAE)
                dbframe = empexceldata
                for dbframe in dbframe.itertuples():
                    print(dbframe)
                    if not MasterTAE.objects.filter(User_Name=dbframe._1, Date=dbframe.Date, Activity=dbframe.Activity):
                        obj = MasterTAE.objects.create(User_Name=dbframe._1,Location=dbframe.Location, Date=dbframe.Date,
                                                    Project=dbframe.Project, Project_Task=dbframe._5, Activity=dbframe.Activity, 
                                                    Role=dbframe.Role, Internal_Note=dbframe._8, Bill_Rate=dbframe._9,Bill_Hrs=dbframe._10,
                                                    NB_Hrs=dbframe._11, Total_Hrs=dbframe._12, Revenue_Reason=dbframe._13)           
                        obj.save()
                downloadfile = str(base_dir)+"/media/TAE_Merged.xlsx"

                #deleting residue files

                files = TAESheet.objects.all()
                for file in files:
                    file.docfile.delete()
                    file.delete()
    #======================================================================================================
                return render(request, "download_merged.html", {'file' : downloadfile,'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin"})
            else:
                return render(request, 'MultiTAE.html', {'isValid': False, 'role': "user" if (request.user.appusers.roles.filter(name="User").exists()) else "admin"})
        except Exception as e :
            return render(request, 'MultiTAE.html', {'isValid': False, 'role': "user" if (request.user.appusers.roles.filter(name="User").exists()) else "admin"})
            
    else:
        form = TAEUploadMultiForm()
    return render(request, 'MultiTAE.html', {'form':form,'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin"})

@auth_middleware
@never_cache
def deleteTAE(request):
    files = TAESheet.objects.all()
    for file in files:
        file.docfile.delete()
        file.delete()
    
    return HttpResponse("Files removed successfully")


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
    if month < 10:
        mn = "0"+str(month)
    else:
        mn = str(month)

    reatt_working = {}
    reatt_leaves = {}
    retae_working = {}
    retae_leaves = {}
    reatt = {}
    retae = {}
    
	
    for tae in MasterTAE.objects.raw(
            f'select distinct id, User_Name, sum(Total_Hrs) as Total_Sum from TAE_mastertae where (activity not like "Leave%"' +

            f'and activity not like "Sick%"' +

            f'and activity not like "Comp%"' +

            f'and activity not like "Holiday") and Date like "{yr}-{mn}%" group by 2'):
        for r in res:
            user_name = tae.User_Name
            total_hrs = tae.Total_Sum
            user_name = user_name.split(", ")
            user_name = user_name[1] + ' ' + user_name[0]
            if r.EmpName == user_name:
                th = int(total_hrs/8)
                retae_working[user_name] = th

    for tae in MasterTAE.objects.raw(

            f'select distinct id, User_Name, sum(Total_Hrs) as Total_Sum from TAE_mastertae where (activity like "Leave%"' +

            f'or activity like "Sick%"' +

            f'or activity like "Comp%"' +

            f'or activity like "Holiday") and Date like "{yr}-{mn}%" group by 2'):
        for r in res:
            user_name = tae.User_Name
            total_hrs = tae.Total_Sum
            user_name = user_name.split(", ")
            user_name = user_name[1] + ' ' + user_name[0]
            if r.EmpName == user_name:
                th = int(total_hrs/8)
                retae_leaves[user_name] = th

    for key, value in retae_working.items():
        rel = retae_leaves.get(key)
        if not rel:
            retae[key] = value
        else:
            retae[key] = value + rel

    for tim in Attendance.objects.raw(
            # f"select distinct id, EmpCode, count(Status) as Attendance from TimeEntry_attendance where Status = 'W' and Date like '%{month}-{yr}%' group by 2"):
            f"select distinct id, EmpCode, count(Status) as Attendance from TimeEntry_attendance where (Status like 'C' or  Status = 'W') and Date like '%{month}-{yr}%' group by 2"):
        for r in res:
            emp_code = str(tim.EmpCode)
            if str(r.EmpCode) == emp_code:
                ta = tim.Attendance
                reatt_working[r.EmpName] = ta

    for tim in Attendance.objects.raw(
            # f"select distinct id, EmpCode, count(Status) as Attendance from TimeEntry_attendance where (Status like 'CO%' or Status like 'L') and Date like '%{str(month)}-{str(yr)}%' group by 2"):
            f"select distinct id, EmpCode, count(Status) as Attendance from TimeEntry_attendance where (Status like 'L') and Date like '%{str(month)}-{str(yr)}%' group by 2"):
        for r in res:
            emp_code = str(tim.EmpCode)
            if str(r.EmpCode) == emp_code:
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
                'reatt' : reatt,
                'retae' : retae,
                'year': year,
                'month': month}
 else:
    return redirect('login')
 return render(request, "reconciliation.html", context)

