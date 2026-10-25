+++
date = '2026-09-20T16:30:00+08:00'
title = 'C++11 新特性学习笔记：从 auto 到智能指针'
summary = '系统整理 C++11 中常用的新特性，包括 auto、nullptr、Lambda、范围 for、统一初始化、智能指针与类型别名，并结合代码示例总结使用注意事项。'
tags = ['C++', 'C++11', '编程语言', '学习笔记']
categories = ['C++ 学习']
draft = false
+++

C++11 是 C++ 标准发展过程中的重要版本。它不仅增加了许多语法特性，还引入了更现代的编程思想，例如自动类型推导、Lambda 表达式、RAII 和智能指针等。

本文根据学习过程中的笔记进行整理，重点介绍日常开发中比较常用的特性，并通过示例说明它们的基本用法与注意事项。

> 说明：本文主要面向 C++ 初学者。示例默认使用 `std` 命名空间中的类型，实际项目中建议显式使用 `std::`，避免命名污染。

## 一、`auto`：自动类型推导

### 1.1 基本用法

`auto` 是一个占位符，编译器会根据初始化表达式在编译期间推导变量类型。因此，使用 `auto` 声明变量时必须同时进行初始化。

```cpp
#include <iostream>
#include <typeinfo>
using namespace std;

int main()
{
    auto a = 10;          // int
    auto b = 3.14;        // double
    auto c = 'c';         // char
    auto d = "hello";     // const char*

    cout << a << endl;
    cout << b << endl;
    cout << c << endl;
    cout << d << endl;
    return 0;
}
```

### 1.2 与指针、引用配合使用

```cpp
int x = 10;

auto p1 = &x;    // int*
auto* p2 = &x;   // int*
auto& p3 = x;    // int&

p3 = 20;         // 修改 x
```

需要注意：`auto` 会遵循类型推导规则。普通的 `auto` 推导通常会忽略顶层 `const` 和引用属性；如果希望保留引用，应明确写出 `auto&` 或 `const auto&`。

### 1.3 常见限制

- `auto` 变量必须初始化。
- 不能直接使用 `auto` 声明未初始化数组，例如 `auto arr[]`。
- C++11 中不能使用 `auto` 作为普通函数参数类型。
- 不能写成 `vector<auto>` 或 `Test<auto>` 来推导模板参数。
- 类的非静态数据成员不能直接声明为 `auto`。

### 1.4 常见应用场景

`auto` 特别适合以下情况：

1. 类型名称较长时简化代码。
2. 使用容器迭代器时减少冗余。
3. 泛型代码中接收不同类型的返回值。

```cpp
vector<int> numbers = {10, 20, 30};

for (auto it = numbers.begin(); it != numbers.end(); ++it)
{
    cout << *it << endl;
}
```

## 二、`nullptr`：更安全的空指针

C++11 引入了 `nullptr`，用于表示空指针。传统的 `NULL` 通常是整数常量 `0` 或相关宏，在函数重载时可能产生歧义。

```cpp
void test(int value)
{
    cout << "int overload" << endl;
}

void test(char* value)
{
    cout << "pointer overload" << endl;
}

int main()
{
    test(0);        // 匹配 int
    test(NULL);     // 通常匹配 int，具体表现与 NULL 定义有关
    test(nullptr);  // 匹配 char*
}
```

推荐在现代 C++ 代码中使用 `nullptr`，而不是使用 `0` 或 `NULL` 表示空指针。

```cpp
int* ptr = nullptr;

if (ptr != nullptr)
{
    cout << *ptr << endl;
}
```

空指针不能被解引用。使用前应确认指针指向有效对象。

## 三、Lambda 表达式

Lambda 表达式也称为匿名函数，可以在需要函数对象的地方直接编写逻辑，常用于算法、回调和容器遍历。

### 3.1 基本结构

```cpp
[capture](parameters) mutable -> return_type
{
    // 函数体
}(arguments);
```

其中：

- `capture`：捕获外部变量的方式。
- `parameters`：参数列表。
- `mutable`：允许修改按值捕获的副本。
- `return_type`：返回值类型，通常可以省略。
- `arguments`：立即调用时传入的参数。

### 3.2 基本示例

```cpp
// 无参数、无返回值
[]()
{
    cout << "Hello Lambda" << endl;
}();

// 带参数并返回结果
auto result = [](int a, int b)
{
    return a + b;
}(3, 5);
```

### 3.3 捕获列表

