# Pine Script V6 → 富途：常用指标配方与习语

富途 `fta` 模块只内置了基础均线类函数，`ta.rsi` / `ta.macd` / `ta.bb` 等常用指标都必须用基础函数**组装**。本文件给出经过口径核对的标准配方，转换时直接套用，不要临场现推公式。

约定：`src`/`x` 均为 `Sequence`；`n`、`fast`、`slow`、`sig` 等为正整数参数。**所有配方均为代码片段**，假设脚本顶部已包含 9 个模块的标准引入块（见 [SKILL.md](../SKILL.md) 第三节骨架）。

---

## 1. 递归习语表（Pine `var`/自引用 → 富途向量化）

| Pine 写法 | 富途写法 | 说明 |
|---|---|---|
| `var float x = 0.0; x := x[1] + v` | `x = sum(v, 0)` | n=0 从首个非空值起累计 |
| `x := cond ? v : nz(x[1])` | `x = value_when(cond, v)` | 保持最近一次条件为真时的取值 |
| `x := cond ? nz(x[1]) + 1 : 0` | `x = bars_last_count(cond)` | 连续为真计数 |
| `x := math.max(v, nz(x[1]))`（有史以来最高） | `hhv(v, n)` 取足够大的窗口 n 近似 | 无固定窗口的"有史以来"聚合，富途中只能大窗口近似 |
| `y := m * x + (1 - m) * nz(y[1], x)` | `y = dma(x, m)` | 动态移动平均 |
| `y := (x + (n - 1) * nz(y[1], x)) / n` | `y = smma(x, n, 1)` | = `ta.rma`，Wilder 平滑 |
| `y := (m * x + (n - m) * y[1]) / n` | `y = smma(x, n, m)` | = 通达信 SMA(X,N,M) |
| `y := a * x + b * y[1]` | `y = tma(x, a, b)` | |
| 其他自定义递归 | 无通用方案 | 寻找代数等价的滚动窗口函数；找不到就向用户说明需简化 |

## 2. 常用指标配方

### 2.1 RSI — `ta.rsi(src, n)`

```python
delta = src.diff(1)
up = smma(max(delta, 0.0), n, 1)      # rma(上涨部分)
down = smma(max(-delta, 0.0), n, 1)   # rma(下跌部分)
rsi_val = 100 * up / (up + down)
```

口径说明：Pine 内部用 rma（= `smma(x, n, 1)`），用 `sma` 或 `ema` 替代会得到不同数值。

### 2.2 MACD — `ta.macd(src, fast, slow, sig)`（常用 12, 26, 9）

```python
dif = ema(src, fast) - ema(src, slow)
dea = ema(dif, sig)
hist = dif - dea
plot("DIF", dif, color=Color.white)
plot("DEA", dea, color=Color.yellow)
plot("MACD", hist * 2, color=iff(hist >= 0, Color.red, Color.green), style=Line.histogram)
```

- Pine 返回 `[macd, signal, hist]`，hist = macd − signal
- 国内软件习惯 MACD 柱 = `2 * (DIF - DEA)`，上面已按此绘制；要严格对齐 TradingView 则去掉 `* 2`
- 演示了**动态颜色**：`iff(hist >= 0, Color.red, Color.green)` 生成 `Sequence(Color)`

### 2.3 布林带 — `ta.bb(src, n, mult)`（常用 20, 2）

```python
mid = sma(src, n)
dev = stdp(src, n) * mult      # ⚠️ 必须 stdp（总体口径），Pine ta.stdev 默认 biased=true
upper = mid + dev
lower = mid - dev
plot("MID", mid, color=Color.yellow)
plot("UPPER", upper, color=Color.lired)
plot("LOWER", lower, color=Color.ligreen)
```

`ta.bbw`（带宽）= `(upper - lower) / mid`；`%b` = `(src - lower) / (upper - lower)`。

### 2.4 KDJ（Pine 无内置，但中文用户常需要）

