---
name: pine-to-futu
description: "将 TradingView Pine Script V6 指标代码转换为富途牛牛（moomoo）新版 Python 自定义指标代码。当用户提供 Pine Script 代码（含 ta.* 函数、indicator()、plot() 等）并希望迁移、改写或移植为富途牛牛自定义指标，或询问 Pine 函数与富途指标函数（fquote/fta/fmath/ftool/fplot 模块）的对应关系、两种语言的差异时使用此 Skill。触发关键词：Pine Script、TradingView、富途牛牛、moomoo、自定义指标、指标转换、指标移植。"
---

# Pine Script V6 → 富途牛牛自定义指标 转换指南

## 适用范围

- **源语言**：TradingView Pine Script V6（规则同样覆盖大部分 V5 代码）
- **目标语言**：富途牛牛**新版指标语言**——基于 Python 语法、以 `Sequence` 全序列计算为核心，函数组织在 `fbasic` / `fquote` / `fta` / `fmath` / `ftool` / `fplot` / `fdatetime` / `ffinance` / `fderivative` 模块中（依据官方《指标帮助手册》）

> ⚠️ **两代指标语言辨析（极重要）**：富途客户端存在两代自定义指标语言，语法完全不同，**不要混用**：
> - **旧版（类通达信公式语言）**：`MA20:MA(C,N1),COLORRED;`、`:=` 赋值、`{}` 注释、函数大写
> - **新版（Python 语言，本 Skill 的目标）**：`plot("MA20", sma(close(), 20), color=Color.red)`、`=` 赋值、`#` 注释、函数小写
>
> 转换产物必须全部是新版 Python 语法。若用户明确要求旧版公式语言，应告知本 Skill 不适用。

## 转换铁律：转不了就明说（最高优先级）

转换中遇到任何无法还原的内容，**禁止编造看似合理的代码蒙混过关**——例如：用 `sma` 冒充 `ta.rma`、把递归状态机悄悄简化、丢弃绘图/告警逻辑却不吭声、生成了一个自己都不确定能编译的函数。必须遵守：

1. **能近似就明示近似**：给出近似方案时，说明它与原版的差异（数值口径、信号时机、视觉缺失）
2. **完全转不了就如实告知**：列入「不可转换声明」交付给用户，不要静默省略
3. **拿不准就标实测待验**：手册未写明的行为（标量广播、ref 移位方向、na 传播等），在代码注释和交付说明中标注"以客户端实测为准"
4. **生成不出来就直接说**：如果一段逻辑你想不出可靠的向量化写法，告诉用户"这部分无法转换"，而不是交出一段可能错误的代码

交付转换结果时，固定附上三段式说明：

- ✅ **完整转换**的部分
- ⚠️ **近似转换**的部分（逐项说明差异）
- ❌ **无法转换**的部分（逐项说明原因，对照 [references/function-mapping.md](references/function-mapping.md) 第 10 节不可转换清单）

## 一、核心心智模型（先理解，再动手）

Pine 和富途新语言**看起来都像在操作"序列"，但执行模型根本不同**，这是所有转换规则的总纲：

| 维度 | Pine Script V6 | 富途新版指标语言 |
|---|---|---|
| 执行模型 | 脚本在**每根 K 线上隐式执行一次**，`close` 是"当前 bar 的值" | **全序列向量化计算**：`close()` 一次返回包含所有 bar 的 `Sequence`，类似 pandas |
| 变量本质 | 标量（带隐式历史） | `Sequence`（整列数据），逐元素参与运算 |
| 历史引用 | `close[1]`（`[]` 历史运算符） | `ref(close(), 1)` 或 `close().ref(1)` 或 `close(1)`（fquote 函数自带 ref 参数） |
| 递归序列 | ✅ 常见写法：`x := cond ? v : nz(x[1])` | ❌ **不可能**（`x` 未定义就引用会报错）→ 必须用习语改写，见下 |
| `var` 关键字 | 声明跨 bar 持久的变量 | 无对应概念，直接删除；其"状态保持"语义用习语表达 |
| 条件语句 | `if` 可用于序列逻辑（逐 bar 求值） | `if` 只能用于**标量**配置逻辑；序列条件一律用 `iff(cond, a, b)` |
| 循环 | `for` 可逐 bar 迭代历史 | `for` 只能用于标量/list；逐 bar 逻辑必须改写为滚动窗口函数（`sma`/`hhv`/`sum`/`count` 等） |
| 布尔运算 | 序列上直接用 `and` `or` `not` | 序列用 `&` `|` `~`（且比较表达式**必须加括号**）；`and`/`or`/`not` 只用于标量 |

