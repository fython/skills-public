# Pine Script V6 → 富途新版指标语言：完整函数对照表

本文件是 [SKILL.md](../SKILL.md) 的详尽版查表手册。所有富途签名以官方《指标帮助手册》为准。

**调用约定（强制）**：每个生成的脚本**必须以标准引入块开头**，否则执行时找不到函数：

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
```

引入之后：
- 各模块函数 → **裸名直接调用**（如 `ema(x, n)`、`close()`、`plot(...)`）
- 枚举/内置类随星号引入一并可用 → 类名前缀：`Color.red`、`Line.line`、`Shape.arrowup`、`BarType.K_DAY`、`FinPeriod.FQ`、`MoneyFlowType.large`
- `math` / `random` / `json` 是 Python 标准库模块 → 保持模块前缀：`math.pi`、`math.nan`、`random.random()`、`json.dumps(obj)`

---

## 1. 声明与输入

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `//@version=6` | 删除 | 富途无版本头 |
| `indicator(title, shorttitle, overlay, ...)` | `indicator(short_name, name, main_chart, remarks)` | ⚠️ 前两个参数必须**按位置**传递（`indicator("DEMA", "双均线", main_chart=True)`），命名形式报错；`overlay=true` → `main_chart=True`；`short_name` 不支持汉字；`precision`/`format`/`timeframe` 等参数无对应 |
| `strategy(...)` | ❌ 不可转换 | 富途指标无下单/回测引擎；`output_parameter(**kwargs)` 仅用于声明回测变量 |
| `input.int(def, title, minval, maxval, step, ...)` | `input_parameter(title, default)` | minval/maxval/step/tooltip/group 全部丢弃，可在 remarks 中说明取值范围 |
| `input.float(...)` / `input.bool(...)` / `input.string(...)` | `input_parameter(title, default)` | 类型由默认值推断 |
| `input.source(close, title)` | ❌ 无对应 | 代码顶部写 `src = close()` 并注释提示用户手动改 |
| `input.color(...)` | ❌ 基本不支持 | 直接写死 `Color.red` 等；手册称返回值可为 Color 但默认值仅支持 str/int/float/bool，以实测为准 |
| `input.time` / `input.symbol` / `input.timeframe` / `input.price` | ❌ 无对应 | |
| `options=[...]` 下拉 | ❌ 无对应 | 改为数值参数 + remarks 说明 |

## 2. 内置变量（行情数据序列）

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `open` | `open(ref=0)` | 返回 `Sequence[float]` |
| `high` | `high(ref=0)` | |
| `low` | `low(ref=0)` | |
| `close` | `close(ref=0)` | |
| `volume` | `vol(ref=0)` | 无成交量数据的品种可用 `vola()`（自动回退成交额） |
| （成交额） | `amount(ref=0)` | Pine 无内置，近似 `close * volume` |
| `hl2` | `(high() + low()) / 2` | |
| `hlc3` | `(high() + low() + close()) / 3` | |
| `ohlc4` | `(open() + high() + low() + close()) / 4` | |
| `hlcc4` | `(high() + low() + close() * 2) / 4` | |
| `bar_index` | `bars_count(close()) - 1`（近似） | `bars_count` 从第一个有效数据计周期数，前导空值时有偏差 |
| `barstate.*` | ❌ 无对应 | |
| `syminfo.*` / `ticker.*` | ❌ 无对应 | 指标固定运行于当前图表品种 |
| `time` / `time_close` / `timenow` | ❌ 无直接对应 | 用下方时间分量函数；构造时间点用 `Time(...)` 类 |

### 时间分量

| Pine V6 | 富途 fdatetime |
|---|---|
| `year` / `month` / `dayofmonth` | `year()` / `month()` / `day()` |
| `dayofweek` | `weekday()` |
| `hour` / `minute` / `second` | `hour()` / `minute()` / `second()` |
| `weekofyear` | `weekofyear()` |
| `timeframe.period` | `period()` → 返回 `BarType` 枚举（`BarType.K_DAY` 等） |
| `session.ismarket` 等 session 变量 | ❌ 无对应；`from_open()` 返回开盘至今分钟数，可部分替代 |
| —（Pine 无） | `total_trading_minute()`、`date_interval(data, target_date)` | 富途独有 |