```python
n, m1, m2 = 9, 3, 3
rsv = (close() - llv(low(), n)) / (hhv(high(), n) - llv(low(), n)) * 100
k = smma(rsv, m1, 1)     # K = SMA(RSV, M1, 1)（通达信定义）
d = smma(k, m2, 1)
j = 3 * k - 2 * d
plot("K", k, color=Color.white)
plot("D", d, color=Color.yellow)
plot("J", j, color=Color.magenta)
```

### 2.5 随机指标 — `ta.stoch(high, low, close, n)`

```python
stoch_val = (close() - llv(low(), n)) / (hhv(high(), n) - llv(low(), n)) * 100
# 平滑版（Full Stoch）：k = stoch_val.sma(sk)，d = k.sma(sd)
```

### 2.6 ATR — `ta.atr(n)`

```python
atr_val = tr().smma(n, 1)   # rma(tr)
```

富途 `tr()` 自动使用图表的最高/最低/前收，定义与 Pine `ta.tr(true)` 一致。

### 2.7 CCI — `ta.cci(src, n)`（常用典型价 hlc3，14）

```python
tp = (high() + low() + close()) / 3
cci_val = (tp - tp.sma(n)) / (0.015 * tp.avedev(n))   # ta.dev = avedev
```

### 2.8 威廉指标 — `ta.wpr(n)`

```python
wpr = (hhv(high(), n) - close()) / (hhv(high(), n) - llv(low(), n)) * -100
```

### 2.9 MFI — `ta.mfi(hlc3, n)`

```python
tp = (high() + low() + close()) / 3
mf = tp * vol()
d = tp.diff(1)
pos = sum(iff(d > 0, mf, 0.0), n)
neg = sum(iff(d < 0, mf, 0.0), n)
mfi_val = 100 - 100 / (1 + pos / neg)
```

### 2.10 DMI/ADX — `ta.dmi(diLen, adxSmoothing)`（常用 14, 14）

```python
up_move = high().diff(1)
down_move = -low().diff(1)
plus_dm = iff((up_move > down_move) & (up_move > 0), up_move, 0.0)
minus_dm = iff((down_move > up_move) & (down_move > 0), down_move, 0.0)
trur = smma(tr(), di_len, 1)
plus_di = 100 * smma(plus_dm, di_len, 1) / trur
minus_di = 100 * smma(minus_dm, di_len, 1) / trur
dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
adx_val = smma(dx, adx_len, 1)
plot("+DI", plus_di, color=Color.red)
plot("-DI", minus_di, color=Color.green)
plot("ADX", adx_val, color=Color.yellow)
```

Pine 内部全部用 rma 平滑，已对应为 `smma(x, n, 1)`。

### 2.11 HMA — `ta.hma(src, n)`

```python
def hma(x, n):
    return wma(2 * wma(x, n // 2) - wma(x, n), round(n ** 0.5))
```

富途环境支持 `def` 定义函数，可直接使用。

### 2.12 VWMA / SWMA

```python
vwma_val = (src * vol()).sma(n) / vol().sma(n)
swma_val = (src + 2 * src.ref(1) + 2 * src.ref(2) + src.ref(3)) / 6
```

### 2.13 线性回归 — `ta.linreg(src, n, offset)` 对照

富途提供两个回归函数（均带截距项）：
- `slope(x, n)`：回归斜率 β
- `forcast(x, n)`：**下一期**预测值 = 当前拟合值 + β

| Pine | 富途 |
|---|---|
| `ta.linreg(src, n, 0)`（当前 bar 拟合值） | `forcast(src, n) - slope(src, n)` |
| `ta.linreg(src, n, 1)` | `forcast(src, n) - 2 * slope(src, n)` |
| 回归斜率（Pine 需手写） | `slope(src, n)` |

### 2.14 枢轴点 — `ta.pivothigh(src, left, right)` / `ta.pivotlow`

```python
left, right = 5, 5
ph_cond = ref(high(), right) == hhv(high(), left + right + 1)
ph = iff(ph_cond, ref(high(), right), math.nan)
plot("PivotHigh", ph, color=Color.red, style=Line.circles)
```

