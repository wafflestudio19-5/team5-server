from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

class SocialLoginSignupForm(forms.Form):
    username = forms.CharField(required=True, max_length=100)   # id
    # password는 따로 입력받지 않았음
    email = forms.EmailField(required=True, max_length=255)
    nickname = forms.CharField(required=True, max_length=30)
    univ = forms.CharField(required=True, max_length=50)
    admission_year = forms.ChoiceField(choices=User.YEAR_CHOICES, required=True)
    profile_picture = forms.ImageField(required=False)

    def clean_admission_year(self):
        admission_year = self.cleaned_data.get('admission_year')
        if (admission_year, admission_year) not in User.YEAR_CHOICES:
            raise forms.ValidationError('학번을 올바르게 입력하세요.')
        return admission_year

    # 소셜 계정으로 가입하더라도 아이디를 만들게 할 것인가? 만들지 않으면 지워도 될듯
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('이미 존재하는 아이디입니다.')
        return username

    # 사실 이전 social login 단계에서 email 중복이 체크되는지 안되는지 아직 모르겠음
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('이미 존재하는 이메일입니다.')
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if User.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError('이미 존재하는 닉네임입니다.')
        return nickname

    def signup(self, request, user):    # 여기서 user는 새로 만들어진 user를 의미
        user.username = self.cleaned_data['username']
        user.nickname = self.cleaned_data['nickname']
        user.univ = self.cleaned_data['univ']
        user.admission_year = self.cleaned_data['admission_year']
        user.profile_picture = self.cleaned_data['profile_picture']
        user.save()