## 3. 历史引用与 na

| Pine V6 | 富途 |
|---|---|
| `x[n]` | `ref(x, n)` 或 `x.ref(n)` |
| `close[n]` | `close(n)`（fquote 函数自带移位参数，三种写法等价） |
| `x[0]` | `x` |
| 负偏移 `x[-1]`（未来数据） | ❌ 手册未支持；枢轴类逻辑见 recipes.md |
| `na` | `math.nan`（标量语境可 `None`） |
| `na(x)` | `is_na(x)` → `Sequence[bool]` |
| `nz(x)` / `nz(x, v)` | `replace_na(x, 0)` / `replace_na(x, v)` |
| `fixnan(x)` | `fill_na(x, "forward")`；`fill_na(x, "backward")` 为富途独有的反向填充 |

## 4. ta.* 函数全表

### 4.1 移动平均与平滑

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `ta.sma(x, n)` | `sma(x, n)` / `x.sma(n)` | 富途默认 n=5 |
| `ta.ema(x, n)` | `ema(x, n)` / `x.ema(n)` | 富途默认 n=5 |
| `ta.wma(x, n)` | `wma(x, n)` / `x.wma(n)` | |
| `ta.rma(x, n)` | `smma(x, n, 1)` | ⚠️ Wilder 平滑；`smma(x,n,m) = (m*x + (n-m)*y[1])/n`，即通达信 SMA(X,N,M) |
| `ta.hma(x, n)` | 配方见 recipes.md | 无内置 |
| `ta.vwma(x, n)` | `(x * vol()).sma(n) / vol().sma(n)` | |
| `ta.swma(x)` | `(x + 2*x.ref(1) + 2*x.ref(2) + x.ref(3)) / 6` | 固定权重 [1,2,2,1]/6 |
| `ta.alma(x, n, offset, sigma)` | ❌ 无对应 | 需手工权重展开，建议改用 ema |
| `ta.linreg(x, n, offset)` | `forcast(x, n)` / `slope(x, n)` 组合 | offset=0 的拟合值 ≈ `forcast(x,n) - slope(x,n)`；详见 recipes.md |
| —（Pine 无） | `dma(x, m)` / `tma(x, a, b)` / `xma(x, n)` | 富途独有的递推/偏移均线 |

### 4.2 动量与变化

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `ta.change(x, n)` / `ta.mom(x, n)` | `x.diff(n)` | 默认 n=1 |
| `ta.roc(x, n)` | `x.pct_change(n) * 100` | pct_change 是小数形式 |
| `ta.rsi(x, n)` | 配方见 recipes.md | 无内置 |
| `ta.macd(src, fast, slow, sig)` | 配方见 recipes.md | 返回三元组，注意国内柱体 ×2 习惯 |
| `ta.stoch(h, l, c, n)` | 配方见 recipes.md | |
| `ta.cci(x, n)` | `(x - x.sma(n)) / (0.015 * x.avedev(n))` | ta.dev = avedev |
| `ta.wpr(n)` | `(hhv(high(), n) - close()) / (hhv(high(), n) - llv(low(), n)) * -100` | |
| `ta.mfi(x, n)` / `ta.cmo(x, n)` | 配方见 recipes.md | |
| `ta.mom` 相关自定义 | `x.diff(n)`、`x.pct_change(n)` | |

### 4.3 波动与区间

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `ta.tr(true)` / `ta.tr(false)` | `tr()` | 自动取图表 HLC 与前收；定义一致 |
| `ta.atr(n)` | `tr().smma(n, 1)` | rma(tr) 习语 |
| `ta.bb(x, n, mult)` | 配方见 recipes.md | 用 `stdp`（Pine 默认总体口径） |
| `ta.bbw(x, n, mult)` | `(upper - lower) / mid`（配方内） | |
| `ta.kc(x, n, mult, useTR)` | 配方见 recipes.md | 经典实现，Pine 内置细节可能略有差异 |
| `ta.range(x, n)` | `hhv(x, n) - llv(x, n)` | |
| `ta.supertrend(factor, atrPeriod)` | ❌ 无可靠对应 | 依赖逐 bar 递归状态，见不可转换清单 |
| `ta.sar(...)` | ❌ 无对应 | 同上 |
| —（Pine 无） | `volat(price, n, bar_type)` | 年化波动率，富途独有 |

