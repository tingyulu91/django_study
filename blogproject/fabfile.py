from fabric.api import env, run
from fabric.operations import sudo

#pip install fabric 目前仅支持Python2（推荐python2.7）
#在python2的环境下用fab命令运行这个脚本文件--> fab deploy

GIT_REPO = "your git repository" #改成你的代码托管仓库地址

#配置一些服务器的地址信息和账户信息，用于远程连接服务器
env.user = "your host username" #用于登录服务器的用户名
env.password = "your host password"#用户名对应的密码

#请填写你自己的主机对应的域名，例子如下
env.hosts = ['demo.zmrenwu.com']#服务器的IP地址，也可以是解析到这个IP的域名

#一般情况下为22端口，如果非22端口请查看你的主机服务提供商提供的信息
env.port = '22'#SSH远程服务器的端口号

def deploy(): # 注意： 全部的脚本代码要放在deploy函数里。Fabric会自动检测fabfile.py脚本中的deploy函数并运行
    source_folder = '/home/yangxg/sites/zmrenwu.com/django-blog-tutorial' #需要部署的项目根目录在服务器上的位置

    #通过run方法在服务器上执行命令，传入的参数为需要执行的命令，用字符串包裹。不同命令间用&&符号连接
    run('cd %s && git pull' % source_folder) #cd命令进入到需要部署的项目根目录， git pull拉去远程仓库的最新代码
    run("""
        cd {} &&
        ../env/bin/pip install -r requirements.txt &&
        ../env/bin/python3 manage.py collectstatic --noinput &&
        ../env/bin/python3 manage.py migrate
        """.format(source_folder))#因为启动了虚拟环境，所以运行的是虚拟环境../env/bin/下的pip和python
        # 如果项目引入了新的依赖，需要执行pip install -r requirements.txt安装最新依赖
        # 如果修改或新增了项目静态文件，需要执行python manage.py collectstatic 收集静态文件
        # 如果数据库发生了变化，需要执行 python manage.py migrate 迁移数据库
    # 重启 Nginx 和 Gunicorn 使改动生效
    sudo('restart gunicorn-demo.zmrenwu.com') #重启Gunicorn，需要在超级权限下运行
    sudo('service nginx reload')#重启Nginx，需要在超级权限下运行
