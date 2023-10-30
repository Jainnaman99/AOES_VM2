from django.shortcuts import render
from django.views.decorators.cache import cache_control
from Contracts.models import Contract
from Middlewares.auth import auth_middleware
from django.http import HttpResponse


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@auth_middleware
def contracts(request):
    allContracts = Contract.objects.all()
    context = {'contracts': allContracts}
    return render(request, "contracts.html", context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @auth_middleware
def contract(request,contract_acronym):
    # contract_name=[]
    # contract_type=[]
    # FTE_count=[]
    # total_contract_value=[]
    # balance=[]
    # start_date=[]
    # end_date=[]
    # total_amount_consumed=[]
    # status=[]
    # return HttpResponse(contract_acronym)
    # return render(request, "edit_contract.html")
    for c in Contract.objects.raw(f"select * from Contracts_contract where contract_acronym ='{contract_acronym}'"):
        # contract_name.append(c.contract_name)
        # contract_type.append(c.contract_type)
        # FTE_count.append(c.FTE_count)
        # total_contract_value.append(c.total_contract_value)
        # balance.append(c.balance)
        # start_date.append(c.start_date)
        # end_date.append(c.end_date)
        # total_amount_consumed.append(c.total_amount_consumed)
        # status.append(c.status)
        contract_name=c.contract_name
        contract_type=(c.contract_type)
        FTE_count=(c.FTE_count)
        total_contract_value=(c.total_contract_value)
        balance=(c.balance)
        start_date=(c.start_date)
        end_date=(c.end_date)
        total_amount_consumed=(c.total_amount_consumed)
        status=(c.status)
        revenue_projection=c.revenue_projection
        revenue_recognised=c.revenue_recognised
        

    # return HttpResponse(list_c)
    context = {'contract_name': contract_name,
    'contract_acronym':contract_acronym,
    'contract_type': contract_type,
    'FTE_count': FTE_count,
    'total_contract_value': total_contract_value,
    'balance': balance,
    'start_date': start_date,
    'end_date': end_date,
    'total_amount_consumed': total_amount_consumed,
    'status': status,
    'revenue_projection':revenue_projection,
    'revenue_recognised':revenue_recognised,

    }
    return render(request, "edit_contract.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@auth_middleware
def saveContract(request):
    context = {'isSaved': False}
    if request.method == "POST":
        contract_name = request.POST.get('contract-name')
        contract_acronym = request.POST.get('contract-acronym')
        contract_type = request.POST.get('contract-type')
        fte_count = request.POST.get('fte-count')
        contract_value = request.POST.get('total-contract-value')
        start_date = request.POST.get('start-date')
        end_date = request.POST.get('end-date')
        status = request.POST.get('status')

        contract_data = Contract(contract_name=contract_name, contract_acronym=contract_acronym,
                                 contract_type=contract_type, FTE_count=fte_count, total_contract_value=contract_value, start_date=start_date, end_date=end_date, status=status, revenue_projection=0, revenue_recognised=0)
        contract_data.save()
        context = {'isSaved': True}

    return render(request, "add_contract.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@auth_middleware
def editContracts(request):
    return render(request, "edit_contract.html")


# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def newPage(request):
#     return render(request, "abc.html")

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @auth_middleware
# def addContracts(request):
#     return render(request, "add_contract.html")
