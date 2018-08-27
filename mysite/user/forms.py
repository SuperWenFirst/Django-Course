from django import forms
from django.contrib import auth
from django.contrib.auth.models import User


# 定制登录表单
class LoginForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        required=True,  # 默认为True
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入用户名'
        }))
    # 设置渲染后的html的属性

    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        }))

    # 验证数据方法
    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('用户名或密码错误')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


class RegForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        required=True,  # 默认为True
        max_length=30,
        min_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入3-30位用户名'
        }))
    password = forms.CharField(
        label='设置密码',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        }))
    password_again = forms.CharField(
        label='确认密码',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '再输入一次密码'
        }))
    email = forms.EmailField(
        label='邮箱',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱'
        }))
    verification_code = forms.CharField(
        label='验证码',
        required=False,  # 为了在不填的时候可以点击发送邮件
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '点击“发送验证码”发送到邮箱'
        }))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')  # 接收传入的rquest信息, 并剔除，为了下一句不出错
        super(RegForm, self).__init__(*args, **kwargs)

    # 验证数据
    def clean(self):
        # 判断验证码
        code = self.request.session.get('register_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    # 验证数据, 是否有效，是否存在
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_again


class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(
        label='新的昵称',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入新的昵称'
        }))

    # 下面2个函数用于判断用户是否登录
    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')  # 接收用户信息, 并剔除，为了下一句不出错
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)

    # 验证数据
    def clean(self):
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()
        if nickname_new == '':
            raise forms.ValidationError('新的昵称不能为空')
        return nickname_new


class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入正确的邮箱'
        }))
    verification_code = forms.CharField(
        label='验证码',
        required=False,  # 为了在不填的时候可以点击发送邮件
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '点击“发送验证码”发送到邮箱'
        }))

    # 下面2个函数用于判断用户是否登录
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')  # 接收传入的rquest信息, 并剔除，为了下一句不出错
        super(BindEmailForm, self).__init__(*args, **kwargs)

    # 验证数据
    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 判断用户数会否已经绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('你已经绑定了邮箱')

        # 判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已经被绑定')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code',
                                                  '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code