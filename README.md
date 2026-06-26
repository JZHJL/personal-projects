# 🎯 高尔顿钉板模拟器 / Galton Board Simulator

一个用 Python 实现的高尔顿钉板（Galton Board / Bean Machine）模拟程序，用于直观演示**二项分布**的形成过程。

A Python simulation of the Galton Board (Bean Machine) that visually demonstrates how the **binomial distribution** emerges from random processes.

---

## 📖 原理 / How It Works

高尔顿钉板是一个经典的统计实验装置。

The Galton Board is a classic statistics demonstration device.

每一排钉子，小球随机向左 (0) 或向右 (1) 弹跳。
Starting from 1, after adding `muma` random 0s or 1s, final position = 1 + number of right bounces.

---

## 💻 运行环境 / Requirements

- **Python**: 3.12.10
- **依赖**: 无（纯标准库）
- **Dependencies**: None (standard library only)

---

## 🚀 使用方法 / Usage

```bash
python3 main.py
```

程序会提示输入两个数字：

| 参数 | 含义 |
|---|---|
| `muma` | 钉板层数 / 每次弹跳次数 |
| `mums` | 重复试验次数 |

### 示例

输入:
```
:10
:100000
```

---

## 📊 输出说明

- `<===>` 每轮开始
- `----` 每次弹跳
- `~~~` 当前累积值
- 最终输出 1~5 各值出现的次数

> ⚠️ 当前仅统计 1~5，层数较多时更高值不会计入。

---

## 📂 文件结构

```
personal-projects/
├── main.py
└── README.md
```