### 递归序列改写习语（最高频转换障碍）

Pine 中大量 `x := f(x[1])` 的递归写法，在富途中必须换成对应的向量化函数：

| Pine 递归模式 | 富途写法 |
|---|---|
| `var x = 0.0; x := x[1] + v`（累加） | `sum(v, 0)`（n=0 表示从首个非空值起累计） |
| `x := cond ? v : nz(x[1])`（保持最后一次条件为真时的值） | `value_when(cond, v)` |
| `x := cond ? nz(x[1]) + 1 : 0`（连续计数） | `bars_last_count(cond)` |
| `y := m * x + (1 - m) * nz(y[1], x)`（动态权重递推） | `dma(x, m)` |
| `y := (x + (n-1) * nz(y[1], x)) / n`（即 `ta.rma`） | `smma(x, n, 1)` |
| `y := (m * x + (n - m) * y[1]) / n`（即通达信 SMA(X,N,M)） | `smma(x, n, m)` |
| `y := a * x + b * y[1]` | `tma(x, a, b)` |
| 其他任意递归 | **无通用方案**：找代数等价的滚动函数，或向用户说明需简化逻辑 |

更完整的习语与指标配方见 [references/recipes.md](references/recipes.md)。

## 二、转换工作流（按此顺序执行）

0. **分诊（30 秒判定可转性）**：通读 Pine 源码，按下表归类。命中 ❌ 且只是辅助成分的，先声明再继续；**若主体逻辑就建立在不可转能力上**（如谐波形态画线、MTF 多周期数据、supertrend 信号），直接告知用户整体无法还原，不要硬转

   | 在 Pine 源码中看到 | 判定 |
   |---|---|
   | `strategy.` | ⚠️ 只能转信号层，下单/回测丢弃 |
   | `request.`（security/footprint/财务等） | ❌ 不可转（多周期/跨品种/逐档数据） |
   | `label.` / `line.` / `box.` / `table.` / `polyline.` | ❌ 视觉层不可转（形态画线、供需区画框、数据面板） |
   | `bgcolor` / `barcolor` / `alert` | ❌ 无对应，丢弃并声明 |
   | `ta.supertrend` / `ta.sar` / ZigZag 类拐点 | ❌ 递归状态机，无法向量化 |
   | `ta.vwap`（含 anchored）/ Volume Profile | ❌ 数据或机制缺失 |
   | `var` + 带分支的自引用状态机 | ⚠️ 需算法级重写，转前告知保真度风险 |
   | `ta.median` / `ta.percentrank` / `ta.valuewhen(…, ≥1)` | ⚠️ 只能近似 |
   | 其余（均线/动量/通道/交叉/统计类） | ✅ 可转 |

1. **拆分可转与不可转成分**：按第 0 步分诊结果只转换可转部分；不可转部分按上方「转换铁律」向用户声明，不要静默丢弃
2. **写标准引入块与声明头**：删除 `//@version=6`，在脚本顶部写入 9 个模块的 `from xxx import *` 引入块（见下方骨架，缺少会导致执行时找不到函数）；`indicator(...)` → `indicator(short_name, name, main_chart, remarks)`（⚠️ 前两个参数必须**按位置**传递，写成 `short_name=`/`name=` 命名参数会报错），`overlay=true` → `main_chart=True`
3. **改写输入**：`input.int/float/bool/string` → `input_parameter("标题", 默认值)`（类型由默认值推断）；`input.source` **无对应**——在代码顶部定义 `src = close()` 并注释提示用户手动切换；minval/maxval/step/options/tooltip 全部丢弃（可在 remarks 中说明）
4. **改写数据序列与历史引用**：内置变量 → fquote 函数调用（`close` → `close()`）；`x[n]` → `ref(x, n)` / `x.ref(n)`
5. **逐函数映射**：查 [references/function-mapping.md](references/function-mapping.md) 的完整对照表；`ta.rsi/macd/bb/stoch/cci/dmi/hma` 等无内置函数的，套用 [references/recipes.md](references/recipes.md) 的配方
6. **改写逻辑与绘图**：`and/or/not` → `&/|/~`（序列）；三元 `?:` → `iff()`；`plot/hline/fill/plotshape/plotcandle` → `plot_*` 系列；颜色 `color.*` → `Color.*`
7. **自查与验证**：对照文末验证清单逐项检查，提示用户在客户端「指标管理 → 测试指标」编译验证