| 写法 | 含义 |
| --- | --- |
| `[]` | 不捕获局部变量 |
| `[x]` | 按值捕获 x |
| `[&x]` | 按引用捕获 x |
| `[=]` | 按值捕获使用到的外部变量 |
| `[&]` | 按引用捕获使用到的外部变量 |
| `[this]` | 捕获当前对象的 this 指针 |

```cpp
int x = 10;
int y = 20;

[x, &y]()
{
    // x 是副本，不能直接修改
    // x = 100;

    // y 通过引用捕获，可以修改
    y = 200;
}();
```

### 3.4 `mutable`

按值捕获的变量默认不能在 Lambda 的 `const` 调用运算符中修改。使用 `mutable` 可以修改 Lambda 内部保存的副本，但不会影响外部原变量。

```cpp
int n = 0;

auto counter = [n]() mutable
{
    return ++n;
};

cout << counter() << endl; // 1
cout << counter() << endl; // 2
cout << n << endl;         // 0
```

需要注意，Lambda 内部的 `n` 是捕获变量的副本，并不是外部的 `n`。

## 四、范围 `for` 循环

C++11 提供了范围 `for` 循环，可以直接遍历数组、容器、字符串等支持 `begin()` 和 `end()` 的对象。

```cpp
vector<string> languages = {"C++", "Python", "JavaScript"};

for (const auto& language : languages)
{
    cout << language << endl;
}
```

常见写法：

- `for (auto value : container)`：复制元素。
- `for (auto& value : container)`：引用元素，可以修改。
- `for (const auto& value : container)`：只读引用，避免拷贝，通常更推荐。

遍历 `map` 时，元素通常是 `pair<const Key, T>`：

```cpp
map<int, string> users = {
    {1, "Alice"},
    {2, "Bob"}
};

for (const auto& item : users)
{
    cout << item.first << ": " << item.second << endl;
}
```

## 五、统一初始化与初始化列表

C++11 扩大了花括号初始化的使用范围，内置类型、数组、结构体、类和标准容器都可以使用统一的初始化形式。

```cpp
int a{10};
int b = {20};
int arr[] = {1, 2, 3};

vector<int> numbers{10, 20, 30};

struct Point
{
    int x;
    int y;
};

Point p{100, 200};
```

### 5.1 构造函数初始化列表

构造函数初始化列表可以直接初始化成员变量，尤其适用于 `const` 成员、引用成员和没有默认构造函数的对象成员。

```cpp
class Teacher
{
public:
    Teacher(int id, const string& name)
        : id_(id), name_(name)
    {
    }

private:
    int id_;
    string name_;
};
```

成员初始化的实际顺序由成员变量在类中的声明顺序决定，而不是由初始化列表中的书写顺序决定。因此，建议按照成员声明顺序编写初始化列表。

### 5.2 `explicit`

当构造函数只有一个参数时，可能发生隐式转换：

```cpp
class Date
{
public:
    Date(int year) : year_(year) {}

private:
    int year_;
};

Date date = 2026; // 允许隐式转换
```

如果不希望发生这种隐式转换，可以使用 `explicit`：

```cpp
explicit Date(int year) : year_(year) {}
```

此时应使用直接初始化：

```cpp
Date date(2026);
```

## 六、智能指针与 RAII

### 6.1 为什么需要智能指针

使用 `new` 动态申请内存后，如果忘记 `delete`，就可能造成内存泄漏。智能指针通过对象生命周期自动管理资源，是 RAII 思想的典型应用。

RAII 的核心思想是：在对象构造时获取资源，在对象析构时释放资源。资源不仅包括内存，也可以包括文件句柄、锁和网络连接等。

C++11 提供了三种主要的智能指针：

- `std::unique_ptr`：独占所有权。
- `std::shared_ptr`：共享所有权，使用引用计数管理对象。
- `std::weak_ptr`：不拥有对象，用于观察 `shared_ptr` 管理的对象，常用于解决循环引用。

`std::auto_ptr` 已经被弃用，不应在新代码中使用。

### 6.2 `unique_ptr`

同一时间只能有一个 `unique_ptr` 拥有某个对象，因此它不能被复制，只能通过移动转移所有权。

```cpp
#include <memory>

class MyTest
{
public:
    explicit MyTest(int value) : value_(value) {}
    int value_;
};

int main()
{
    auto ptr = std::unique_ptr<MyTest>(new MyTest(10));
    cout << ptr->value_ << endl;

    auto ptr2 = std::move(ptr); // 转移所有权
    // ptr 此时为空，ptr2 拥有对象
}
```

