from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import College, Lecture, LectureEva, UserLectureList, LectureChat,Text_product,Circle,Board
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User
from import_export import resources
from import_export.admin import ImportExportMixin


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class EvaResource(resources.ModelResource):
    class Meta:
        model = LectureEva


class EvaAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = EvaResource

class LectureResource(resources.ModelResource):
    class Meta:
        model = Lecture


class EvaAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = LectureResource

admin.site.register(User)
admin.site.register(College)
admin.site.register(Lecture,EvaAdmin)
admin.site.register(LectureEva,EvaAdmin)
admin.site.register(UserLectureList)
admin.site.register(LectureChat)
admin.site.register(Text_product)
admin.site.register(Circle)
admin.site.register(Board)
