# Twitter Monitor Trade Bot

## 项目概述

这是一个基于Twitter监控的加密货币自动交易机器人，主要功能是监控指定的Twitter账号（KOL）的推文，自动识别其中的加密货币合约地址，并根据策略自动执行交易操作。

## 核心工作思想

项目的核心工作流程如下：

1. **Twitter监控**: 定时监控关注列表中KOL的推文更新
2. **合约地址提取**: 从推文中使用正则表达式提取Solana代币合约地址（CA）
3. **代币信息获取**: 通过GMGN等第三方API获取代币的详细信息和价格数据
4. **自动交易**: 根据预设策略使用Jupiter协议自动执行买入/卖出操作
5. **消息推送**: 通过Telegram机器人向用户推送交易信息和KOL动态

## 技术栈

### 核心依赖
- **Python**: 主要编程语言
- **twikit**: Twitter API操作库，用于获取推文和用户信息
- **mongoengine**: MongoDB ORM，用于数据存储
- **jupiter-python-sdk**: Jupiter协议SDK，用于Solana链上交易
- **telegram**: Telegram机器人API
- **requests**: HTTP请求处理
- **colorama**: 控制台彩色输出
- **async_retrying**: 异步重试机制

### 技术架构
- **数据库**: MongoDB (用于存储用户信息、推文、代币信息、交易订单)
- **区块链**: Solana (主要交易链)
- **交易协议**: Jupiter (DEX聚合器)
- **消息推送**: Telegram Bot
- **数据源**: Twitter API、GMGN API、DexScreen API

## 项目结构

```
tw_monitor_tradebot/
├── main.py                    # 主入口文件
├── kol_tw_monitor_bot.py      # KOL Twitter监控主程序
├── monitor_ca_bot.py          # 合约地址监控和交易执行
├── config.py                  # 配置文件
├── constant.py                # 常量定义
├── requirement.txt            # 依赖包列表
├── 思路                       # 项目思路文档
├── mangodb_ops/               # MongoDB操作模块
│   ├── connect.py            # 数据库连接
│   ├── orm_ops.py            # ORM操作
│   └── ormmapper.py          # 数据模型定义
├── telegrambot/              # Telegram机器人模块
│   ├── telegram_bot_alter.py # 消息推送功能
│   └── config.py             # Telegram配置
├── soltradebot/              # Solana交易模块
│   └── tradebot.py           # 交易执行逻辑
├── binance/                  # Binance交易相关
│   └── token_trade.py        # 代币交易
├── buystrage/                # 购买策略模块
│   ├── new_pairs.py          # 新币对策略
│   ├── new_pump.py           # 新热门代币策略
│   └── twitter_strage.py     # Twitter策略评分
└── utils/                    # 工具模块
    ├── gmgn.py               # GMGN API交互
    ├── regex_utils.py        # 正则表达式工具
    ├── time_utils.py         # 时间工具
    ├── tw_login.py           # Twitter登录
    └── warp_utils.py         # 装饰器工具
```

## 核心功能模块

### 1. Twitter监控 (`kol_tw_monitor_bot.py`)
- 监控指定KOL账号的推文更新
- 实时检测新推文并存储到数据库
- 向关注该KOL的用户推送Telegram消息

### 2. 合约地址监控 (`monitor_ca_bot.py`)
- 从历史推文中提取合约地址
- 获取代币信息并评估投资价值
- 自动执行买入操作并设置卖出订单

### 3. 交易执行 (`soltradebot/tradebot.py`)
- 基于Jupiter协议的Solana代币交易
- 支持市价交易和限价交易
- 集成多种价格查询API

### 4. 数据存储 (`mangodb_ops/`)
- 用户信息管理
- 推文历史存储
- 代币信息缓存
- 交易订单记录

### 5. 消息推送 (`telegrambot/`)
- Telegram机器人集成
- 实时推送KOL动态
- 交易执行结果通知

## 数据模型

### 主要数据表
- `user_info`: 用户信息（Telegram ID、钱包信息、关注的KOL）
- `twitter_user`: Twitter用户信息（用户ID、昵称、粉丝数等）
- `tweet`: 推文信息（推文ID、内容、互动数据等）
- `token_info`: 代币信息（地址、价格、流动性等）
- `orders`: 交易订单（买入/卖出记录）
- `wallet`: 钱包信息（私钥、公钥等）

## 安装和使用

### 环境要求
- Python 3.8+
- MongoDB
- Solana钱包
- Twitter开发者账号
- Telegram Bot Token

### 安装依赖
```bash
pip install -r requirement.txt
```

### 配置文件
编辑 `config.py` 设置：
- 代理URL
- Twitter登录凭据
- Telegram Bot Token
- MongoDB连接信息

### 运行程序
```bash
# 启动KOL监控
python kol_tw_monitor_bot.py

# 启动合约地址监控
python monitor_ca_bot.py
```

## 风险提示

⚠️ **重要提醒**: 
- 本项目仅供学习和研究使用
- 加密货币交易存在极高风险，可能导致资金损失
- 自动交易策略需要充分测试和风险控制
- 请确保遵守相关法律法规和平台使用条款

## 注意事项

1. **Twitter API限制**: 注意Twitter API的调用频率限制
2. **资金安全**: 妥善保管私钥，建议使用小额资金测试
3. **网络稳定**: 确保网络连接稳定，避免交易执行失败
4. **监控策略**: 合理设置监控频率，避免过度频繁的API调用

## 开发者信息

本项目为个人研究项目，如有问题或建议，欢迎提出Issues或Pull Requests。