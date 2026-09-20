+++
date = '2026-09-20T18:30:00+08:00'
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

常见操作系统包括：

- **Windows**：常见的桌面操作系统，也广泛应用于企业环境。
- **macOS**：Apple 设备使用的桌面操作系统。
- **Linux**：广泛应用于服务器、嵌入式设备、开发环境和云计算平台。
- **Android**：基于 Linux 内核的移动操作系统。
- **iOS**：Apple 移动设备使用的操作系统。
- **HarmonyOS**：华为相关设备使用的操作系统平台。
- **UNIX 及其商业系统**：例如 AIX、HP-UX 和 Solaris。

### 1.2 Linux 的主要特点

Linux 常见特点包括：

1. **开源**：源代码可以在许可证允许的范围内查看、修改和分发。
2. **稳定性较好**：适合长时间运行的服务器和后台服务，但稳定性仍然取决于内核、软件、配置和运维方式。
3. **网络能力完善**：提供丰富的网络工具和服务能力。
4. **权限管理清晰**：通过用户、用户组和文件权限控制资源访问。
5. **命令行工具丰富**：便于自动化、远程管理和批量处理。

Linux 并不是绝对不会受到病毒、木马或其他安全问题影响。实际使用中仍然需要及时更新软件、限制权限、配置防火墙并做好日志和备份管理。

### 1.3 内核与发行版

Linux 内核负责进程、内存、设备、文件系统和网络等核心功能。常用命令如下：

```bash
uname -r
```

发行版是在 Linux 内核基础上，集成软件包管理器、系统工具、编译环境、桌面组件和其他软件形成的完整操作系统，例如 Ubuntu、Debian、CentOS、Rocky Linux 和 Fedora。

---

## 二、Linux 常用命令

### 2.1 命令的基本格式

常见命令格式为：

```bash
命令名称 [选项] [参数] [操作对象]
```

Linux 命令和文件名通常区分大小写。多个短选项有时可以合并，例如 `ls -l -a` 可以写成 `ls -la`，但具体是否支持合并要以命令说明为准。

查看命令帮助：

```bash
man ls
man grep
```

查看当前用户：

```bash
whoami
```

### 2.2 文件和目录操作

#### `ls`：查看目录内容

```bash
ls              # 查看当前目录
ls -l           # 查看详细信息
ls -a           # 显示隐藏文件
ls -h           # 以易读形式显示文件大小
ls -lah         # 常见组合用法
```

`ls -l` 的输出中，第一列表示文件类型和权限：

- `d`：目录。
- `-`：普通文件。
- `l`：软链接。
- `p`：管道文件。
- `s`：套接字文件。
- `c`：字符设备。
- `b`：块设备。

权限部分通常由三组组成，分别对应文件所有者、所属组和其他用户。`r` 表示可读，`w` 表示可写，`x` 表示可执行，`-` 表示没有对应权限。

#### `cd`、`pwd`：切换和查看目录

```bash
pwd             # 显示当前目录
cd /etc         # 使用绝对路径切换
cd ..           # 返回上一级目录
cd .            # 当前目录
cd ~            # 进入当前用户家目录
cd -            # 返回上一次所在目录
```

绝对路径从根目录 `/` 开始，例如 `/etc/ssh`；相对路径以当前目录为参照，例如 `../logs`。

Linux 中，`root` 用户的家目录通常是 `/root`，普通用户的家目录通常位于 `/home` 下。

#### `mkdir`：创建目录

```bash
mkdir demo
mkdir dir1 dir2
mkdir -p project/src/main
```

`-p` 可以在上级目录不存在时一并创建多级目录。

#### `touch`：创建文件或更新时间戳

```bash
touch a.txt

touch a.txt b.txt c.txt
```

如果文件已经存在，`touch` 通常会更新文件的访问时间和修改时间，而不会清空文件内容。

#### `cp`：复制文件或目录

```bash
cp a.txt b.txt
cp a.txt /tmp/
cp -r source_dir target_dir
```

复制目录时通常需要使用 `-r`（递归）选项。执行复制前要注意目标路径是否已经存在，以免覆盖文件。

#### `mv`：移动或重命名

```bash
mv old.txt new.txt
mv file.txt /tmp/
mv old_dir new_dir
```

`mv` 既可以移动文件，也可以用于文件或目录重命名。

#### `rm`：删除文件或目录

```bash
rm file.txt
rm -r directory
rm -f file.txt
rm -rf directory
```

`-r` 表示递归删除目录，`-f` 表示强制删除并减少提示。`rm` 不会像图形界面回收站那样自动保留副本，因此操作前应反复确认路径。

> 特别注意：不要随意执行 `rm -rf /` 或包含变量、通配符但未经检查的删除命令。生产环境中应尽量避免直接使用高权限执行破坏性操作。

