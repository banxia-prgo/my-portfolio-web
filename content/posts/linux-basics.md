+++
date = '2026-09-19T12:00:00+08:00'
title = 'Linux 基础学习笔记：常用命令、Vim、Shell 与编译工具'
summary = '整理 Linux 基础知识、文件与文本操作、进程和网络管理、Vim、Shell 脚本、软件安装、C/C++ 编译流程、Makefile 以及软硬链接。'
tags = ['Linux', 'Shell', 'Vim', 'C++', '学习笔记']
categories = ['Linux 学习']
draft = false
+++

Linux 是后端开发、服务器运维和 C/C++ 开发中经常接触的操作系统环境。本文根据学习笔记进行整理，覆盖 Linux 基础概念、常用命令、文本处理、Vim、Shell 脚本、软件安装、编译流程和链接文件等内容，作为日常学习与查阅的速记手册。

> 说明：本文以常见的 Linux 命令行环境为基础，部分命令参数会因发行版、权限和软件版本不同而有所差异。执行删除、关机、修改系统文件等操作前，应确认目标和当前用户权限。

## 一、Linux 基础概述

### 1.1 什么是操作系统

操作系统（Operating System，OS）是一套管理计算机硬件和软件资源的系统软件，负责进程管理、内存管理、文件管理、设备管理以及为应用程序提供运行环境。

常见操作系统包括 Windows、macOS、Linux、Android、iOS、HarmonyOS 以及 UNIX 系列系统。

### 1.2 Linux 的主要特点

Linux 常见特点包括开源、可定制、网络能力完善、权限管理清晰以及命令行工具丰富。Linux 适合服务器和开发环境，但并不是绝对不会受到病毒、木马或其他安全问题影响，实际使用中仍需及时更新软件、限制权限并做好备份。

### 1.3 内核与发行版

查看 Linux 内核版本：

```bash
uname -r
```

Linux 发行版是在内核基础上集成软件包管理器、系统工具、编译环境和其他软件形成的完整操作系统，例如 Ubuntu、Debian、CentOS、Rocky Linux 和 Fedora。

---

## 二、Linux 常用命令

### 2.1 命令基本格式

```bash
命令名称 [选项] [参数] [操作对象]
```

Linux 命令和文件名通常区分大小写。查看命令帮助：

```bash
man ls
man grep
whoami
```

### 2.2 文件和目录操作

```bash
ls              # 查看目录内容
ls -l           # 查看详细信息
ls -a           # 显示隐藏文件
ls -h           # 以易读形式显示文件大小
pwd             # 显示当前目录
cd /etc         # 切换目录
cd ..           # 返回上一级目录
cd ~            # 进入当前用户家目录
mkdir -p a/b/c  # 创建多级目录
touch demo.txt   # 创建文件或更新时间戳
cp -r src dst    # 复制目录
mv old new       # 移动或重命名
rm -r directory  # 递归删除目录
```

`ls -l` 的第一列表示文件类型和权限。常见文件类型包括目录 `d`、普通文件 `-`、软链接 `l`、管道 `p`、套接字 `s`、字符设备 `c` 和块设备 `b`。权限通常分为所有者、所属组和其他用户三组，`r`、`w`、`x` 分别表示读、写和执行。

绝对路径从根目录 `/` 开始，相对路径以当前目录为参照。`find` 可以按名称或类型查找文件：

```bash
find . -name '*.cpp'
find /var/log -type f -name '*.log'
find . -type d -name 'build'
```

通配符 `*` 匹配零个或多个字符，`?` 匹配一个字符。

> 注意：`rm` 不会像图形界面回收站一样自动保留副本。执行 `rm -rf` 前必须确认路径，尤其不要随意执行 `rm -rf /` 或未经检查的变量、通配符删除命令。

### 2.3 文本处理命令

查看文件：

```bash
cat demo.txt
cat -n demo.txt
less demo.txt
more demo.txt
head -3 demo.txt
tail -5 demo.txt
tail -f application.log
```

`less` 中可以使用 `/关键字` 搜索，按 `n` 查找下一个，按 `N` 查找上一个，按 `q` 退出。

查找文本：