### 4.4 统计

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `ta.stdev(x, n)`（默认 biased=true） | `stdp(x, n)` | ⚠️ 总体口径 |
| `ta.stdev(x, n, false)` | `std(x, n)` | 样本口径 |
| `ta.variance(x, n)` / `ta.variance(x, n, false)` | `varp(x, n)` / `var(x, n)` | 同上规则 |
| `ta.correlation(x, y, n)` | `corr(x, y, n)` | |
| `ta.dev(x, n)` | `avedev(x, n)` | 平均绝对偏差 |
| （协方差，需手写） | `covar(x, y, n)` | 富途独有内置 |
| `ta.median` / `ta.mode` / `ta.percentile_*` / `ta.percentrank` | ❌ 无滚动版本 | `Sequence.quantile(n)` 是全序列标量分位数，不是滚动窗口 |
| `math.sum(x, n)` | `sum(x, n)` / `x.sum(n)` | n=0 → 从首个非空值累计 = `ta.cum(x)` |
| `ta.cum(x)` | `sum(x, 0)` | |
| —（Pine 无） | `devsq(x, n)` / `mular(x, n)` | 偏差平方和 / n 期乘积，富途独有 |

### 4.5 极值与位置

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `ta.highest(x, n)` | `hhv(x, n)` / `x.hhv(n)` | |
| `ta.lowest(x, n)` | `llv(x, n)` / `x.llv(n)` | |
| `ta.highestbars(x, n)` | `-hhv_bars(x, n)` | ⚠️ 符号翻转：Pine 返回 ≤0 偏移，富途返回 ≥0 周期数 |
| `ta.lowestbars(x, n)` | `-llv_bars(x, n)` | 同上 |
| `ta.pivothigh` / `ta.pivotlow` | 配方见 recipes.md | 含未来数据（Pine 同样如此） |
| —（Pine 无） | `hod(x, n)` / `lod(x, n)` | 当前值是 n 期内第几高/低 |
| —（Pine 无） | `find_n_highest(x, step, n, top)` / `find_n_lowest(...)` / `*_bars` | 第 top 大/小值 |
| —（Pine 无） | `high_range(x)` / `low_range(x)` | 当前值是过去多少周期内最大/小 |

### 4.6 交叉、状态与计数

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `ta.crossover(a, b)` | `cross(a, b, 1)` | 富途要求前 n 点严格小于（Pine 前一根为 `<=`），等值边界有微差 |
| `ta.crossunder(a, b)` | `cross(b, a, 1)` | ⚠️ 参数对调 |
| `ta.cross(a, b)` | `cross(a, b, 1) \| cross(b, a, 1)` | |
| `ta.rising(x, n)` | `x > x.ref(1).hhv(n)` | ⚠️ Pine 语义=当前值 > 前 n 期所有值；**不是** `up_n_day` |
| `ta.falling(x, n)` | `x < x.ref(1).llv(n)` | 同上 |
| （逐根严格递增，Pine 需手写） | `up_n_day(x, n)` | = `count(x.diff() > 0, n) == n` |
| （逐根严格递减） | `down_n_day(x, n)` | |
| `math.sum(cond ? 1 : 0, n) > 0` | `exist(cond, n)` | n 期内至少一次为真 |
| `math.sum(cond ? 1 : 0, n) == n` | `greater_n_day` 不适用；用 `count(cond, n) == n` | n 期内全部为真 |
| （Pine 无直接函数） | `count(cond, n)` | n 期内为真的周期数 = `math.sum(cond?1:0, n)` |
| `ta.barssince(cond)` | `bars_last(cond)` | 均未出现过时返回空值，语义一致 |
| `ta.valuewhen(cond, x, 0)` | `value_when(cond, x)` | ⚠️ 富途只支持最近一次（occurrence=0） |
| —（Pine 无） | `bars_last_count(cond)` | 当前连续为真的周期数 |
| —（Pine 无） | `last(x, step, n)` | step 步长前 n 期内持续为真（通达信 LAST） |
| —（Pine 无） | `bars_count(x)` / `curr_bars_count(x)` / `bars_first_n(cond, n)` | |
| —（Pine 无） | `filter(cond, n)` / `backset(cond, n)` / `bars_next(cond)` / `sum_bars(x, target)` | ⚠️ backset/bars_next 引入未来数据 |

