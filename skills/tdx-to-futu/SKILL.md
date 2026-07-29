---
name: tdx-to-futu
description: "将通达信公式系统（TDX/MyLang 风格）的技术指标、条件选股公式、五彩 K 线或专家信号公式转换为富途牛牛（moomoo）新版 Python 自定义指标代码。用户提供含 :=、冒号输出、MA/EMA/SMA/REF/HHV/LLV/CROSS、DRAWICON/STICKLINE、COLORRED/LINETHICK 等通达信公式并要求迁移、改写、解释差异或排查富途编译问题时使用。也适用于查询通达信函数与富途 fbasic/fquote/fta/fmath/ftool/fplot/fdatetime/ffinance/fderivative 函数的对应关系。目标是富途 Python 指标语言，不是富途旧版 MyLang。"
---

# 通达信公式 → 富途新版 Python 指标

## 目标与边界

把通达信的声明式序列公式转换为富途新版 Python 自定义指标。输出必须使用 `Sequence` 全序列运算与 `fbasic`、`fquote`、`fta`、`fmath`、`ftool`、`fplot` 等模块。

不要混用富途的两代语言：

- 富途 MyLang 与通达信语法相近，如 `MA20:MA(C,N),COLORRED;`。如果用户只想让公式在富途旧版公式编辑器运行，先说明可能只需兼容性修订。
- 本 Skill 的固定目标是富途新版 Python，如 `plot("MA20", sma(close(), n), color=Color.red)`。

只转换指标计算与可表达的绘图。不要声称转换结果能执行交易、复现跨品种数据、访问通达信本地数据或保证与通达信逐点完全一致。

## 必读路由

- 每次转换都读 [references/function-mapping.md](references/function-mapping.md)，按源代码实际出现的函数查表。
- 源码含绘图、条件选股、未来函数、动态周期、财务数据或跨品种/跨周期引用时，再读 [references/recipes.md](references/recipes.md)。
- 需要核实依据、查漏函数或向用户给出处时，读 [references/sources.md](references/sources.md)，优先打开通达信官方函数列表与富途官方资料。

## 转换铁律

1. 保留公式含义优先于保留表面写法。通达信与富途都做序列计算，但语法、数据源、绘图和部分边界规则不同。
2. 不编造不存在的富途函数。查不到可靠映射时，标为“待客户端函数库核实”或“无法转换”。
3. 不静默删除。绘图对象、未来函数、跨品种引用、财务编号、交易指令等无法等价迁移时，逐项说明。
4. 不隐藏重绘。发现未来函数或隐式未来数据时，在代码注释和交付说明中同时标注。
5. 不猜参数默认值。通达信参数通常配置在公式编辑器外；用户未给默认值时，保留清晰占位并询问，或在代码中明确写 `# TODO: 按原公式参数表填写`。
6. 不承诺已编译。除非确实在富途客户端通过“测试指标”，否则写明“需在客户端编译验证”。

交付固定包含：

- ✅ 完整转换：逐项列出等价部分。
- ⚠️ 近似或待验证：列出数值口径、数据单位、绘图样式、边界条件或客户端版本差异。
- ❌ 无法转换：列出被省略的能力与原因。
- 🧪 验证建议：给出至少两个可比对点和富途客户端编译步骤。

## 工作流

### 1. 识别公式类型与外部信息

先提取：

- 公式类型：技术指标、条件选股、五彩 K 线、专家/交易系统公式。
- 主图或副图、输出名称、参数名及默认值。
- 行情序列、普通函数、绘图语句、样式后缀。
- 指标引用、跨品种/跨周期引用、财务/板块/逐笔/Level-2 数据。
- 未来函数、动态回看周期、信号过滤或会改写历史值的函数。

参数默认值、主副图信息不在源码内且用户未提供时，不要凭经验补齐；采用最小明确假设并在交付中列出。

### 2. 进行可转性分诊

| 通达信源码特征 | 判定 |
|---|---|
| `MA/EMA/SMA/WMA/DMA/REF/HHV/LLV/SUM/COUNT/CROSS` 等常用序列函数 | ✅ 通常可直接映射 |
| `DRAWICON/DRAWTEXT/STICKLINE/DRAWKLINE/DRAWBAND` | ⚠️ 可转或近似，视觉需客户端核验 |
| `FILTER/BACKSET/BARSNEXT/XMA` | ⚠️ 富途可能有对应，但涉及信号抑制或未来数据；必须标注行为与重绘风险 |
| `REFX/REFXV/ZIG/PEAK/TROUGH/DRAWLINE` | ❌ 或高风险近似；默认不伪造等价实现 |
| `"代码$字段"`、`#WEEK`、`指标.输出`、`CALCSTOCKINDEX` | ❌ 当前图表外数据/指标引用通常无法等价请求 |
| `FINANCE(id)`、板块/成本分布/逐笔/Level-2/DLL/外部数据 | ⚠️ 仅在找到富途同语义数据函数时重写，否则不可转 |
| `BUY/SELL/ENTERLONG/EXITLONG/AUTOFILTER` 等 | ❌ 不能迁移执行/回测；最多保留布尔信号与图标 |
| 动态周期 `REF(X,A)`、`MA(X,N)` 且 A/N 为序列 | ⚠️ 富途函数签名可能只接受标量周期，需改写或声明 |