#### `find`：查找文件

```bash
find . -name '*.cpp'
find /var/log -type f -name '*.log'
find . -type d -name 'build'
```

常用类型参数：

- `-type f`：只查找普通文件。
- `-type d`：只查找目录。
- `-name`：按名称匹配。

通配符：

- `*`：匹配零个或多个任意字符。
- `?`：匹配一个任意字符。

### 2.3 文本文件处理

#### `cat`、`less` 和 `more`

```bash
cat demo.txt
cat -n demo.txt
less demo.txt
more demo.txt
```

`cat` 适合查看较短文件；`less` 更适合查看较长内容，常用操作包括：

- 空格：向下翻页。
- 回车：向下移动一行。
- `/关键字`：搜索关键字。
- `n`：查找下一个匹配项。
- `N`：查找上一个匹配项。
- `q`：退出。

#### `head` 和 `tail`

```bash
head -3 demo.txt
tail -5 /etc/services
```

不指定参数时，`head` 和 `tail` 通常分别显示前 10 行和后 10 行。

`tail -f` 常用于实时查看日志：

```bash
tail -f application.log
```

#### `grep`：查找文本内容

```bash
grep 'error' application.log
grep -n 'error' application.log
grep -i 'error' application.log
grep -w 'error' application.log
grep -v 'debug' application.log
```

常用参数：

- `-n`：显示匹配行的行号。
- `-w`：匹配完整单词。
- `-i`：忽略大小写。
- `-v`：显示不匹配的行。

`grep` 经常和管道组合使用：

```bash
ps -ef | grep nginx
ls -l | grep '.cpp'
```

也可以使用正则表达式：

```bash
grep -n '^w' hello.txt   # 查找以 w 开头的行
grep -n 'w$' hello.txt   # 查找以 w 结尾的行
```

#### `sed`：流式文本处理

`sed` 可以对文本进行筛选、插入、删除和替换。默认情况下，命令只输出处理结果，不会直接修改源文件；使用 `-i` 才会修改文件。

```bash
sed -n '3p' hello.txt       # 输出第 3 行
sed -n '3,5p' hello.txt     # 输出第 3～5 行
sed '3d' hello.txt          # 删除第 3 行的输出结果
sed '2a 88888888' hello.txt # 在第 2 行后追加内容
sed '3i 88888888' hello.txt # 在第 3 行前插入内容
```

字符串替换：

```bash
sed 's/nice/888/' hello.txt       # 每行替换第一个匹配项
sed 's/nice/888/g' hello.txt      # 每行替换所有匹配项
sed 's/nice/888/gi' hello.txt     # 忽略大小写并替换全部匹配项
sed -i 's/old/new/g' hello.txt    # 直接修改源文件
```

修改文件前建议先备份，或先不加 `-i` 检查输出结果。

#### `awk`：按列处理文本

`awk` 适合按照分隔符处理文本中的列。默认分隔符通常是空白字符，也可以通过 `-F` 指定。

```bash
awk -F: '{print $1}' /etc/passwd
awk -F: 'NR==53 {print $1}' /etc/passwd
```

其中，`$1` 表示第一列，`NR` 表示当前记录的行号。

### 2.4 管道、重定向和基础工具

管道符 `|` 会把前一个命令的标准输出交给后一个命令作为输入：

```bash
ps -ef | grep ssh
```

重定向用于将输出写入文件：

```bash
echo 'hello' > output.txt    # 覆盖写入
echo 'world' >> output.txt   # 追加写入
```

其他常用命令：

```bash
clear                 # 清屏
date '+%Y-%m-%d'       # 显示日期
cal 2026              # 查看指定年份日历
```

---

## 三、系统、用户、进程与网络命令

### 3.1 用户管理

```bash
useradd devuser       # 创建用户
passwd devuser        # 设置或修改密码
userdel devuser       # 删除用户
userdel -r devuser    # 删除用户及其家目录
su - devuser          # 切换用户并加载目标用户环境
exit                  # 退出当前 Shell 或用户会话
```

执行用户管理操作通常需要管理员权限。删除用户前，应确认该用户是否仍然拥有重要文件或正在运行的服务。

### 3.2 关机和重启

```bash
poweroff
reboot
shutdown -h now      # 立即关机
shutdown -r now      # 立即重启
shutdown -h 10       # 约 10 分钟后关机
```

服务器环境中执行关机或重启前，应确认是否会影响其他用户和业务服务。

### 3.3 磁盘和进程

```bash
df -h                # 查看文件系统磁盘使用情况
du -sh .             # 查看当前目录总占用空间
ps -ef               # 查看进程详细信息
ps -ef | grep nginx  # 查找指定进程
```

终止进程：

```bash
kill PID
kill -9 PID
```

