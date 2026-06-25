from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.

class Club(models.Model):
    #club_id = models.IntegerField('社團id' , default=0)
    club_name = models.CharField('社團名稱' , max_length=64)
    max_people_num = models.IntegerField('社團人數上限' , default=0)
    now_people_num = models.IntegerField('社團現有人數' , default=0, validators=[MinValueValidator(1),MaxValueValidator(512)])

    def __str__(self):
        return f"{self.club_name}"


class User(AbstractUser):
    #us_id = models.IntegerField('使用者編號' , default=0)
    #  = models.CharField('使用者姓名' , max_length=64)
    # us_email = models.CharField('使用者信箱', max_length=128)
    class Rank(models.IntegerChoices):
        lv1 = 1 #最高權限管理人
        lv2 = 2 #校方人員:可進行除了任命1級人員和更改後台之外的所有動作
        lv3 = 3 #社長:只比4級人員多了可以對所屬社團的聲請表單進行認證的功能
        lv4 = 4 #一班學生:只能進行表單填寫和瀏覽   

    us_rank = models.IntegerField('權限等級劃分' , choices=Rank.choices, default=Rank.lv4)
    # club = models.ForeignKey(Club , models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所屬社團')  #AI提供的版本，以便解決少數帳號能在沒有社團的狀況下建立

    def clean(self):
        super().clean()
        if self.us_rank in [self.Rank.lv3, self.Rank.lv4] and not self.club:
            raise ValidationError({
                'club': '3級(社長)與4級(一般學生)必須選擇所屬社團！'
            })
        if self.us_rank in [self.Rank.lv1, self.Rank.lv2] and self.club:
            # 做法選項一：自動幫他清空社團
            self.club = None
            raise ValidationError({'club': '1級與2級管理人員不應該隸屬於任何社團！'})

    def save(self, *args, **kwargs):  #自動化權限給予

        # 在儲存前，強迫執行 clean() 的驗證邏輯
        self.full_clean()

        if self.us_rank == self.Rank.lv1:
            self.is_superuser = True
            self.is_staff = True  #決定使用者是否能登入後台
        elif self.us_rank == self.Rank.lv2:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)
        
    #one to one?(已捨棄)


    # def save(self, *args, **kwargs):
    #     # 在儲存前，強迫執行 clean() 的驗證邏輯
    #     self.full_clean() 
        
    #     # 原本自動調整 is_superuser 的邏輯
    #     if self.us_rank == self.Rank.lv1:
    #         self.is_superuser = True
    #         self.is_staff = True
    #     elif self.us_rank == self.Rank.lv2:
    #         self.is_staff = True
    #         self.is_superuser = False
    #     else:
    #         self.is_staff = False
    #         self.is_superuser = False
            
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}-{self.email}"

class Apply(models.Model):
    #ap_id = models.IntegerField('申請單id' , default=0)
    created = models.DateField('表單建立時間' , auto_now_add=True)
    sstu1_pass = models.BooleanField('原社長同意' ,null=True ,blank=True ,default=None)
    sstu2_pass = models.BooleanField('新社長同意' ,null=True ,blank=True ,default=None)
    sch_pass = models.BooleanField('學校同意',null=True, blank=True, default=None)
    user = models.ForeignKey(User , models.CASCADE)
    club = models.ForeignKey(Club ,models.CASCADE)
    club_after = models.ForeignKey(Club , on_delete=models.CASCADE, related_name='after_apply', null=True, blank=True)
    
    #原社長確認權限
    def can_user_check_sstu1(self, reviewing_user):
        if reviewing_user.us_rank == User.Rank.lv1:  #這裡先設定只有1級和該社社長可以確認，不包括校方人員
            return True
        
        if reviewing_user.us_rank == User.Rank.lv3 and reviewing_user.club == self.club:
            return True 

    #新社長確認權限
    def can_user_check_sstu2(self, reviewing_user):
        if reviewing_user.us_rank == User.Rank.lv1:
            return True
        # 比對登入者的社團，是否等於這張單子申請轉入的「新社團 (club_after)」
        if reviewing_user.us_rank == User.Rank.lv3 and reviewing_user.club == self.club_after:
            return True
        return False
    
    #校方人員確認權限
    def can_user_check_school(self, reviewing_user):
        if reviewing_user.us_rank in [User.Rank.lv1, User.Rank.lv2]:
            return True
        return False
#    def __str__(self):
#       return self.

class Log(models.Model): #包含記錄追尋
    #path_id = models.IntegerField('歷史路徑id' , default=0)
    result = models.BooleanField('審查結果' , default=False)
    date = models.DateField('審核時間' , auto_now_add=True)
    state = models.IntegerField('目前審核狀態' , default=0) #0=不通過 ; 1=審核中 : 2=通過 ; 3=其他
    apply = models.ForeignKey(Apply , models.CASCADE) 
    user = models.ForeignKey(User , models.CASCADE)
    club = models.ForeignKey(Club , models.CASCADE)

    def __str__(self):
        return f"{self.user.username}-{self.date}"