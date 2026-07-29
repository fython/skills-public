# 转换配方与高风险模式

在源公式含绘图、条件选股、未来函数、动态周期、财务数据或外部引用时读取本文件。

## 目录

- [1. 输出语句拆解](#1-输出语句拆解)
- [2. 常用指标配方](#2-常用指标配方)
- [3. 绘图配方](#3-绘图配方)
- [4. 公式类型转换](#4-公式类型转换)
- [5. 高风险与不可转模式](#5-高风险与不可转模式)
- [6. 验证清单](#6-验证清单)

## 1. 输出语句拆解

不要直接把冒号换成等号。通达信输出同时承担“命名、计算、绘图”三件事。

```text
通达信：
DIF:EMA(CLOSE,12)-EMA(CLOSE,26),COLORWHITE;
```

```python
dif = ema(close(), 12) - ema(close(), 26)
plot("DIF", dif, color=Color.white)
```

`:=` 只赋值：

```text
TMP:=MA(CLOSE,20);
```

```python
tmp = sma(close(), 20)
```

`NODRAW` 保留计算但不绘图；若目标是让富途量化功能读取该变量，先查客户端对 `output_parameter` 的要求，再明确声明输出。

## 2. 常用指标配方

### 2.1 MACD

通达信：

```text
DIF:EMA(CLOSE,SHORT)-EMA(CLOSE,LONG),COLORWHITE;
DEA:EMA(DIF,MID),COLORYELLOW;
MACD:(DIF-DEA)*2,COLORSTICK;
```

富途：

```python
short = input_parameter("短周期", 12)
long = input_parameter("长周期", 26)
mid = input_parameter("信号周期", 9)

dif = ema(close(), short) - ema(close(), long)
dea = ema(dif, mid)
macd = (dif - dea) * 2

plot("DIF", dif, color=Color.white)
plot("DEA", dea, color=Color.yellow)
plot("MACD", macd, color=iff(macd >= 0, Color.red, Color.green), style=Line.histogram)
```

保留通达信国内常见的柱体乘 2 口径。

### 2.2 KDJ

```text
RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
K:SMA(RSV,M1,1);
D:SMA(K,M2,1);
J:3*K-2*D;
```

```python
denom = hhv(high(), n) - llv(low(), n)
rsv = (close() - llv(low(), n)) / denom * 100
k = smma(rsv, m1, 1)
d = smma(k, m2, 1)
j = 3 * k - 2 * d
plot("K", k, color=Color.white)
plot("D", d, color=Color.yellow)
plot("J", j, color=Color.magenta)
```

分母为 0 时的空值/无穷处理可能不同，需用横盘样本核验。

### 2.3 RSI（通达信常见写法）

```text
LC:=REF(CLOSE,1);
RSI1:SMA(MAX(CLOSE-LC,0),N,1)/SMA(ABS(CLOSE-LC),N,1)*100;
```

```python
lc = ref(close(), 1)
up = smma(max(close() - lc, 0), n, 1)
total = smma(abs(close() - lc), n, 1)
rsi1 = up / total * 100
plot("RSI1", rsi1)
```

### 2.4 BOLL

通达信的 `STD` 是样本标准差，必须映射到富途 `std`，不要套用 Pine 默认总体标准差的规则：

```python
mid = sma(close(), n)
upper = mid + p * std(close(), n)
lower = mid - p * std(close(), n)
```

若源公式写 `STDP`，才改用 `stdp`。

### 2.5 ATR

通达信公式可能写 `MA(TR,N)`、`SMA(TR,N,1)` 或其他平滑方式。逐字保留：

```python
atr_ma = sma(tr(), n)          # MA(TR,N)
atr_wilder = smma(tr(), n, 1) # SMA(TR,N,1)
```

不要因为指标名叫 ATR 就擅自统一为 Wilder 口径。

## 3. 绘图配方

### 3.1 条件断线

```text
UP:IF(CLOSE>MA(CLOSE,20),CLOSE,DRAWNULL),COLORRED;
```

```python
import math

ma20 = sma(close(), 20)
up = iff(close() > ma20, close(), math.nan)
plot("UP", up, color=Color.red)
```

不能用 0 替代 `DRAWNULL`，否则图上会出现落到零轴的线。

### 3.2 条件柱线

```text
STICKLINE(CLOSE>=OPEN,CLOSE,OPEN,0.8,1),COLORRED;
```

近似：

```python
up_bar = close() >= open()
plot_stickline("阳线实体", up_bar, open(), close(), width=1, empty=1, color=Color.red)
```

`width`、`empty` 的显示效果依客户端签名与缩放而异，必须实测。

### 3.3 图标与文字

```text
DRAWICON(CROSS(MA(C,5),MA(C,10)),LOW,1);
DRAWTEXT(CROSS(MA(C,5),MA(C,10)),LOW,'买');
```

```python
fast = sma(close(), 5)
slow = sma(close(), 10)
buy = cross(fast, slow, 1)
plot_icon("买入图标", buy, low(), Shape.arrowup, color=Color.red, size=2)
plot_text("买入文字", buy, low(), "买", color=Color.red, size=2)
```

通达信数字图标编号不是跨平台标准。按图标语义选择 `Shape`，并声明像素不等价。

### 3.4 双色填充

`DRAWBAND(A,RGB1,B,RGB2)` 可拆成两个条件填充：

```python
plot_fillcolor("A在上", a, b, cond=a >= b, color=Color.lired)
plot_fillcolor("B在上", a, b, cond=a < b, color=Color.ligreen)
```

若客户端拒绝常量/颜色广播，保留两条线并声明填充不可用。

## 4. 公式类型转换

### 4.1 条件选股公式

通达信条件选股只有一个布尔输出。富途指标不能自动等同于通达信全市场选股器。把条件保留为图表信号：

```text
XG:CROSS(MA(C,5),MA(C,20));
```

```python
signal = cross(sma(close(), 5), sma(close(), 20), 1)
plot_icon("XG", signal, low(), Shape.arrowup, color=Color.red, size=2)
```

如用户要在富途量化/提醒中引用，查当前客户端对指标输出变量的约束，再使用 `output_parameter`；不要声称已复现通达信选股扫描。

### 4.2 五彩 K 线

优先保留着色条件，必要时用 `plot_candlestick` 或多组 `plot_stickline` 近似。富途没有完全等价的原图 K 线全局染色时，明确说明会叠加绘制而非修改系统 K 线。

### 4.3 专家系统/交易公式

删除下单与账户状态，只保留可独立计算的入场/离场条件和图标。例如 `ENTERLONG:C;` 不能成为真实订单。若信号依赖 `AUTOFILTER`、持仓或成交回报状态，整体逻辑不可高保真转换。

## 5. 高风险与不可转模式

### 5.1 未来函数

- `BACKSET`、`BARSNEXT`、`XMA`：即使富途存在同名能力，也会使用未来信息或改写历史。转换代码旁写 `# 未来函数：信号会重绘`。
- `REFX/REFXV`：默认不可转，不用负 `ref` 猜测方向。
- `ZIG/PEAK/TROUGH`：拐点在后续行情到来后改变，不能用普通 `hhv/llv` 冒充。
- `DRAWLINE`：既有未来条件确认又有绘图对象状态，通常两层都不可转。

### 5.2 跨品种、跨周期、指标引用

以下形式不是简单变量引用：

```text
"SH000001$CLOSE"
"MACD.DIF"
TMP#WEEK
CALCSTOCKINDEX(...)
```

目标指标运行在当前图表数据上，通常无法请求另一品种、周期或公式输出。不要替换成当前 `close()`。如果用户能把被引用公式源码一并提供，可以先内联同周期计算；跨周期仍需声明不可等价。

### 5.3 财务与板块数据

`FINANCE(7)` 一类编号必须先查通达信字段含义，再查富途 `ffinance` 是否有同语义字段。即使名称相似，也要核对：

- 报告期与公告日对齐方式；
- 单季度、累计值、TTM 或年度值；
- 单位与币种；
- 历史数据是否按当时可得信息回放。

任何一项不明就列为待验证，不按编号硬映射。

### 5.4 成交量与复权

相同公式在两个客户端也可能因数据源而不同。尤其核对：

- A 股 `VOL` 是手还是股；
- `AMOUNT` 单位；
- 前复权/后复权/不复权；
- 停牌补值、集合竞价和盘中未完成 K 线；
- 上市初期不足 N 根时的均线初值。

## 6. 验证清单

编译前静态检查：

- 是否包含 9 个标准模块引入。
- `indicator()` 前两个参数是否按位置传递。
- 行情函数是否都加了括号。
- 是否把通达信相等 `=` 正确改为 `==`，且没有破坏 Python 赋值。
- Sequence 逻辑是否使用 `&/|/~` 并加括号。
- `IF` 是否改为 `iff`。
- `DRAWNULL` 是否使用 `math.nan` 且导入 `math`。
- `SMA` 是否映射为 `smma`。
- 每条冒号输出是否生成绘图或被明确标为 `NODRAW`。
- 是否遗漏颜色、线宽、图标、柱线或主副图信息。

数值对比至少覆盖：

1. 最新 50–100 根 K 线的一般区间。
2. 上市初期或数据不足 N 根的起始区间。
3. 分母为 0、缺失值、停牌或量为 0 的区间。
4. 交叉前后和相等边界。
5. 所有未来函数信号在新增 K 线后的历史变化。
