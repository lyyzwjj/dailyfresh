from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponseRedirect
from .models import *
from hashlib import sha1
from . import user_decorator



def register(request):
    return render(request, 'df_user/register.html', {'title': '用户注册'})

def register_handle(request):
    # 接受用户输入
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemail = post.get('email')
    # 判断两次密码:
    if upwd != upwd2:
        return redirect('/user/register/')

    # 密码加密
    s1 = sha1()
    s1.update(bytes(upwd, encoding='utf-8'))
    upwd3 = s1.hexdigest()

    # 创建对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()

    # 注册成功，转到登陆页面
    return redirect('/user/login/')

# 注册页判断用户名是否存在
def register_exist(request):
    uname = request.GET['uname']
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count':count})

def login(request):
    uname = request.COOKIES.get('uname')

    # print(uname)
    return render(request, 'df_user/login.html', {'title': '用户登录', 'error_user':0, 'error_pass': 0, 'uname': uname})



def login_handle(request):
    uname = request.POST['username']
    upwd = request.POST['pwd']
    jizhu = request.POST.get('jizhu', 0)
    # print(jizhu)

    user = UserInfo.objects.filter(uname=uname)
    if len(user) == 0:
        return render(request, 'df_user/login.html', {'title': '用户登录', 'error_user':1, 'error_pass': 0, 'uname': uname})

    s1 = sha1()
    s1.update(bytes(upwd, encoding='utf-8'))
    pwd2 = s1.hexdigest()
    if user[0].upwd != pwd2:
        return render(request, 'df_user/login.html', {'title': '用户登录', 'error_user': 0, 'error_pass': 1, 'uname': uname})
    else:
        url = request.COOKIES.get('url','/')

        red = HttpResponseRedirect(url)


        if int(jizhu) == 1:
            red.set_cookie('uname', uname)
            print(uname)
        else:
            red.set_cookie('uname', '', max_age=-1)
        request.session['user_id'] = user[0].id
        request.session['uname'] = uname
        return red


@user_decorator.login
def info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail
    context = {'title': '用户中心', 'user_email': user_email, 'uname': request.session['uname']}
    return render(request, 'df_user/user_center_info.html', context)


@user_decorator.login
def order(request):
    context = {'title': '用户中心'}
    return render(request, 'df_user/user_center_order.html', context)


@user_decorator.login
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uyoubian = post.get('uyoubian')
        user.uphone = post.get('uphone')
        user.save()
    context = {'title': '用户中心', 'user': user}
    return render(request, 'df_user/user_center_site.html', context)

def logout(request):
    request.session.flush()
    return redirect('/index/')