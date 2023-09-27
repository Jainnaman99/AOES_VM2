from import_export import resources
from .models import MasterTAE

class TAEResource(resources.ModelResource):
    class Meta:
        model = MasterTAE