## 三、脚本骨架对照

**Pine V6：**

```pine
//@version=6
indicator("双均线", shorttitle="DEMA", overlay=true)
fastLen = input.int(5, "快线", minval=1)
slowLen = input.int(20, "慢线", minval=1)
fast = ta.ema(close, fastLen)
slow = ta.ema(close, slowLen)
plot(fast, "Fast", color=color.orange, linewidth=2)
plot(slow, "Slow", color=color.blue, linewidth=2)
```

**富途新版指标语言：**

```python
from fbasic import *
from fdatetime import *
from fmath import *
from fplot import *
from fquote import *
from fta import *
from ftool import *
from ffinance import *
from fderivative import *

indicator("DEMA", "双均线", main_chart=True)   # ⚠️ 前两个参数必须按位置传递，不能写 short_name=/name=

fast_len = input_parameter("快线", 5)   # Pine 的 minval/maxval 不支持，丢弃
slow_len = input_parameter("慢线", 20)

plot("Fast", ema(close(), fast_len), color=Color.hex("#FFA500"), linewidth=2)
plot("Slow", ema(close(), slow_len), color=Color.blue, linewidth=2)
```

要点：① 脚本**必须以 9 个模块的 `from xxx import *` 引入块开头**（fbasic/fdatetime/fmath/fplot/fquote/fta/ftool/ffinance/fderivative），否则执行时找不到函数；② **`indicator()` 的前两个参数必须按位置传递**（`indicator("DEMA", "双均线", main_chart=True)`），`short_name=`/`name=` 命名形式会报错；③ `plot` 的**名称是第一个参数**；④ `color.orange` 在富途无内置色，用 `Color.hex()` 兜底；⑤ 引入后模块函数裸名调用（`ema`/`close`/`plot`），枚举类带类名前缀（`Color.red`、`Line.line`、`Shape.arrowup`、`BarType.K_DAY`），Python 标准库 `math`/`random`/`json` 保持模块前缀（`math.nan`、`random.random()`）。

## 四、核心映射速查表

### 4.1 数据序列（Pine 变量 → 富途 fquote 函数）

| Pine | 富途 | 说明 |
|---|---|---|
| `open` / `high` / `low` / `close` | `open()` / `high()` / `low()` / `close()` | 返回 `Sequence`，**必须加括号** |
| `volume` | `vol()` | 成交额用 `amount()` |
| `close[1]`（历史引用） | `close(1)` 或 `ref(close(), 1)` 或 `close().ref(1)` | fquote 函数自带 ref 移位参数 |
| `hl2` / `hlc3` / `ohlc4` | `(high()+low())/2` 等，手写 | 无内置变量 |
| `bar_index` | `bars_count(close()) - 1`（近似） | 前导空值时略有偏差 |
| `time` / `time_close` | 无直接对应 | 用 `day()`/`hour()` 等分量函数替代 |
| `dayofweek` / `dayofmonth` / `hour` / `minute` / `month` / `year` / `second` / `weekofyear` | `weekday()` / `day()` / `hour()` / `minute()` / `month()` / `year()` / `second()` / `weekofyear()` | 注意是 `weekday()` 不是 `dayofweek()` |
| `timeframe.period` | `period()` | 返回 `BarType` 枚举 |
| `syminfo.*` / `ticker.*` | 无 | 指标固定运行在图表品种上 |

### 4.2 na 处理

| Pine | 富途 |
|---|---|
| `na` | `math.nan`（标量语境也可用 `None`） |
| `na(x)` | `is_na(x)` |
| `nz(x)` / `nz(x, v)` | `replace_na(x, 0)` / `replace_na(x, v)` |
| `fixnan(x)` | `fill_na(x, "forward")` |

### 4.3 逻辑运算（序列）

| Pine | 富途 |
|---|---|
| `cond1 and cond2` | `(cond1) & (cond2)` |
| `cond1 or cond2` | `(cond1) \| (cond2)` |
| `not cond` | `~(cond)` |
| `cond ? a : b` | `iff(cond, a, b)`（a/b 也可以是 `Color`，用于动态颜色） |

