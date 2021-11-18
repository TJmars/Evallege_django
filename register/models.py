from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.validators import FileExtensionValidator


#大学モデル
class College(models.Model):
    college_name = models.CharField('大学名',max_length=200,blank=False)
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.college_name



#講義モデル
class Lecture(models.Model):
    lecture_name = models.CharField('講義名', max_length=200,blank=False)
    teacher_name = models.CharField('担当教員名', max_length=200,blank=False)
    college_name = models.ForeignKey(
                    College, verbose_name='大学名',
                    on_delete=models.PROTECT,blank=False
               )



    created_at = models.DateTimeField('作成日', default=timezone.now)


    def __str__(self):
        return self.lecture_name



class CustomUserManager(UserManager):
    """ユーザーマネージャー"""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""

    email = models.EmailField(_('email address'), unique=True)
    #first_name = models.CharField(_('first name'), max_length=30, blank=True)
    #last_name = models.CharField(_('last name'), max_length=150, blank=True)
    user_name = models.CharField(_('ユーザーネーム'), max_length=150, blank=False)


    college_name = models.ForeignKey(
                    College, verbose_name='大学名',
                    on_delete=models.PROTECT,blank=False
               )
    lecture_list = models.ManyToManyField(Lecture,through='UserLectureList', verbose_name='履修講義名',blank=True)

    user_point = models.IntegerField(
        verbose_name='ユーザーポイント',
        default=0,
    )


    invi_code = models.CharField('自分の招待コード',max_length=200,blank=False)
    input_invi_code = models.CharField('招待コード',max_length=200,blank=True)

    invi_point = models.IntegerField(
        verbose_name='被招待ポイント',
        default=0,
    )




    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    #def get_full_name(self):
    #    """Return the first_name plus the last_name, with a space in
        #between."""
    #    full_name = '%s %s' % (self.first_name, self.last_name)
        #return full_name.strip()""

#    def get_short_name(self):
    #    """Return the short name for the user."""
        #return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email


#評価モデル
class LectureEva(models.Model):
    lecture = models.ForeignKey(
         Lecture,verbose_name='講義名',
         on_delete=models.PROTECT,blank=False
    )

    user = models.ForeignKey(
           User, verbose_name='評価者',on_delete=models.PROTECT
    )

    PLACE = (
       (1, '対面'),
       (2, 'オンライン'),
    )


    GRADE_LANK = (
        (5, 'S'),
        (4, 'A'),
        (3, 'B'),
        (2, 'C'),
        (1, 'D'),
    )
    EVA_LANK = (
        (5, '多い'),
        (4, 'やや多い'),
        (3, '普通'),
        (2, 'やや少ない'),
        (1, '少ない'),
    )
    DIF_LANK = (
        (5, '簡単'),
        (4, 'やや簡単'),
        (3, '普通'),
        (2, 'やや難しい'),
        (1, '難しい'),
    )
    GAKUNEN_LANK = (
        (1,'１年'),
        (2,'２年'),
        (3,'３年'),
        (4,'４年'),
    )
    grade_lank = models.IntegerField(verbose_name='成績',choices=GRADE_LANK, blank=False)
    eva_lank = models.IntegerField(verbose_name='課題量',choices=EVA_LANK, blank=False)
    dif_lank = models.IntegerField(verbose_name='授業の難易度',choices=DIF_LANK, blank=False)
    gakunen_lank = models.IntegerField(verbose_name='学年',choices=GAKUNEN_LANK, blank=False)
    place = models.IntegerField(verbose_name='授業方式',choices=PLACE, blank=False)

    eva_comment = models.TextField(
        verbose_name='コメント(空欄可)',
        null=True,
        blank=True,
        max_length=200,
    )

    created_at = models.DateTimeField('作成日', default=timezone.now)


#ユーザーと履修講義の中間フィールド(講義を履修したdateを記録)
class UserLectureList(models.Model):
    lecture = models.ForeignKey(
         Lecture,verbose_name='講義名',
         on_delete=models.PROTECT,blank=False
    )

    user = models.ForeignKey(
           User, verbose_name='ユーザー',on_delete=models.PROTECT
    )
    created_at = models.DateTimeField('登録日', default=timezone.now)


#チャット用のモデル
class LectureChat(models.Model):


    lecture = models.ForeignKey(
         Lecture,verbose_name='講義名',
         on_delete=models.PROTECT,blank=False
    )
    user = models.ForeignKey(
           User, verbose_name='ユーザー',on_delete=models.PROTECT
    )

    chat_text = models.TextField(
    verbose_name='投稿',

    max_length=1000,
    )
    created_at = models.DateTimeField('登録日', default=timezone.now)

class Text_product(models.Model):
    """教科書の製品モデル"""
    product_name = models.CharField('教科書名', max_length=200)
    price = models.IntegerField(verbose_name='価格')
    pass_place = models.TextField('受け渡し日時/場所',default='')
    created_at = models.DateTimeField('出品日', default=timezone.now)
    on_sale = models.BooleanField(verbose_name='販売中かチェック', default=True)
    lecture = models.ForeignKey(Lecture, verbose_name='講義', on_delete=models.PROTECT)
    url = models.URLField('商品URL',max_length=200)


class Circle(models.Model):
    """サークル掲示板のモデル"""
    circle_name = models.CharField('団体名', max_length=200)

    GENRE = (
        (1,'球技'),
        (2,'スポーツ'),
        (3,'学問'),
        (4,'音楽'),
        (5,'その他'),
    )
    genre = models.IntegerField(verbose_name='ジャンル',choices=GENRE, blank=True)
    message = models.TextField(verbose_name='活動紹介、メッセージ', blank=True)
    day_place = models.TextField(verbose_name='活動日/場所', blank=True)
    member_num = models.TextField(verbose_name='所属人数', blank=True)
    cost = models.TextField(verbose_name='活動費用', blank=True)
    sns_mail = models.TextField(verbose_name='SNS/連絡先', blank=True)
    image = models.FileField(upload_to='circle_image/',verbose_name='画像',validators=[FileExtensionValidator(['pdf','jpg','jpeg','png','HEIC',])],blank=True)

    college = models.ForeignKey(
                    College, verbose_name='大学名',
                    on_delete=models.PROTECT
               )
    administrator = models.ForeignKey(User, verbose_name='管理者', on_delete=models.PROTECT)
    circle_id = models.IntegerField(verbose_name='ID')
    circle_password = models.CharField('パスワード', max_length=20)

    def __str__(self):
        return self.circle_name
