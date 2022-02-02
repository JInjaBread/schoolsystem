from import_export import resources
from .models import Staffs, Students, Question

class StaffResource(resources.ModelResource):
    class meta:
        model = Staffs

class StudentResource(resources.ModelResource):
    class meta:
        model = Students

class QuestionResource(resources.ModelResource):
    class meta:
        model = Question
