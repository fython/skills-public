# 通达信 → 富途新版 Python 函数映射

本表用于转换时查阅。富途签名以客户端内置函数库/《指标帮助手册》为最终准绳；“待验证”表示客户端版本或输入类型可能有差异。

## 目录

- [1. 语法与数据](#1-语法与数据)
- [2. 引用与窗口](#2-引用与窗口)
- [3. 均线与统计](#3-均线与统计)
- [4. 条件与状态](#4-条件与状态)
- [5. 数学与时间](#5-数学与时间)
- [6. 绘图与样式](#6-绘图与样式)
- [7. 不可直接转换](#7-不可直接转换)

## 1. 语法与数据

### 1.1 语句

| 通达信 | 富途 Python | 注意 |
|---|---|---|
| `X:=E;` | `x = e` | 赋值，不绘图 |
| `X:E;` | `x = e` 后 `plot("X", x)` | 冒号是输出，不是 Python 类型标注 |
| `E;` | 生成名称后 `plot(name, e)` | 记录命名假设 |
| `{注释}` | `# 注释` | 通达信注释不可嵌套 |
| `A=B` | `a == b` | 通达信 `=` 是相等比较 |
| `A<>B` | `a != b` | `!=` 也可原样表达 |
| `A AND B` / `A OR B` | `(a) & (b)` / `(a) \| (b)` | Sequence 比较必须加括号 |
| `NOT A` | `~(a)` | 不要对 Sequence 用 Python `not` |
| `IF(C,A,B)` / `IFF(C,A,B)` | `iff(c, a, b)` | Sequence 分支 |
| `IFN(C,A,B)` | `iff(c == 0, a, b)` | 通达信条件为 0 时取 A |
| `DRAWNULL` | `math.nan` | 脚本顶部加 `import math` |

### 1.2 行情序列

| 通达信 | 富途 | 注意 |
|---|---|---|
| `C` / `CLOSE` | `close()` | 必须加括号 |
| `O` / `OPEN` | `open()` | |
| `H` / `HIGH` | `high()` | |
| `L` / `LOW` | `low()` | |
| `V` / `VOL` | `vol()` | 通达信 A 股常以“手”显示，需核对目标单位 |
| `AMO` / `AMOUNT` | `amount()` | 核对币种与单位 |
| `TR` | `tr()` | 真实波幅 |
| `CAPITAL` | `capital()` | 版本/市场支持可能不同 |
| `INDEXC/INDEXO/INDEXH/INDEXL/INDEXV` | 无通用当前图表等价 | 指数数据是另一数据源，不要替换为个股 OHLCV |

## 2. 引用与窗口

| 通达信 | 富途 | 注意 |
|---|---|---|
| `REF(X,N)` | `ref(x, n)` 或 `x.ref(n)` | N 最稳妥为非负标量 |
| `REFV(X,N)` | `ref(x, n)` 近似 | 通达信“平滑处理”和动态 N 边界需比对 |
| `REFX/REFXV` | 无安全直接映射 | 引用未来值，会重绘 |
| `HHV(X,N)` / `LLV(X,N)` | `hhv(x,n)` / `llv(x,n)` | N=0 的全历史语义需核对 |
| `HHVBARS(X,N)` / `LLVBARS(X,N)` | `hhv_bars(x,n)` / `llv_bars(x,n)` | 两边均返回距极值的非负周期数 |
| `SUM(X,N)` | `sum(x,n)` | N=0 从首个有效值累计 |
| `COUNT(C,N)` | `count(c,n)` | 条件为真的周期数 |
| `MULAR(X,N)` | `mular(x,n)` | 待客户端核实可用版本 |
| `SUMBARS(X,A)` | `sum_bars(x,a)` | 累加达到目标所需周期数 |
| `BARSCOUNT(X)` | `bars_count(x)` | 有效数据总周期数 |
| `CURRBARSCOUNT` | `curr_bars_count(close())` | 从当前到最后一根的计数，需实测起点 |
| `ISLASTBAR` | `curr_bars_count(close()) == 1` | 以客户端计数定义验证 |
| `CONST(X)` | 无完全等价 | 取最后值为全序列常量涉及回看未来；默认不迁移 |
| `ALIGNRIGHT(X)` | 无可靠直接映射 | 有效值重排语义不同 |

动态窗口是高风险项。若 `N` 是随 K 线变化的 Sequence，而富途签名只接受整数参数，不要强转。

## 3. 均线与统计

| 通达信 | 富途 | 注意 |
|---|---|---|
| `MA(X,N)` | `sma(x,n)` | 简单移动平均 |
| `EMA(X,N)` / `EXPMA(X,N)` | `ema(x,n)` | |
| `SMA(X,N,M)` | `smma(x,n,m)` | 不是简单均线；递推 `Y=(M*X+(N-M)*Y')/N` |
| `MEMA(X,N)` | `smma(x,n,1)` | 通达信称等价于 `SMA(X,N,1)` |
| `WMA(X,N)` | `wma(x,n)` | |
| `DMA(X,A)` | `dma(x,a)` | A 可为序列；需满足权重范围 |
| `TMA(X,A,B)` | `tma(x,b,a)` | 参数必须交换：通达信为 `Y=A*Y'+B*X`，富途为 `Y=a*X+b*Y'` |
| `XMA(X,N)` | `xma(x,n)` | 未来函数，会重绘，必须警告 |
| `AVEDEV(X,N)` | `avedev(x,n)` | 平均绝对偏差 |
| `DEVSQ(X,N)` | `devsq(x,n)` | |
| `STD(X,N)` | `std(x,n)` | 样本标准差 |
| `STDP(X,N)` | `stdp(x,n)` | 总体标准差 |
| `VAR(X,N)` | `var(x,n)` | 样本方差 |
| `VARP(X,N)` | `varp(x,n)` | 总体方差 |
| `COVAR(X,Y,N)` | `covar(x,y,n)` | |
| `RELATE(X,Y,N)` | `corr(x,y,n)` | 相关系数 |
| `FORCAST(X,N)` | `forcast(x,n)` | 两边均沿用 `forcast` 拼写 |
| `SLOPE(X,N)` | `slope(x,n)` | |

## 4. 条件与状态

| 通达信 | 富途 | 注意 |
|---|---|---|
| `CROSS(A,B)` | `cross(a,b,1)` | 等值边界可能有差异 |
| `LONGCROSS(A,B,N)` | `cross(a,b,n)` | 核对“之前 N 根严格小于”的边界 |
| `UPNDAY(X,N)` | `up_n_day(x,n)` | 连续严格上涨 |
| `DOWNNDAY(X,N)` | `down_n_day(x,n)` | 连续严格下跌 |
| `UPDOWN(X)` | `sign(x.diff(1))` | 上涨/不变/下跌返回 1/0/-1 |
| `NDAY(X,Y,N)` | `count(x > y,n) == n` | 连续 N 根 X>Y |
| `EXIST(C,N)` | `exist(c,n)` | N 期内至少一次成立 |
| `EXISTR(C,A,B)` | `exist(ref(c,b),a-b+1)` | 假设 A≥B；A/B 为 0 的特殊语义需另行处理 |
| `EVERY(C,N)` | `count(c,n) == n` | 比依赖未确认的别名更稳妥 |
| `BARSLAST(C)` | `bars_last(c)` | 从最近成立到当前的周期数 |
| `BARSLASTCOUNT(C)` | `bars_last_count(c)` | 当前连续成立周期数 |
| `VALUEWHEN(C,X)` | `value_when(c,x)` | 最近一次成立时的值 |
| `LAST(C,A,B)` | `last(c,a,b)` | 参数边界需客户端比对 |
| `FILTER(C,N)` | `filter(c,n)` | 成立后抑制后续 N 根信号 |
| `BACKSET(C,N)` | `backset(c,n)` | 会改写过去 N 根，属于未来函数/重绘 |
| `BARSNEXT(C)` | `bars_next(c)` | 使用下一次成立位置，未来数据/重绘 |
| `FILTERX(C,N)` | 无可靠直接映射 | 反向过滤，默认不可转 |
| `TFILTER/TTFILTER/AUTOFILTER` | 无可靠等价 | 状态机与交易信号配对逻辑 |
| `BARSSINCE(C)` | 无已确认直接映射 | 勿与 `BARSLAST` 混淆 |

## 5. 数学与时间

### 5.1 数学

| 通达信 | 富途 | 注意 |
|---|---|---|
| `ABS(X)` | `abs(x)` | |
| `MAX(A,B)` / `MIN(A,B)` | `max(a,b)` / `min(a,b)` | 富途序列函数 |
| `MAX6(A,...,F)` / `MIN6(A,...,F)` | `max(a,...,f)` / `min(a,...,f)` | 富途支持多参数时可直接展开 |
| `SQRT(X)` | `x ** 0.5` | |
| `POW(A,B)` | `a ** b` | |
| `EXP(X)` | `math.e ** x` | 加 `import math` |
| `CEILING(X)` / `FLOOR(X)` | `ceil(x)` / `floor(x)` | |
| `ROUND(X)` / `ROUND2(X,N)` | `round(x)` / `round(x,n)` | |
| `SIGN(X)` | `sign(x)` | |
| `MOD(A,B)` | `a % b` | |
| `LN(X)` | `ln(x)` | 自然对数 |
| `LOG(X)` | `math_log(x,10)` | 核对原公式所指底数 |
| `BETWEEN(A,B,C)` | `(a >= min(b,c)) & (a <= max(b,c))` | 含边界 |
| `RANGE(A,B,C)` | `(a > b) & (a < c)` | 通达信定义为严格 `B<A<C` |
| `INTPART/FRACPART/RAND` | 仅在客户端函数库确认后转换 | 避免 Python 标量函数误用于 Sequence |

### 5.2 日期时间

| 通达信 | 富途 | 注意 |
|---|---|---|
| `YEAR` | `year()` | |
| `MONTH` | `month()` | |
| `DAY` | `day()` | |
| `WEEKDAY` | `weekday()` | 两端星期编号需样本核验 |
| `WEEKOFYEAR` | `weekofyear()` | |
| `HOUR` | `hour()` | |
| `MINUTE` | `minute()` | |
| `DATE/TIME/TIME2` | 无相同打包整数 | 用分量函数重写比较逻辑 |
| `PERIOD` | `period()` | 富途返回 `BarType`，不可沿用通达信数字枚举 |

## 6. 绘图与样式

### 6.1 输出与绘图函数

| 通达信 | 富途 | 注意 |
|---|---|---|
| `OUT:X;` | `plot("OUT", x)` | 通达信输出语句需显式改为 plot |
| `OUT:IF(C,X,DRAWNULL);` | `plot("OUT", iff(c,x,math.nan))` | 加 `import math` |
| `STICKLINE(C,A,B,W,E)` | `plot_stickline(name,c,a,b,width=w,empty=e,...)` | 参数名/空心样式按客户端签名核验 |
| `DRAWICON(C,Y,T)` | `plot_icon(name,c,y,Shape.*,...)` | 数字图标无稳定一一映射 |
| `DRAWTEXT(C,Y,'文')` | `plot_text(name,c,y,"文",...)` | |
| `DRAWTEXT_FIX` | 无固定视口坐标等价 | 可省略或改为最后一根 K 线附近文字，必须说明 |
| `DRAWKLINE(H,O,L,C)` | `plot_candlestick(name,h,o,l,c)` | 两边顺序均为 H,O,L,C |
| `DRAWBAND(A,C1,B,C2)` | `plot_fillcolor(name,a,b,cond=True,color=...)` 近似 | 动态双色需拆分条件 |
| `DRAWLINE/PLOYLINE/DRAWSL` | 无通用动态线段等价 | 不要用普通 `plot` 冒充对象线段 |

### 6.2 颜色

| 通达信 | 富途 |
|---|---|
| `COLORRED/GREEN/BLUE/YELLOW` | `Color.red/green/blue/yellow` |
| `COLORWHITE/BLACK/GRAY` | `Color.white/black/gray` |
| `COLORCYAN/MAGENTA` | `Color.cyan/magenta` |
| `COLORRGB(R,G,B)` 或 `RGB(R,G,B)` | `Color.rgb(r,g,b,255)`，待客户端签名核验 |
| 其他十六进制色 | `Color.hex("#RRGGBB")` |

### 6.3 线型与后缀

| 通达信 | 富途 | 注意 |
|---|---|---|
| `LINETHICK1..9` | `linewidth=1..9` | |
| `DOTLINE` | `style=Line.line_dotted` | |
| `CROSSDOT` | `style=Line.cross` | |
| `CIRCLEDOT` | `style=Line.circles` | |
| `COLORSTICK` | `style=Line.histogram` + 动态涨跌色 | 正负颜色按用户客户端配色确认 |
| `STICK` | `style=Line.histogram` 近似 | |
| `LINESTICK` | `style=Line.histogram_line` | |
| `NODRAW` | 不调用绘图，仅保留变量 | 供量化读取时考虑 `output_parameter` |
| `VOLSTICK` | 直方图近似 | 空实心与涨跌配色未必一致 |

## 7. 不可直接转换

以下能力默认列入“无法转换”，除非富途客户端函数库中确认存在同语义接口：

- 跨品种、跨周期或指标引用：`"SH600000$CLOSE"`、`#WEEK`、`KDJ.K`、`CALCSTOCKINDEX`、`CLOUDREF`。
- 未来引用与之字转向：`REFX/REFXV`、`ZIG`、`PEAK/PEAKBARS`、`TROUGH/TROUGHBARS`。
- 动态绘图对象：`DRAWLINE`、`PLOYLINE`、`DRAWSL`、固定视口面板。
- 成本分布：`COST/WINNER/LWINNER/PWINNER/PPART/COSTEX`。
- 板块横向统计、字符串证券元数据、外部文件/DLL、逐笔与 Level-2 数据。
- 交易账户、持仓、下单、专家系统配对与回测状态。
- 未知 `FINANCE(id)`：先查清字段含义，再寻找 `ffinance` 同义函数；禁止按编号猜测。