### 4.4 最常用 ta 函数

| Pine | 富途 | 备注 |
|---|---|---|
| `ta.sma(x, n)` | `sma(x, n)` | |
| `ta.ema(x, n)` | `ema(x, n)` | |
| `ta.wma(x, n)` | `wma(x, n)` | |
| `ta.rma(x, n)` | `smma(x, n, 1)` | ⚠️ 不是 `sma`！见陷阱 2 |
| `ta.hma(x, n)` | 配方（recipes.md） | 无内置 |
| `ta.vwma(x, n)` | `(x * vol()).sma(n) / vol().sma(n)` | |
| `ta.tr(true)` | `tr()` | 富途 tr 自动取图表 HLC |
| `ta.atr(n)` | `tr().smma(n, 1)` | rma(tr) 的习语 |
| `ta.highest(x, n)` / `ta.lowest(x, n)` | `hhv(x, n)` / `llv(x, n)` | |
| `ta.highestbars(x, n)` / `ta.lowestbars(x, n)` | `-hhv_bars(x, n)` / `-llv_bars(x, n)` | ⚠️ Pine 返回负偏移，富途返回正数 |
| `ta.stdev(x, n)` | `stdp(x, n)` | ⚠️ Pine 默认总体标准差；`ta.stdev(x, n, false)` → `std(x, n)` |
| `ta.variance(x, n)` | `varp(x, n)` | 同理，`false` → `var(x, n)` |
| `ta.correlation(x, y, n)` | `corr(x, y, n)` | |
| `ta.dev(x, n)` | `avedev(x, n)` | 平均绝对偏差 |
| `math.sum(x, n)` / `ta.cum(x)` | `sum(x, n)` / `sum(x, 0)` | |
| `ta.change(x, n)` / `ta.mom(x, n)` | `x.diff(n)` | |
| `ta.roc(x, n)` | `x.pct_change(n) * 100` | |
| `ta.crossover(a, b)` | `cross(a, b, 1)` | |
| `ta.crossunder(a, b)` | `cross(b, a, 1)` | ⚠️ 参数对调 |
| `ta.cross(a, b)` | `cross(a, b, 1) \| cross(b, a, 1)` | |
| `ta.rising(x, n)` | `x > x.ref(1).hhv(n)` | ⚠️ 不是 `up_n_day`，语义不同，见陷阱 6 |
| `ta.falling(x, n)` | `x < x.ref(1).llv(n)` | 同上 |
| `ta.barssince(cond)` | `bars_last(cond)` | |
| `ta.valuewhen(cond, x, 0)` | `value_when(cond, x)` | occurrence ≥ 1 无对应 |
| `ta.rsi` / `ta.macd` / `ta.bb` / `ta.stoch` / `ta.cci` / `ta.dmi` | 配方（recipes.md） | 富途无内置，用基础函数组装 |

完整对照（含 math.*、plot 样式、颜色、形状）见 [references/function-mapping.md](references/function-mapping.md)。

### 4.5 绘图

| Pine | 富途 | 备注 |
|---|---|---|
| `plot(x, title, color, linewidth, style, offset)` | `plot(name, x, color, style, linewidth, ref)` | 名称在首位；ref=移位周期（方向以客户端实测为准） |
| `hline(price, title, color, linestyle)` | `plot_hline(name, price, color, style)` | `hline.style_dashed` → `Line.line_dashed` |
| `fill(p1, p2, color)` | `plot_fillcolor(name, val1, val2, cond, color)` | Pine 的 `color = cond ? c : na` → 直接用 `cond` 参数 |
| `plotshape(cond, style, location, color, size)` | `plot_icon(name, cond, y, Shape.*, color, size, offseth, offsetv)` | location 用 y 坐标表达：`abovebar` → `high()` 附近，`belowbar` → `low()` 附近 |
| `plotshape(..., text="买")` / `plotchar` | `plot_text(name, cond, y, text, color, size)` | |
| `plotcandle(o, h, l, c)` | `plot_candlestick(name, high, open, low, close)` | ⚠️ **参数顺序不同**：富途是 high, open, low, close |
| `bgcolor(...)` / `barcolor(...)` | **无对应** | 直接丢弃并向用户说明 |

## 五、高频陷阱清单

