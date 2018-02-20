## 基本要求
    - Linux 操作系统，最好是 Ubuntu 16.04
    - 超级权限（root 用户登录）

## 安装 Docker （Ubuntu 16.04）
```
apt-get remove docker docker-engine docker.io
apt-get update
apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt-get update
apt-get install docker-ce
```

## 安装 botvs runtime
```
docker pull fanhed/botvsrt
```

## 运行 botvs 托管者
进入到托管者的目录，假设托管者的目录在 /home/demo/botvs，则如下执行:
```
cd /home/demo/botvs
docker run -it --rm -h botvsrt -v `pwd`:/mnt fanhed/botvsrt
cd /mnt
```
然后按照 botvs 网站上的托管者的命令运行 robot 即可，形如 ./robot xx yy zz
