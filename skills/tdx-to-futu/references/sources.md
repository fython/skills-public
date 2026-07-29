# 文档来源与核实顺序

本 Skill 的通达信语法与函数定义优先依据通达信官方文档；富途能力以客户端内置函数库/《指标帮助手册》为最终准绳，网页资料用于确认产品入口与语言类型。

## 通达信官方资料

1. [通达信公式系统主页](https://help.tdx.com.cn/gspt/)
   - 公式类型、用途和输出约束。
   - 技术指标、条件选股、专家系统、五彩 K 线是不同公式类型。

2. [通达信公式系统：基本概念](https://help.tdx.com.cn/gspt/docs/markdown/tdxgs-1d1k7b2r1ihug/)
   - `A:CLOSE;` 是指标输出。
   - `A:=CLOSE;` 是赋值且不直接输出。
   - 参数通常在公式编辑器中配置。

3. [通达信公式系统：函数列表](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)
   - 行情、引用、窗口、统计、绘图、财务、板块、交易和运算符的官方定义。
   - 官方明确标注 `BACKSET`、`REFX/REFXV`、`BARSNEXT`、`XMA`、`ZIG/PEAK/TROUGH` 等未来函数或未来数据能力。
   - 官方给出 `SMA(X,N,M)`、`EMA`、`MEMA`、`DMA`、`STD/STDP` 等算法或口径。

4. [通达信公式系统 PDF](https://help.tdx.com.cn/gspt/%E9%80%9A%E8%BE%BE%E4%BF%A1%E5%85%AC%E5%BC%8F%E7%B3%BB%E7%BB%9F.pdf)
   - 网站内容的可下载版本；网页与 PDF 不一致时，以当前官网和客户端函数说明为准。

## 富途/moomoo 官方资料

1. [富途帮助中心：桌面端指标脚本编写](https://support.futunn.com/topic541/?lang=zh-CN)
   - 指标管理入口、函数库、代码编辑区、参数设置和“测试指标”流程。
   - 页面示例主要是旧版 MyLang，不应当与新版 Python 语法混用。

2. [富途帮助中心：编写指标](https://support.futunn.com/topic74?from_platform=1&lang=zh-cn)
   - 自定义指标编辑、导入导出与编译失败排查入口。

3. [moomoo OpenAPI：获取指标列表](https://openapi.moomoo.com/moomoo-api-doc/quote/get-indicator-list.html)
   - 官方接口明确区分 `IndicatorLangType.MyLang` 与 `IndicatorLangType.Python`，证明两种指标脚本语言并存。

4. [moomoo OpenAPI：行情定义中的指标语言类型](https://openapi.moomoo.com/moomoo-api-doc/en/quote/quote.html)
   - `MYLANG` 与 `PYTHON` 枚举、指标输入输出元数据和线型/形状定义。

## 查漏顺序

遇到本 Skill 未收录的通达信函数时：

1. 在通达信官方函数列表中按完整大写函数名查找。
2. 记录参数、返回类型、是否要求特定市场/周期/版本、是否是未来函数。
3. 在富途客户端函数库中按语义搜索，不只按名称搜索。
4. 找到候选后核对窗口边界、初值、缺失值、单位和未来数据行为。
5. 仍不确定时标为“待客户端实测”，不要生成无依据的等价代码。

资料核实日期：2026-07-29。