## 5. math.* 函数全表

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `math.abs(x)` | `abs(x)` | 内建函数，支持 Sequence |
| `math.max(a, b, ...)` / `math.min(...)` | `max(a, b, ...)` / `min(...)` | 支持多参数与 Sequence 混合 |
| `math.sign(x)` | `sign(x)` | |
| `math.ceil` / `math.floor` | `ceil` / `floor` | |
| `math.round(x, precision)` | `round(x, ndigits)` | |
| `math.log(x)`（自然对数） | `ln(x)` | |
| `math.log10(x)` | `math_log(x, 10)` | `math_log(x, base)` 默认 base=10 |
| `math.exp(x)` | `math.e ** x` | 富途无 exp 函数 |
| `math.pow(a, b)` | `a ** b` | |
| `math.sqrt(x)` | `x ** 0.5` | |
| `math.sum(x, n)` | `sum(x, n)` | |
| `math.avg(a, b, ...)` | `(a + b + ...) / k` 手写 | |
| `math.mod`（不存在，Pine 用 `%`） | `%` | |
| `math.random(...)` | `random.random()` / `random.uniform(a, b)` / `random.randint(a, b)` / `rand(n)` | |
| `math.pi` / `math.e` | `math.pi` / `math.e` | |
| `math.todegrees(x)` | `x * 180 / math.pi` | |
| `math.toradians(x)` | `x * math.pi / 180` | |
| `sin`/`cos`/`tan`/`asin`/`acos`/`atan`（Pine 在 math.* 下） | `sin`/`cos`/`tan`/`asin`/`acos`/`atan` | 一一对应 |
| `math.round_to_mintick` | ❌ 无对应 | 用 `round(x, ndigits)` 近似 |

## 6. 逻辑与运算

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `cond ? a : b`（序列） | `iff(cond, a, b)` | a/b 可为数值、bool、`Color` |
| `cond ? a : b`（标量） | `a if cond else b` | Python 三元 |
| `and` / `or` / `not`（序列） | `&` / `\|` / `~` | ⚠️ 比较表达式必须加括号：`(a > 1) & (b < 2)` |
| `and` / `or` / `not`（标量） | 同 Pine | Python 关键字一致 |
| `==` `!=` `<` `>` `<=` `>=` | 相同 | 序列上逐元素比较，返回 `Sequence[bool]` |
| `+` `-` `*` `/` `%` | 相同 | 序列逐元素运算 |
| `math.pow` | `**` | |
| — | `//`（整除） | 富途独有（Pine 除法总是小数） |
| `if` 语句 | `if` 语句 | ⚠️ 仅限标量条件；序列分支必须 `iff()` |
| `for` / `while` | `for` / `while` | ⚠️ 仅限标量/list；`Sequence.values` 可取出 list 做全序列后处理 |

## 7. 绘图 API 全表

### 7.1 绘图函数

| Pine V6 | 富途 fplot | 备注 |
|---|---|---|
| `plot(x, title, color, linewidth, style, offset)` | `plot(name, x, color, style, linewidth, ref)` | 名称在**首位**；`ref` 为移位周期（方向以实测为准）；`trackprice`/`histbase`/`display` 无对应 |
| `plotshape(cond, title, style, location, color, size, text)` | `plot_icon(name, cond, y, type, color, size, offseth, offsetv, ref)` | location → 用 y 坐标表达（见 7.4）；带文字改用 `plot_text` |
| `plotchar(...)` | `plot_text(name, cond, y, text, color, size, offseth, offsetv, ref)` | |
| `plotcandle(o, h, l, c, title, color)` | `plot_candlestick(name, high, open, low, close, ref)` | ⚠️ 参数顺序 h, o, l, c |
| `plotbar(o, h, l, c)` | 无直接对应；可用 `plot_stickline(name, cond, bottom, top, width, empty, dashed, color)` 组合近似 | |
| `hline(price, title, color, linestyle)` | `plot_hline(name, x, color, style, linewidth)` | x 为标量 |
| `fill(p1, p2, color)` | `plot_fillcolor(name, val1, val2, cond, color, ref)` | Pine 的条件色 `cond ? c : na` → 直接用 `cond` 参数 |
| `bgcolor(color)` | ❌ 无对应 | |
| `barcolor(color)` | ❌ 无对应 | |
| `alertcondition` / `alert` | ❌ 无对应 | |
| `label.*` / `line.*` / `box.*` / `table.*` / `polyline.*` | ❌ 无对应 | `plot_text`/`plot_icon` 只能部分替代静态标注 |