```bash
grep -n 'error' application.log
grep -i 'error' application.log
grep -w 'error' application.log
grep -v 'debug' application.log
ps -ef | grep nginx
grep -n '^w' hello.txt
grep -n 'w$' hello.txt
```

`sed` 可以进行筛选、插入、删除和替换：

```bash
sed -n '3p' hello.txt
sed -n '3,5p' hello.txt
sed '3d' hello.txt
sed '2a 88888888' hello.txt
sed '3i 88888888' hello.txt
sed 's/nice/888/g' hello.txt
sed -i 's/old/new/g' hello.txt
```

修改源文件前，建议先不加 `-i` 检查输出结果，或提前备份。

`awk` 适合按列处理文本：

```bash
awk -F: '{print $1}' /etc/passwd
awk -F: 'NR==53 {print $1}' /etc/passwd
```

### 2.4 管道、重定向和基础工具

```bash
ps -ef | grep ssh
echo 'hello' > output.txt
echo 'world' >> output.txt
clear
date '+%Y-%m-%d'
cal 2026
```

`>` 会覆盖写入，`>>` 会追加写入；管道符 `|` 会将前一个命令的输出交给后一个命令处理。

---

## 三、系统、用户、进程与网络

用户管理：

```bash
useradd devuser
passwd devuser
userdel devuser
userdel -r devuser
su - devuser
exit
```

关机和重启：

```bash
poweroff
reboot
shutdown -h now
shutdown -r now
shutdown -h 10
```

磁盘和进程：

```bash
df -h
du -sh .
ps -ef
ps -ef | grep nginx
kill PID
kill -9 PID
```

通常应先使用普通的 `kill`，让进程有机会完成清理；`kill -9` 会强制终止进程，应谨慎使用。终端中的 `Ctrl + C` 通常用于中断当前前台程序。

网络命令：

```bash
ping -c 4 192.168.1.1
ping -c 4 example.com
ifconfig
netstat
```

部分新发行版中，`ifconfig` 和 `netstat` 可能需要额外安装，或者使用 `ip`、`ss` 等工具替代。

---

## 四、打包、解包和压缩

`tar` 常用参数：`-c` 创建归档、`-x` 解包、`-v` 显示过程、`-f` 指定文件名、`-z` 使用 gzip、`-j` 使用 bzip2、`-C` 指定操作目录。

```bash
tar -cvf cplus.tar 111.cpp 222.cpp 333.cpp
tar -xvf cplus.tar
tar -xvf cplus.tar -C ../banana
tar -zcvf cplus.tar.gz *.cpp
tar -zxvf cplus.tar.gz -C ../banana
```

---

## 五、Vim 基础使用

Vim 的核心是模式切换。普通模式用于移动和执行操作，插入模式用于输入文本，命令模式用于保存、退出和执行命令。

常用普通模式操作：

| 操作 | 功能 |
| --- | --- |
| `h`、`j`、`k`、`l` | 左、下、上、右移动 |
| `0`、`$` | 跳到行首、行尾 |
| `gg`、`G` | 跳到文件开头、末尾 |
| `x`、`dw`、`dd` | 删除字符、单词、行 |
| `yw`、`yy`、`p` | 复制单词、复制行、粘贴 |
| `u`、`Ctrl + r` | 撤销、重做 |
| `/关键字`、`n`、`N` | 搜索和切换匹配项 |

数字可以作为操作数量，例如 `3dd` 删除三行。

插入模式命令：

- `i`：在光标前插入。
- `a`：在光标后插入。
- `o`：在当前行后新建一行。
- `O`：在当前行前新建一行。
- `I`：在行首插入。
- `A`：在行尾插入。

命令模式：

```vim
:q
:wq
:q!
:set nu
:set nonu
:set hlsearch
:nohlsearch
:!ls
:s/old/new/g
:%s/old/new/gi
```

Vim 自带教程：

```bash
vimtutor
```

---

## 六、Shell 脚本入门

Shell 脚本是由 Shell 语法和 Linux 命令组成的脚本文件，可以把多个操作组织成自动化任务。常见的 Shell 是 Bash。

变量示例：

```bash
name='Banxia'
echo "$name"
unset name
```

变量名和等号之间不能有空格，使用变量时需要加 `$`。建议在引用变量时使用双引号，避免空格导致参数拆分。