C++11 中没有 `std::make_unique`，它是 C++14 才加入的工具函数。因此，C++11 代码通常使用 `new` 初始化 `unique_ptr`，或者自行编写兼容的工厂函数。

不要让多个智能指针分别接管同一个裸指针：

```cpp
MyTest* raw = new MyTest(10);
std::unique_ptr<MyTest> p1(raw);
std::unique_ptr<MyTest> p2(raw); // 错误：可能导致重复释放
```

### 6.3 `shared_ptr`

`shared_ptr` 允许多个智能指针共同拥有一个对象。当最后一个拥有者被销毁时，对象才会被释放。

```cpp
auto p1 = std::make_shared<MyTest>(10);
auto p2 = p1;

auto count = p1.use_count(); // 2
cout << count << endl;

p2.reset();                  // p2 放弃所有权
cout << p1.use_count() << endl; // 1
```

常用成员函数：

- `use_count()`：查看当前共享所有者数量，主要用于观察和调试，不建议把它作为业务逻辑判断依据。
- `reset()`：释放当前所有权，或者让指针管理新的对象。
- `get()`：获取内部裸指针，但不会转移所有权，也不能通过返回值手动 `delete`。

通常更推荐使用 `std::make_shared<T>()` 创建对象，因为它表达清晰，并且通常可以减少一次内存分配。

### 6.4 自定义删除器

智能指针默认使用 `delete` 释放对象。如果资源需要特殊的释放方式，可以传入自定义删除器，例如函数对象或 Lambda。

```cpp
std::shared_ptr<MyTest> ptr(
    new MyTest(100),
    [](MyTest* value)
    {
        cout << "释放对象前执行操作" << endl;
        delete value;
    }
);
```

### 6.5 `weak_ptr` 与循环引用

如果两个对象通过 `shared_ptr` 互相持有，就可能形成循环引用。即使外部已经没有指针指向它们，引用计数仍然不为零，析构函数也不会被调用。

解决方式是将其中一条不需要所有权的关系改为 `weak_ptr`：

```cpp
class B;

class A
{
public:
    std::shared_ptr<B> b;
};

class B
{
public:
    std::weak_ptr<A> a;
};
```

使用 `weak_ptr` 访问对象前，需要通过 `lock()` 获取临时的 `shared_ptr`，并判断对象是否仍然存在：

```cpp
if (auto owner = weak.lock())
{
    // owner 有效，可以安全访问对象
}
```

### 6.6 智能指针使用建议

1. 优先使用 RAII 和标准智能指针管理动态资源。
2. 不要让多个独立的智能指针接管同一个裸指针。
3. 明确所有权：独占关系优先考虑 `unique_ptr`，确实需要共享时再使用 `shared_ptr`。
4. 不要随意保存由 `get()` 返回的裸指针并延长其生命周期。
5. 注意 `shared_ptr` 的循环引用问题，必要时使用 `weak_ptr`。

## 七、类型别名：`typedef` 与 `using`

类型别名不会创建新的类型，只是为已有类型提供另一个名称。

```cpp
typedef int MyInt;
using MyChar = char;

MyInt number = 10;
MyChar ch = 'A';
```

相比 `typedef`，`using` 的语法更加直观，并且在模板别名中更方便：

```cpp
using UserMap = map<string, vector<int>>;

UserMap users = {
    {"first", {1, 2, 3}},
    {"second", {4, 5, 6}}
};
```

## 八、总结

本文整理了 C++11 中最常见的一组语言和库特性：

- `auto`：减少冗长类型声明。
- `nullptr`：明确表达空指针语义。
- Lambda：方便地编写匿名函数和回调逻辑。
- 范围 `for`：简化容器和数组遍历。
- 统一初始化：提供更加统一的对象初始化方式。
- 初始化列表：直接初始化类成员，适合处理常量和引用成员。
- 智能指针：通过 RAII 降低手动内存管理的风险。
- 类型别名：提高复杂类型代码的可读性。

学习 C++11 时，不应该只记住语法，还需要理解它背后的设计思想：**减少重复代码、明确资源所有权、降低手动管理带来的错误，并让代码更容易阅读和维护。**

在实际开发中，建议结合编译器的 `-std=c++11` 选项逐个编译和运行示例，观察代码行为，再根据项目需求选择合适的特性。