通常应先使用普通的 `kill`，让进程有机会进行清理；`kill -9` 会发送强制终止信号，只有在普通终止方式无效且确认后果时才考虑使用。

在终端中，`Ctrl + C` 通常用于中断当前前台程序。

### 3.4 网络命令

```bash
ping -c 4 192.168.1.1
ping -c 4 example.com
ifconfig
netstat
```

`ping` 可用于初步测试网络连通性，但不能单独证明目标服务端口一定可用。`ifconfig` 和 `netstat` 在部分新发行版中可能需要额外安装，或被 `ip`、`ss` 等工具替代。

---

## 四、打包、解包和压缩

Linux 中经常使用 `tar` 管理文件归档。常用参数如下：

- `-c`：创建归档。
- `-x`：解开归档。
- `-v`：显示处理过程。
- `-f`：指定归档文件名，通常放在参数末尾。
- `-z`：使用 gzip 压缩或解压。
- `-j`：使用 bzip2 压缩或解压。
- `-C`：切换到指定目录后执行操作。

示例：

```bash
tar -cvf cplus.tar 111.cpp 222.cpp 333.cpp
tar -cvf java.tar '*.java'
tar -xvf cplus.tar
tar -xvf cplus.tar -C ../banana

tar -zcvf cplus.tar.gz *.cpp
tar -zxvf cplus.tar.gz -C ../banana
```

现代 `tar` 通常可以根据文件扩展名或参数自动识别压缩格式，但在学习和脚本中明确写出参数有助于理解命令含义。

---

## 五、Vim 基础使用

Vim 是 Linux 环境中常见的文本编辑器。理解它的模式切换是使用 Vim 的关键。

### 5.1 普通模式

打开文件后，Vim 通常处于普通模式。常用操作：

| 操作 | 功能 |
| --- | --- |
| `h`、`j`、`k`、`l` | 左、下、上、右移动 |
| `Ctrl + f` | 向下翻页 |
| `Ctrl + b` | 向上翻页 |
| `0` | 跳到行首 |
| `$` | 跳到行尾 |
| `gg` | 跳到文件开头 |
| `G` | 跳到文件末尾 |
| `x` | 删除一个字符 |
| `dw` | 删除一个单词 |
| `dd` | 删除一行 |
| `yw` | 复制一个单词 |
| `yy` | 复制一行 |
| `p` | 粘贴 |
| `u` | 撤销 |
| `Ctrl + r` | 重做 |
| `/关键字` | 搜索关键字 |
| `n` / `N` | 查找下一个 / 上一个 |

许多操作支持数字前缀，例如：

```text
3x      删除 3 个字符
3dd     删除 3 行
3dw     删除 3 个单词
```

### 5.2 插入模式

在普通模式下，可以通过以下命令进入插入模式：

- `i`：在光标前插入。
- `a`：在光标后插入。
- `o`：在当前行后新建一行并插入。
- `O`：在当前行前新建一行并插入。
- `I`：在行首插入。
- `A`：在行尾插入。

按 `Esc` 可以返回普通模式。

### 5.3 命令模式

在普通模式下按 `:` 进入命令模式：

```vim
:q       " 未修改时退出
:wq      " 保存并退出
:q!      " 不保存并强制退出
:set nu  " 显示行号
:set nonu " 取消显示行号
:set hlsearch " 开启搜索高亮
:nohlsearch  " 取消当前搜索高亮
:!ls     " 执行外部命令
```

替换操作：

```vim
:s/old/new/       " 当前行替换第一个匹配项
:s/old/new/g      " 当前行替换全部匹配项
:s/old/new/gi     " 当前行忽略大小写并全部替换
:%s/old/new/gi    " 全文忽略大小写并全部替换
```

Vim 自带交互式教程，可以使用以下命令学习：

```bash
vimtutor
```

---

## 六、Shell 脚本入门

Shell 脚本是由 Shell 语法和 Linux 命令组成的脚本文件，可以将多个操作组织起来，完成自动化任务。CentOS 等系统中常见的 Shell 是 Bash。

### 6.1 变量

Shell 变量的基本规则：

- 变量名和等号之间不能有空格。
- 变量名通常由字母、数字和下划线组成。
- 变量名不能以数字开头。
- 使用变量时，需要在变量名前加 `$`。
- 使用 `unset` 删除变量。

```bash
name='Banxia'
echo "$name"
unset name
```

建议在使用变量时加上双引号，避免变量内容包含空格时产生意外的参数拆分。

### 6.2 `if` 条件语句

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

示例中的年龄区间只是演示条件分支语法，实际分类标准应根据具体业务需求确定。

### 6.3 `while` 循环

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

### 6.4 `for` 循环

```bash
#!/bin/bash

sum=0

for (( i = 1; i <= 100; i++ )); do
    (( sum += i ))
done

echo "1+2+...+100 = $sum"
```

