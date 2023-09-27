from django.shortcuts import render,HttpResponse

from Middlewares.auth import auth_middleware
from .forms import ResourceForm,ResetForm
from .models import Resource
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from Authentication.models import UserRole, ApplicationUser
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.conf import settings
import json


base_dir = str(settings.BASE_DIR)
password1 = 'Per@1234'
# Create your views here.
@auth_middleware
def onboard(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        updated = False
        if form.is_valid():
            # form.save(commit=False)
            print(Resource.objects.filter(EmpCode = form.data['EmpCode']))
            if len(Resource.objects.filter(EmpCode = form.data['EmpCode'])) != 0:
                form.save(commit=False)
                member = Resource.objects.get(EmpCode = form.data['EmpCode'])
                empname = request.POST['EmpName']
                sowroles = request.POST['SowRoles']
                role = request.POST['Role']
                location = request.POST['Location']
                billed = request.POST['Billed']
                status = request.POST['Status']
                project = request.POST['Project']
                # reset_password = request.POST['reset_password']
                # EmpCode = form.data['EmpCode']
                # if(reset_password == EmpCode):
                #     user = User.objects.get(username=EmpCode)
                #     user.set_password(password1)
                #     user.save()
                #     appuser = ApplicationUser.objects.get(user= user)
                #     print(appuser.reset)
                #     appuser.reset = False
                #     appuser.save()
                #     reset_password = 0
                member.EmpName = empname
                member.SowRoles = sowroles
                member.Role = role
                member.Location = location
                member.Billed = billed
                member.Status = status
                member.Project = project
                updated = True
                member.save()
            
            else:
                form.save()
            source_data = Resource.objects.all()
            for data in source_data:
                if User.objects.filter(username=data.EmpCode).exists():
                    continue
                user = User(
                    username=data.EmpCode,
                    password = make_password(password1),    
                )
                user.save()
                appuser = ApplicationUser(user=user)
                role = UserRole.objects.get(name="User")
                print('Roles getting succesfull', role)
                appuser.save()
                appuser.roles.add(role)
                appuser.save()
            if updated:
                messages.success(request,f'{empname}\'s details updated successfully')
            else:
                messages.success(request,'New User Created Successfully')
                
    else :  
        form = ResourceForm()
    form = ResourceForm()

    return render(request, 'onboard.html', {'form' : form, 'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin"})


@auth_middleware
def bulk_upload(request):
    global color
    global updated
    color = "1"
    updated = False
    try:
        if request.method == "POST":
            if not 'ExcelData' in request.FILES:
                print("inside EXCELDATA")
                color = "0"
                messages.info(request, "Please Select An XLSX file to upload the data")
            else:
                ExcelData = request.FILES['ExcelData']

                if not ExcelData.name.endswith('xlsx'):
                    print("inside EXCELDATA ends with xlsx")
                    color = "0"
                    messages.info(request, "Wrong Format Only XLSX File's are accepted")
                    return render(request, 'bulk_upload.html',{'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin",'color':color})
                
                fs = FileSystemStorage()
                filename = fs.save(ExcelData.name, ExcelData)             
                empexceldata = pd.read_excel(base_dir+"/media/"+filename)        
                dbframe = empexceldata
                for dbframe in dbframe.itertuples():
                    print(dbframe)
                    find = Resource.objects.filter(EmpCode = dbframe.EmpCode)
                    if find :
                        member = Resource.objects.get(EmpCode = dbframe.EmpCode)
                        member.EmpName = dbframe.EmpName
                        member.SowRoles = dbframe.SowRoles
                        member.Role = dbframe.Role
                        member.Location = dbframe.Location
                        member.Billed = dbframe.Billed
                        member.Status = dbframe.Status
                        member.Project = dbframe.Project
                        updated = True
                        member.save()
                    else:   
                        obj = Resource.objects.create(EmpCode=dbframe.EmpCode,EmpName=dbframe.EmpName, SowRoles=dbframe.SowRoles,
                                                        Role=dbframe.Role, Location=dbframe.Location, Billed=dbframe.Billed, Status=dbframe.Status,Project=dbframe.Project)           
                        obj.save()

                source_data = Resource.objects.all()
                for data in source_data:
                    if User.objects.filter(username=data.EmpCode).exists():
                        continue
                    user = User(
                        username=data.EmpCode,
                        password = make_password(password1),    
                    )
                    user.save()
                    appuser = ApplicationUser(user=user)
                    role = UserRole.objects.get(name="User")
                    print('Roles getting succesfull', role)
                    appuser.save()
                    appuser.roles.add(role)
                    appuser.save()
                if updated:
                    print("inside Updated ")
                    color = "1"
                    messages.success(request,"User's Details Updated Successfully")
                    return render(request, 'bulk_upload.html',{'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin",'color':color})

                else:
                    print("inside Updated else block ")
                    color = "1"
                    messages.success(request,"New User's Created Successfully")
                    return render(request, 'bulk_upload.html',{'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin",'color':color})
                    
        return render(request, 'bulk_upload.html',{'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin",'color':color})
        
    except:
        color = "0"
        messages.info(request, "Excel Uploaded has a wrong format or it does not have relevant Titles It should have Titles (EmpCode| EmpName| SowRoles |Role|Priject| Location| Billed| Status)")
        return render(request, 'bulk_upload.html',{'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin",'color':color})
@auth_middleware           
def details(request):
    source_data = Resource.objects.all()
    for data in source_data:
        if User.objects.filter(username=data.EmpCode).exists():
            continue
        user = User(
            username=data.EmpCode,
            password = make_password(password1),    
        )
        user.save()
        appuser = ApplicationUser(user=user)
        role = UserRole.objects.get(name="User")
        print('Roles getting succesfull', role)
        appuser.save()
        appuser.roles.add(role)
        appuser.save()
    return render(request, "user_home.html")


def update_view(request):
    print('id is ')
    id=request.POST['id']
    user=Resource.objects.filter(EmpCode=id)[0]
    print(user)
    dic = {'empcode':user.EmpCode,
        'empname':user.EmpName,
        'empsowroles':user.SowRoles,
        'emprole' : user.Role,
        'emplocation' : user.Location,
        'empbilled' : user.Billed,
        'empstatus' : user.Status,
        'empproject':user.Project
    }
    dic=json.dumps(dic)
    return HttpResponse(dic)
            
@auth_middleware
def reset_pwd(request):
    if request.method == 'POST':
        form = ResetForm(request.POST)
        updated = False
        if form.is_valid():
            form.save(commit=False)
            print(form.data)
            # print(Resource.objects.filter(EmpCode = form.data['EmpCode']))
            if len(Resource.objects.filter(EmpCode = (form.data['EmpCode']))) != 0:
            # if (Resource.objects.filter(EmpCode = form.data['EmpCode'])):
                print("If")
                form.save(commit=False)
                reset_password = 'Per@1234'
                EmpCode = form.data['EmpCode']
                user = User.objects.get(username=EmpCode)
                user.set_password(reset_password)
                user.save()
                appuser = ApplicationUser.objects.get(user= user)
                print(appuser.reset)
                appuser.reset = False
                appuser.save()
                reset_password = 0
                updated = True
                messages.success(request,'Password reset successfully')
             
            else:
                # form.save()
                # print("Else")
                messages.error(request,'User Does Not Exist')
                return render(request, 'reset_pwd.html', {'form' : form, 'updated':updated, 'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin"})
            # if updated:
            #     messages.success(request,'Password reset successfully')
            # else:
            #     messages.success(request,'User Not Exist')
        
                
    else :  
        form = ResetForm()
    form = ResetForm()

    return render(request, 'reset_pwd.html', {'form' : form, 'role':"user" if(request.user.appusers.roles.filter(name="User").exists()) else "admin"})