主体逻辑依赖不可转能力时，直接说明不能高保真迁移，并只在用户接受后给近似版本。

### 3. 建立富途脚本骨架

始终使用标准引入块。只在实际用到标准库时追加 `import math` 等：

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

indicator("TDX2FT", "转换后的指标", main_chart=False, remarks="由通达信公式转换；请核对参数与数据口径")
```

`indicator()` 的前两个参数按位置传递。根据原公式属性设置 `main_chart=True/False`，不要从是否引用 `CLOSE` 猜主副图。

### 4. 转换语法结构

按以下顺序处理，不要只做字符串替换：

1. `{注释}` → `# 注释`。
2. `X:=expr;` → `x = expr`，只计算不绘制。
3. `X:expr,样式;` → 先计算 `x = expr`，再生成 `plot("X", x, ...)` 或对应绘图函数。
4. 裸输出 `expr;` → 为输出生成稳定名称后绘制，并在说明中记录命名假设。
5. 行情常量改成函数调用：`C/CLOSE` → `close()`，`H` → `high()`，`V/VOL` → `vol()`。
6. `=` 比较 → `==`，`<>` → `!=`；不要误改 Python 赋值语句。
7. 序列逻辑 `AND/OR/NOT` → `&/|/~`，每个比较式都加括号。
8. `IF/IFF` → `iff(cond, a, b)`；不要用 Python `if` 处理 `Sequence` 条件。
9. 函数名按查表结果改为富途小写名或等价表达式。
10. 样式后缀与绘图语句最后处理。

变量名优先转为 ASCII `snake_case`，避免与导入函数冲突。维护一张源变量到目标变量的对应表；通达信变量大小写不敏感，而 Python 大小写敏感。

### 5. 转换输入参数

通达信参数表通常不写在源码中。已知默认值时：

```python
n = input_parameter("周期", 20)
```

只知道变量名但不知道默认值时：

```python
# TODO: 按通达信公式参数表填写原始默认值
n = input_parameter("N", 20)  # 临时值 20，不代表原公式默认值
```

若默认值会显著改变结果，优先停止猜测并要求用户提供参数表。

### 6. 转换计算与绘图

用 [references/function-mapping.md](references/function-mapping.md) 查每个函数。优先采用富途内置函数，不重复手写已有能力。

| 通达信 | 富途 Python |
|---|---|
| `CLOSE` | `close()` |
| `REF(CLOSE,1)` | `ref(close(), 1)` |
| `MA(CLOSE,N)` | `sma(close(), n)` |
| `SMA(X,N,M)` | `smma(x, n, m)` |
| `A AND B` | `(a) & (b)` |
| `IF(COND,X,DRAWNULL)` | `iff(cond, x, math.nan)` |
| `OUT:X,COLORRED,LINETHICK2;` | `plot("OUT", x, color=Color.red, linewidth=2)` |

用到 `math.nan` 时显式 `import math`。绘图映射不确定时保留计算序列，宁可声明视觉层缺失，也不要捏造参数。

### 7. 进行语义审计

逐项检查：

- `SMA(X,N,M)` 是否映射到 `smma(x,n,m)`，而不是简单均线 `sma`。
- `STD` 与 `STDP` 是否保留样本/总体口径。
- `VOL` 的市场与单位是否一致；A 股“手”和目标数据单位可能造成 100 倍差异。
- 复权、停牌、缺失值与首个有效值处理是否可能不同。
- `CROSS` 在相等边界的判断是否需实测。
- `REF` 的周期是否为标量；负数或动态周期是否被误转。
- `DRAWNULL` 是否变为真正的空值而不是 0。
- 未来函数、信号回置、跨周期与跨品种能力是否已显式声明。
- 主副图、颜色、线宽、坐标和图标只承诺近似时是否说清楚。

### 8. 交付并指导验证

先给完整富途代码，再给三段式转换说明和验证建议。建议用户：

1. 在富途桌面端“指标管理”中新建 Python 指标。
2. 粘贴代码并运行“测试指标”。
3. 用相同品种、周期、复权方式和参数，与通达信对比最后 50–100 根 K 线。
4. 至少核对起始区间、交叉信号、空值区间与极值附近。
5. 返回第一条编译错误与函数库签名；根据客户端版本修正，不要盲猜。

## 最小完整示例

通达信：

```text
M1:=MA(CLOSE,N1);
M2:=MA(CLOSE,N2);
快线:M1,COLORRED,LINETHICK2;
慢线:M2,COLORBLUE;
DRAWICON(CROSS(M1,M2),LOW,1);
```

假设参数表给出 `N1=5`、`N2=20`，且原公式为主图：

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

indicator("TDXMA", "通达信双均线", main_chart=True, remarks="由通达信公式转换")

n1 = input_parameter("快线周期", 5)
n2 = input_parameter("慢线周期", 20)

m1 = sma(close(), n1)
m2 = sma(close(), n2)
golden = cross(m1, m2, 1)

plot("快线", m1, color=Color.red, linewidth=2)
plot("慢线", m2, color=Color.blue)
plot_icon("金叉", golden, low(), Shape.arrowup, color=Color.red, size=2)
```

说明 `DRAWICON(...,1)` 到 `Shape.arrowup` 是语义近似，不保证与通达信 1 号图标像素一致；`CROSS` 等值边界也需客户端比对。