`if` 示例：

```bash
#!/bin/bash

echo 'Please input your age:'
read -r age

if (( age <= 2 )); then
    echo '婴儿'
elif (( age <= 8 )); then
    echo '幼儿'
elif (( age <= 18 )); then
    echo '少年'
elif (( age <= 40 )); then
    echo '青年'
elif (( age <= 60 )); then
    echo '中年'
else
    echo '老年'
fi
```

`while` 示例：

```bash
#!/bin/bash
i=1
sum=0
while (( i <= 100 )); do
    (( sum += i ))
    (( i++ ))
done
echo "1+2+...+100 = $sum"
```

`for` 示例：

```bash
#!/bin/bash
sum=0
for (( i = 1; i <= 100; i++ )); do
    (( sum += i ))
done
echo "1+2+...+100 = $sum"
```

运行脚本：

```bash
chmod +x demo.sh
./demo.sh
```

---

## 七、Linux 下的软件安装

基于 RPM 的发行版可以使用 `yum`：

```bash
yum install 软件包名
yum -y install 软件包名
yum remove 软件包名
yum update 软件包名
yum list installed
yum info 软件包名
yum provides 命令名
```

不同发行版使用的包管理器可能不同，例如 Ubuntu/Debian 常用 `apt`。

从源代码安装通常包括下载、解压、配置、编译和安装：

```bash
wget https://www.memcached.org/files/memcached-1.6.45.tar.gz
tar -zxvf memcached-1.6.45.tar.gz
cd memcached-1.6.45
./configure
make
sudo make install
```

实际步骤应以项目 README 或官方安装文档为准。

---

## 八、C/C++ 源代码到可执行程序

传统 GCC 编译过程包括预处理、编译、汇编和链接：

```bash
gcc -E test.cpp -o test.ii
gcc -S test.ii -o test.s
gcc -c test.s -o test.o
g++ test.o -o test
```

流程可以概括为：

```text
源代码 → 预处理文件 → 汇编代码 → 目标文件 → 可执行程序
```

对于 C++ 程序，使用 `g++` 进行最终链接通常更加方便，因为它会自动处理 C++ 标准库链接。

---

## 九、Makefile 基础

当项目源文件较多时，逐个编译会比较繁琐。`make` 根据 Makefile 中的目标、依赖和命令，自动决定需要重新构建哪些内容。

```makefile
CXX = g++
CXXFLAGS = -std=c++11 -Wall

app: main.o
	$(CXX) main.o -o app

main.o: main.cpp
	$(CXX) $(CXXFLAGS) -c main.cpp -o main.o

clean:
	rm -f main.o app
```

执行：

```bash
make
make clean
```

Makefile 命令行通常必须使用 **Tab** 开头，而不是普通空格。

---

## 十、硬链接和软链接

创建硬链接：

```bash
ln source.txt hardlink.txt
```

创建软链接：

```bash
ln -s source.txt softlink.txt
```

主要区别：

1. 硬链接和原文件共享同一个 inode，软链接本身有独立的 inode。
2. 硬链接通常不能跨文件系统，软链接可以。
3. 硬链接通常不能直接链接目录，软链接可以指向目录。
4. 删除软链接的目标后，软链接可能变成悬空链接；硬链接只要仍有链接存在，数据通常仍可访问。

查看 inode 信息：

```bash
ls -li source.txt hardlink.txt softlink.txt
```

---

## 十一、学习总结

Linux 学习不应只停留在记忆命令，更重要的是理解命令之间如何组合，以及命令会对文件、进程和系统状态产生什么影响。

建议按照以下顺序练习：

1. 熟悉目录切换、文件创建、复制、移动和删除。
2. 使用 `cat`、`less`、`grep`、`sed` 和 `awk` 处理文本。
3. 掌握管道和重定向，尝试组合多个命令。
4. 使用 `ps`、`df`、`du` 和网络工具观察系统状态。
5. 使用 Vim 修改配置文件和编写代码。
6. 编写简单 Shell 脚本完成重复任务。
7. 理解 C/C++ 编译、链接过程，并使用 Makefile 管理项目。

掌握这些基础工具后，后续学习 Linux 服务部署、网络编程、进程间通信、性能分析和自动化运维会更加顺畅。