### 7.2 plot 线型（plot.style_* → Line）

| Pine V6 | 富途 Line | 备注 |
|---|---|---|
| `plot.style_line` | `Line.line`（默认） | |
| `plot.style_histogram` | `Line.histogram` | |
| `plot.style_columns` | `Line.histogram`（近似） | 柱体样式略异 |
| `plot.style_cross` | `Line.cross` | |
| `plot.style_circles` | `Line.circles` | |
| `plot.style_stepline` / `style_steplinebr` | ❌ 无对应，`Line.line` 近似 | |
| `plot.style_area` / `style_areabr` | ❌ 无对应 | 可 `plot_fillcolor` 填充到 0 轴近似 |
| `plot.style_linebr` | `Line.line`（na 自然断开） | |
| `hline.style_solid` | `Line.line` | |
| `hline.style_dashed` | `Line.line_dashed` | |
| `hline.style_dotted` | `Line.line_dotted` | |
| —（Pine plot 无） | `Line.histogram_line` | 柱线同画，富途独有 |

### 7.3 形状（shape.* → Shape，几乎一一对应）

| Pine V6 | 富途 Shape |
|---|---|
| `shape.triangleup` / `shape.triangledown` | `Shape.triangleup` / `Shape.triangledown` |
| `shape.arrowup` / `shape.arrowdown` | `Shape.arrowup` / `Shape.arrowdown` |
| `shape.labelup` / `shape.labeldown` | `Shape.labelup` / `Shape.labeldown` |
| `shape.circle` | `Shape.circle` |
| `shape.square` | `Shape.square` |
| `shape.diamond` | `Shape.diamond` |
| `shape.cross` | `Shape.cross` |
| `shape.xcross` | `Shape.xcross` |
| `shape.flag` | `Shape.flag` |
| `shape.star` | ❌ 无对应，用 `Shape.diamond` 近似 |

### 7.4 位置与尺寸

| Pine V6 | 富途 |
|---|---|
| `location.abovebar` | `y = high()`（可加 `offsetv` 微调，主图） |
| `location.belowbar` | `y = low()`（主图） |
| `location.top` / `location.bottom`（副图） | 固定 y 值（如副图指标的极值区） |
| `location.absolute` | 直接指定 y 数值 |
| `size.tiny` / `small` / `normal` / `large` / `huge` | `size` 取 1~9 整数（近似：tiny→1、small→2、normal→3、large→5、huge→9） |

## 8. 颜色

### 8.1 命名色

| Pine V6 | 富途 Color |
|---|---|
| `color.red` / `color.green` / `color.blue` / `color.yellow` | `Color.red` / `Color.green` / `Color.blue` / `Color.yellow` |
| `color.white` / `color.black` / `color.gray` | `Color.white` / `Color.black` / `Color.gray` |
| `color.fuchsia` | `Color.magenta` |
| `color.aqua` | `Color.cyan` |
| `color.orange` | `Color.hex("#FFA500")` |
| `color.purple` | `Color.hex("#800080")` |
| `color.navy` | `Color.hex("#000080")` |
| `color.teal` | `Color.hex("#008080")` |
| `color.olive` | `Color.hex("#808000")` |
| `color.maroon` | `Color.hex("#800000")` |
| `color.lime` | `Color.hex("#00FF00")` |
| `color.silver` | `Color.hex("#C0C0C0")` |
| —（Pine 无） | `Color.up` / `Color.down` | 跟随客户端涨跌配色，富途独有 |
| —（Pine 无） | `Color.lired`/`ligreen`/`liblue`/`licyan`/`ligray`/`limagenta`/`brown` | 浅色系列，富途独有 |

