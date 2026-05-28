from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class Club(models.Model):
    #club_id = models.IntegerField('社團id' , default=0)
    club_name = models.CharField('社團名稱' , max_length=64)
    max_people_num = models.IntegerField('社團人數上限' , default=0)
    now_people_num = models.IntegerField('社團現有人數' , default=0, validators=[MinValueValidator(0),MinValueValidator(512)])

    def __str__(self):
        return f"{self.club_name}"


class User(models.Model):
    #us_id = models.IntegerField('使用者編號' , default=0)
    us_name = models.CharField('使用者姓名' , max_length=64)
    us_email = models.CharField('使用者信箱', max_length=128)
    us_rank = models.IntegerField('使用者身分' , default=0) #0=轉社學生 ; 社長=1 ; 2=教師 ; 3=行政 (問題:如果是社長要轉社)
    club = models.ForeignKey(Club , models.CASCADE)
    #one to one

    def __str__(self):
        return f"{self.us_name}-{self.us_email}"

class Apply(models.Model):
    #ap_id = models.IntegerField('申請單id' , default=0)
    created = models.DateField('表單建立時間' , auto_now_add=True)
    sstu_pass = models.BooleanField('社長同意' ,default=False)
    sch_pass = models.BooleanField('學校同意', default=False)
    user = models.ForeignKey(UserProfile , models.CASCADE)
    club = models.ForeignKey(Club ,models.CASCADE)
    club_after = models.ForeignKey(Club ,
                                # models.CASCADE
                                on_delete=models.CASCADE,
                                related_name='after_apply',
                                null=True,
                                blank=True
                                )
#    def __str__(self):
#       return self.

class Log(models.Model): #包含記錄追尋
    #path_id = models.IntegerField('歷史路徑id' , default=0)
    result = models.BooleanField('審查結果' , default=False)
    date = models.DateField('審核時間' , auto_now_add=True)
    state = models.IntegerField('目前審核狀態' , default=0) #0=不通過 ; 1=審核中 : 2=通過 ; 3=其他
    apply = models.ForeignKey(Apply , models.CASCADE) 
    user = models.ForeignKey(UserProfile , models.CASCADE)
    club = models.ForeignKey(Club , models.CASCADE)

    def __str__(self):
        return f"{self.user.us_name}-{self.date}"