1. **`close` 忘加括号**：富途里 `close()` 是函数调用，不是变量。所有内置行情序列同理
2. **`ta.rma` ≠ `sma`**：Pine 的 rma（Wilder 平滑）对应 `smma(x, n, 1)`；而 `ta.sma`（简单平均）才对应 `sma`。RSI/ATR/ADX 内部都用 rma，写错结果会偏
3. **标准差默认口径**：Pine `ta.stdev`/`ta.variance` 默认 `biased=true`（总体）→ `stdp`/`varp`；富途 `std`/`var` 是样本口径。布林线必须用 `stdp`
4. **bars 类函数符号**：`ta.highestbars`/`ta.lowestbars` 返回 ≤0 的偏移，富途 `hhv_bars`/`llv_bars` 返回 ≥0 的周期数，转换时加负号
5. **cross 的参数顺序**：富途只有"上穿" `cross(x, y, n)`（前 n 点 x 均小于 y、当前 x 大于 y）；下穿必须把参数对调。另外富途要求前 n 点**严格**小于，Pine 前一根是 `<=`，等值边界有细微差异
6. **`ta.rising` 的真实语义**：是"当前值大于过去 n 期内所有值"，**不是**逐根递增——对应 `x > x.ref(1).hhv(n)`。富途 `up_n_day(x, n)` 是"逐根严格递增"（通达信 UPNDAY 语义），两者不等价，混用会改变信号
7. **递归自引用无法编译**：`x = iff(cond, a, ref(x, 1))` 会报未定义错误，必须用第一节的习语表改写
8. **序列逻辑运算符**：`cond1 and cond2` 在序列上是错误（或语义不符），必须 `(cond1) & (cond2)`，括号不可省（`&` 优先级高于比较符）
9. **纯标量进不了序列函数**：`cross(rsi, 50, 1)` 的 `50` 可能被拒（手册签名要求 Sequence）。稳妥写法：构造常数序列 `axis50 = rsi * 0 + 50`，再 `cross(rsi, axis50, 1)`（部分版本支持标量广播，以客户端实测为准）
10. **`if`/`for` 只服务标量**：序列上的逐 bar 分支/循环必须向量化（`iff`、布尔掩码算术、滚动窗口函数）
11. **颜色透明度方向相反**：Pine `color.rgb(r,g,b,transp)` 的 transp 是**透明度**（0-100，100=全透明）；富途 `Color.rgb(r,g,b,a)` 的 a 是**不透明度**（0-255，255=不透明）。换算：`a = round((100 - transp) * 255 / 100)`
12. **`plot_candlestick` 参数顺序**：富途是 `(name, high, open, low, close)`，Pine 是 `(open, high, low, close)`，直接照搬会画出错乱 K 线

## 六、完整转换示例

**Pine V6 源码：**

```pine
//@version=6
indicator("RSI 50 轴交叉", shorttitle="RSIX", overlay=false)

lenRSI = input.int(14, "RSI 周期", minval=1)
src    = input.source(close, "数据源")

rsiVal  = ta.rsi(src, lenRSI)
crossUp = ta.crossover(rsiVal, 50)
crossDn = ta.crossunder(rsiVal, 50)

plot(rsiVal, "RSI", color=color.new(color.blue, 0), linewidth=2)
hline(70, "超买", color=color.red, linestyle=hline.style_dashed)
hline(30, "超卖", color=color.green, linestyle=hline.style_dashed)
plotshape(crossUp, title="上穿", style=shape.triangleup, location=location.bottom, color=color.green, size=size.small)
plotshape(crossDn, title="下穿", style=shape.triangledown, location=location.top, color=color.red, size=size.small)
bgcolor(rsiVal > 70 ? color.new(color.red, 90) : na)
```

**转换后的富途指标代码：**