### 8.2 颜色构造与动态色

| Pine V6 | 富途 | 备注 |
|---|---|---|
| `#RRGGBB` 字面量 | `Color.hex("#RRGGBB")` | |
| `color.rgb(r, g, b, transp)` | `Color.rgb(r, g, b, a)` | ⚠️ 方向相反：`a = round((100 - transp) * 255 / 100)`（transp 0-100 透明度 → a 0-255 不透明度） |
| `color.new(c, transp)` | 无直接对应 | 已知色换算成 `Color.rgb` 并套上行公式 |
| 序列动态色 `cond ? color.red : color.green` | `iff(cond, Color.red, Color.green)` | `plot`/`plot_icon` 等的 color 参数接受 `Sequence(Color)` |
| `color.from_gradient(...)` | ❌ 无对应 | |

## 9. 富途独有（Pine 无对应来源，不可反向映射）

转换时如果 Pine 源码需要这些能力，属于富途增强，按需使用：

| 函数 | 用途 |
|---|---|
| `amount()` / `total_amount()` / `total_vol()` | 成交额 / 当日累计成交额 / 当日累计成交量 |
| `capital()` | 最新流通股本 |
| `money_net_inflow(type)` | 资金净流入（`MoneyFlowType.extra_large/large/medium/small`） |
| `pe_ratio()` / `turnover_rate()` | 市盈率 / 换手率 |
| `rise_count/fall_count/component_count/over_ma200(index)` | 指数涨跌家数等市场宽度数据 |
| `ffinance.*`（23 个财务函数） | 财报数据序列（`total_assets`、`return_on_equity` 等，`FinPeriod.FQ/FY`） |
| `fderivative.*` | 期权持仓/PCR/IV 分位、期货持仓增仓 |
| `filter(cond, n)` / `backset(cond, n)` / `bars_next(cond)` | 信号过滤与回置（⚠️ 后两者含未来数据） |
| `sum_bars(x, target)` / `find_n_highest*` / `find_n_lowest*` / `high_range` / `low_range` | 通达信系工具函数 |
| `output_parameter(**kwargs)` | 声明指标回测变量 |

## 10. 不可转换清单（遇到即向用户声明）

| Pine V6 能力 | 原因/替代 |
|---|---|
| `strategy()` 及全部 `strategy.*`（下单、回测、风险管理） | 富途指标无交易引擎；仅可保留信号绘图，或用 `output_parameter` 声明回测变量 |
| `request.security` / `request.*`（多周期、跨品种、财务数据请求） | 富途指标无法请求其他品种/周期数据；财务数据可改用 `ffinance.*` 重写 |
| `alertcondition()` / `alert()` | 无告警 API |
| `bgcolor()` / `barcolor()` | 无背景/K 线染色 |
| `table.*` / `label.*` / `line.*` / `box.*` / `polyline.*` | 无绘图对象；`plot_text`/`plot_icon` 仅部分替代 |
| `ta.supertrend` / `ta.sar` | 依赖逐 bar 递归状态，向量化模型无可靠等价（可用 `Sequence.apply(func)` 闭包 hack 尝试逐元素带状态计算，但执行顺序无文档保证，不建议） |
| `ta.vwap`（含 anchored） | 需要交易时段重置的累计量，无内置；可尝试用 `day()` 变化检测自行实现（复杂） |
| `ta.valuewhen(cond, x, occurrence)` occurrence ≥ 1 | 富途 `value_when` 只取最近一次 |
| `ta.median` / `ta.mode` / `ta.percentile_*` / `ta.percentrank`（滚动） | 无滚动版本 |
| `array` / `matrix` / `map` / 用户自定义类型（UDT）/ `method` | 无逐 bar 持久化语义；`Sequence.values` 取 list 可做全序列后处理 |
| `varip` / 实时 bar 内逐 tick 计算 | 富途指标按完整序列计算 |
| `log.*` / `str.*` 大部分 | 无日志面板；字符串处理有限（`json` 模块可用） |
| `library` / `import` Pine 库 | 富途 `import` 是 Python 语义，体系不同 |