运行脚本前，通常需要赋予执行权限：

```bash
chmod +x demo.sh
./demo.sh
```

---

## 七、Linux 下的软件安装

### 7.1 使用包管理器安装

在基于 RPM 的发行版中，可以使用 `yum` 管理软件包：

```bash
yum install 软件包名
yum -y install 软件包名
yum remove 软件包名
yum -y remove 软件包名
yum update 软件包名
yum list installed
yum info 软件包名
yum provides 命令名
```

`-y` 会自动对交互式确认选择 `yes`，在生产环境使用前应确认命令的影响。

不同发行版可能使用不同的包管理器，例如 Debian/Ubuntu 常用 `apt`，因此不能把 `yum` 命令直接套用到所有 Linux 系统。

### 7.2 从源代码安装

从源代码安装软件时，常见流程如下：

1. 下载源代码。
2. 解包和解压。
3. 检查和配置编译环境。
4. 编译。
5. 安装。

例如：

```bash
wget https://www.memcached.org/files/memcached-1.6.45.tar.gz
tar -zxvf memcached-1.6.45.tar.gz
cd memcached-1.6.45
./configure
make
sudo make install
```

具体构建步骤取决于项目使用的构建系统，实际操作前应优先阅读项目提供的 README 或安装文档。

---

## 八、C/C++ 源代码到可执行程序

以传统 GCC 编译流程为例，源代码通常要经历预处理、编译、汇编和链接四个阶段。

### 8.1 预处理

处理头文件包含、宏展开和条件编译等内容：

```bash
gcc -E test.cpp -o test.ii
```

### 8.2 编译

将预处理结果转换为汇编代码：

```bash
gcc -S test.ii -o test.s
```

### 8.3 汇编

将汇编代码转换为目标文件：

```bash
gcc -c test.s -o test.o
```

### 8.4 链接

将目标文件和需要的库链接为可执行文件：

```bash
g++ test.o -o test
```

对于 C++ 程序，使用 `g++` 进行链接通常更直接，因为它会自动处理 C++ 标准库的链接。也可以使用 `gcc`，但需要根据程序情况显式链接相应的 C++ 库。

完整流程可以概括为：

```text
源代码 → 预处理文件 → 汇编代码 → 目标文件 → 可执行程序
```

---

## 九、Makefile 基础

当项目中的源文件较多时，逐个手动编译会非常繁琐。`make` 是一种自动化构建工具，它根据 Makefile 中定义的规则，决定哪些文件需要编译、哪些目标需要重新生成。

Makefile 通常包含目标、依赖和命令：

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

使用：

```bash
make
make clean
```

Makefile 的主要优点是：

- 自动处理文件依赖关系。
- 只重新编译发生变化的目标。
- 将复杂的构建命令集中管理。
- 方便团队协作和重复构建。

注意：Makefile 中的命令行通常必须使用 **Tab** 开头，而不是普通空格。

---

## 十、硬链接和软链接

Linux 中可以通过链接为同一个文件提供多个访问路径。

### 10.1 硬链接

```bash
ln source.txt hardlink.txt
```

硬链接与原文件指向同一个 inode，多个目录项共同指向同一份文件数据。删除其中一个名称，通常不会影响其他硬链接对文件内容的访问，只要仍有链接存在。

### 10.2 软链接

```bash
ln -s source.txt softlink.txt
```

软链接是一个独立的文件，内部保存目标路径。访问软链接时，系统会继续访问它指向的目标。

### 10.3 主要区别

1. 硬链接和原文件共享同一个 inode；软链接本身有独立的 inode。
2. 硬链接通常不能跨文件系统；软链接可以指向其他文件系统中的路径。
3. 硬链接通常不能直接链接目录；软链接可以指向目录。
4. 目标文件被删除后，软链接可能变成悬空链接；硬链接只要仍有其他链接存在，数据通常仍然可访问。

查看链接信息：

```bash
ls -li source.txt hardlink.txt softlink.txt
```

---

## 十一、学习总结

Linux 学习不能只停留在记忆命令，更重要的是理解命令之间如何组合，以及命令对文件、进程和系统状态产生的影响。

建议按照以下顺序练习：

1. 熟悉目录切换、文件创建、复制、移动和删除。
2. 使用 `cat`、`less`、`grep`、`sed` 和 `awk` 处理文本。
3. 掌握管道和重定向，尝试把多个命令组合起来。
4. 使用 `ps`、`df`、`du` 和网络工具观察系统状态。
5. 用 Vim 修改配置文件和编写代码。
6. 编写简单的 Shell 脚本完成重复任务。
7. 理解 C/C++ 的编译、链接过程，并使用 Makefile 管理项目。

熟悉这些基础工具后，后续学习 Linux 服务部署、网络编程、进程间通信、性能分析和自动化运维都会更加顺畅。