- 原理：在 bar t 判断 `t-right` 处的值是否等于过去 `left+right+1` 根窗口的极值
- ⚠️ 与 Pine 一样**含未来数据**（信号要 right 根之后才确认），回测时注意
- 等值并列极值可能与 Pine 检出点略有差异

### 2.15 一目均衡表（Pine 手写版 → 富途）

```python
tenkan = (hhv(high(), 9) + llv(low(), 9)) / 2
kijun = (hhv(high(), 26) + llv(low(), 26)) / 2
senkou_a = (tenkan + kijun) / 2
senkou_b = (hhv(high(), 52) + llv(low(), 52)) / 2
plot("Tenkan", tenkan, color=Color.red)
plot("Kijun", kijun, color=Color.blue)
plot("SenkouA", senkou_a, color=Color.ligreen, ref=26)   # Pine displacement=26
plot("SenkouB", senkou_b, color=Color.brown, ref=26)
plot("Chikou", close(), color=Color.gray, ref=-26)
plot_fillcolor("Cloud", senkou_a, senkou_b, cond=True, color=Color.ligray)
```

⚠️ `plot` 的 `ref` 移位方向（正数向前还是向后）手册未写明，需在客户端实测校准。

## 3. 常用模式片段

### 3.1 常数序列（喂给只接受 Sequence 的函数）

```python
axis50 = rsi_val * 0 + 50
cross(rsi_val, axis50, 1)
```

### 3.2 严格逐根递增/递减（与 `ta.rising` 区分）

```python
strict_up = count(x.diff() > 0, n) == n     # 或用 up_n_day(x, n)
strict_dn = count(x.diff() < 0, n) == n     # 或用 down_n_day(x, n)
pine_rising = x > x.ref(1).hhv(n)           # ta.rising 的精确等价
pine_falling = x < x.ref(1).llv(n)          # ta.falling 的精确等价
```

### 3.3 金叉/死叉信号 + 图标

```python
golden = cross(fast, slow, 1)
death = cross(slow, fast, 1)
plot_icon("金叉", golden, low(), Shape.triangleup, color=Color.red, size=3, offsetv=-1)
plot_icon("死叉", death, high(), Shape.triangledown, color=Color.green, size=3, offsetv=1)
plot_text("买", golden, low() * 0.99, "买", color=Color.red, size=2)
```

### 3.4 条件填充两条线之间

```python
# Pine: fill(p1, p2, color = bull ? color.new(color.green, 80) : na)
plot_fillcolor("BullZone", fast, slow, cond=fast > slow, color=Color.ligreen)
```

### 3.5 超买超卖区背景带（替代 bgcolor 的近似方案）

`bgcolor` 无对应函数；若用户接受，可用填充到水平线的方式近似：

```python
plot_hline("上限", 70, color=Color.gray, style=Line.line_dashed)
plot_hline("下限", 30, color=Color.gray, style=Line.line_dashed)
plot_fillcolor("Zone", 70, 30, cond=True, color=Color.ligray)  # 常量序列做整带填充
```

### 3.6 多空柱体着色直方图

```python
plot("HIST", hist, color=iff(hist >= hist.ref(1), Color.red, Color.green), style=Line.histogram)
```

## 4. 已知"只能近似或不可转"的指标

| 指标/Pine 函数 | 处理方式 |
|---|---|
| `ta.supertrend(factor, atrPeriod)` | 依赖逐 bar 递归的上下轨状态机，向量化无可靠等价。向用户说明：可改用 ATR 通道近似（`hl2 ± factor * tr().smma(n, 1)`），但信号逻辑不同 |
| `ta.sar(...)` | 同上，加速因子递归不可向量化 |
| `ta.vwap` / Anchored VWAP | 需要按交易时段重置的累计量；可尝试用 `day()` 检测换日 + 分组累计实现（复杂，且富途未明确支持分组运算），默认告知不可转 |
| `ta.alma` | 无内置；如必须，按 ALMA 定义手工展开权重（`math.e ** (-((i - m) ** 2) / (2 * s * s))` 加权求和），代码冗长 |
| 滚动中位数/分位数 | 无；可用 `hhv`/`llv` 组合近似分位区间 |
