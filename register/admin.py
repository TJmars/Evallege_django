from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import College, Lecture, LectureEva, UserLectureList, LectureChat,Text_product
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


admin.site.register(User)
admin.site.register(College)
admin.site.register(Lecture)
admin.site.register(LectureEva)
admin.site.register(UserLectureList)
admin.site.register(LectureChat)
admin.site.register(Text_product)