```python
from fbasic import *
from fdatetime import *
from fmath import *
from fplot import *
from fquote import *
from fta import *
from ftool import *
from ffinance import *
from fderivative import *

indicator("RSIX", "RSI 50 轴交叉", main_chart=False,
          remarks="RSI 上穿/下穿 50 轴提示。input.source 不支持，数据源请在代码中修改 src 一行")

len_rsi = input_parameter("RSI 周期", 14)
src = close()  # Pine 的 input.source 无对应，需手动切换数据源

# ta.rsi 配方：rma = smma(x, n, 1)
delta = src.diff(1)
up = smma(max(delta, 0.0), len_rsi, 1)
down = smma(max(-delta, 0.0), len_rsi, 1)
rsi_val = 100 * up / (up + down)

axis50 = rsi_val * 0 + 50            # 常数序列（cross 要求 Sequence 参数）
cross_up = cross(rsi_val, axis50, 1)   # ta.crossover
cross_dn = cross(axis50, rsi_val, 1)   # ta.crossunder（参数对调）

plot("RSI", rsi_val, color=Color.blue, linewidth=2)
plot_hline("超买", 70, color=Color.red, style=Line.line_dashed)
plot_hline("超卖", 30, color=Color.green, style=Line.line_dashed)
plot_icon("上穿", cross_up, 25, Shape.triangleup, color=Color.green, size=2)
plot_icon("下穿", cross_dn, 75, Shape.triangledown, color=Color.red, size=2)
# bgcolor 无对应函数，背景染色逻辑已省略
```

转换动作解说（交付时也应这样向用户说明关键决策）：
- `ta.rsi` 富途无内置 → 用 rma 配方组装（`smma(x, n, 1)`）
- `input.source` 不支持 → 顶部 `src = close()` + remarks 提示
- `bgcolor` 无对应 → 省略并显式告知用户
- `plotshape` 的 location.bottom/top → 用固定 y 值（25/75）落在副图边缘

## 七、参考文件

- [references/function-mapping.md](references/function-mapping.md)——**完整**对照表：声明/输入、内置变量、时间、na、ta.* 全表、math.* 全表、绘图 API（样式/形状/颜色/尺寸）、富途独有函数、不可转换清单
- [references/recipes.md](references/recipes.md)——无内置函数的常用指标配方（RSI/MACD/BOLL/KDJ/STOCH/CCI/WPR/MFI/DMI-ADX/HMA/VWMA/SWMA/一目均衡/枢轴点）、递归习语、常用模式片段

查表原则：SKILL.md 第四节的速查表覆盖 80% 场景；遇到没列出的函数，先查 function-mapping.md，再没有就查 recipes.md，仍没有则按"不可转换"处理并向用户说明。

## 八、验证清单（交付前逐项自查）

> ⚠️ **保真度灰色地带**：即使语法 100% 可转，以下差异仍可能导致两边数值对不上，交付时须提醒用户抽查对账：① na/nan 传播语义不同（Pine 的 `na > 1` 得 `na`，富途基于 nan 比较得 `False`），主要影响前 N 根 bar；② EMA/rma 的种子值处理可能不同，长序列末端收敛、头部有差异；③ 复权方式与 K 线数据源不同（如富途默认前复权），属平台数据层差异而非转换错误。

- [ ] 脚本顶部包含 9 个模块的标准引入块（`from fbasic import *` … `from fderivative import *`）
- [ ] `indicator()` 前两个参数为位置传参（未写成 `short_name=`/`name=` 命名形式）
- [ ] 代码中已无 `//@version`、`ta.`、Pine 版 `math.*`（math.max/math.sum/math.pow 等；富途的 `math.nan`/`math.pi` 属正常保留）、`input.`、`color.`、`shape.*`、`size.*`、`strategy.*`/`request.*` 残留
- [ ] 所有行情序列都是函数调用形式：`close()`/`open()`/`high()`/`low()`/`vol()`
- [ ] 所有 `x[n]` 已改为 `ref(x, n)` / `x.ref(n)`
- [ ] 序列布尔运算全部改为 `&` `|` `~` 且比较两侧加了括号
- [ ] 无递归自引用变量；`var` 声明已用习语改写
- [ ] `ta.rma` → `smma(x, n, 1)`（不是 sma）；`ta.stdev` → `stdp`（除非显式 biased=false）
- [ ] `crossunder` 已做参数对调；`cross` 的标量阈值已构造常数序列
- [ ] 每个 `input_parameter` 都有中文标题和合理默认值；`input.source` 已改为顶部 src 变量
- [ ] `plot*` 系列函数名称参数在首位；`plot_candlestick` 参数顺序为 high, open, low, close
- [ ] 颜色已换算（Pine 无对应色用 `Color.hex`，透明度方向已翻转）
- [ ] 已按「转换铁律」完成三段式告知：✅ 完整转换 / ⚠️ 近似转换（含差异）/ ❌ 无法转换（含原因）；生成不出来的部分已如实说明，没有编造代码蒙混
- [ ] 提醒用户在客户端「指标管理 → 测试指标」编译，并与 TradingView 抽查若干 K 线核对数值
