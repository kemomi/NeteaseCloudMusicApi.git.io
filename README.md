### 项目说明



> 与其说是项目，实际上就是一个`python` 脚本，运行该脚本需要您电脑上有python环境，该脚本依赖github上这个项目：

https://github.com/kemomi/NeteaseCloudMusicApi.git.io

通过Node获取网抑云相关数据， 然后进行填充歌曲信息，该项目我以部署在远程服务器，小伙伴们可以不用本地运行了。

> 为什么需要本地操作呢？就一个原因，服务器带宽太贵了，本来想着小伙伴在网页上输入一个歌单id，
直接能下载歌曲的压缩包，然后直接导入，爽歪歪，但是没办法啊， 把文件放服务器上，小伙伴们下载太慢，简直龟速，把文件放oss上，服务器上行太慢，上传也是龟速，所以只能小伙伴们在电脑上操作下喽，我尽量将东西简单化，这次环境用到的是`python`，正好小伙伴们也可以一起玩一玩。



#### 前置条件

可以使用 `python3 --version` 来查看是否安装python环境，没有安装的小伙伴可以网上找下教程，很简单的



#### 项目目录

```shell
.
├── README.md 
├── config_demo.json # 配置文件例子
├── config.json # 配置文件
├── main.py # 主文件
└── requirements.txt # 依赖文件
```



#### 具体步骤 

1. **安装脚本依赖文件**

```python
pip3 install -r requirements.txt
```

2. **获取token**

> token是用户登陆凭证，因为获取歌单信息时候网易要求必须登陆，有些歌曲需要vip才能下载，所以需要token，获取方式也很简单，两种方式

- 第一种通过接口获取

  访问服务器接口（不会记录您的账号信息）：http://39.98.194.220:3000/login/cellphone?phone=xxx&password=xxx ，手机号和密码换成您自己的。





- 第二种通过查看网页版网易云获取

  在网易云网页版登陆您的账号，通过查看接口获取token







3. **填写配置文件**



- base_path：生成的歌曲目录
- playId：歌单id
- token：第二步获取



4. **执行脚本**

```python
python3 main.py
```





