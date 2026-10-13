# 平面图与 3D 的交接约定

本约定用于组织证据，不假设任何文件已经可生产。未知项填 null 或明确写 unknown，不填看似精确的数字。

## 项目层

记录 `schema_version`、`design_id`、`deliverable_level`（concept / print-layout / sewing-pattern）、`units`、`target_height`、比例来源、面料与伸缩方向/实测数据、参考文件、证据类型和假设。

## 部件层

每个部件使用稳定的 `id`，记录：

- `role`：head / torso / limb / hair / garment / accessory；`filled`；`quantity`。
- `source`：文件、页码、图层或图集区域；坐标单位、原点及轴方向。
- `front_art` 与 `back_art`：独立来源、镜像规则；同色反面也须明确指定。
- `outline`、`seam_line`、`cut_line`、`seam_allowance`、折线/省道、对位点；缺失不等同于零。
- `material`、布纹/伸缩方向、厚度依据；概念模型可用注明为假设的值。
- `attachment_ids`、层级与正反朝向，形变时应固定的边界及特征点。

## 连接层

每个连接记录两端 `part_id` 与 `edge_id`/顶点组、类型（seam / inserted-seam / surface-attach / fold）、配对方向、对位点、已知长度或未知状态、允许吃势/活动性，以及依据。

- 整体封闭网格与分体缝合结构都可以表达成品；不能仅凭对象是否合并判定真实连接。
- 一体躯干纸样已有腿和裆部时，在清单中显式标记，不再另加脚体积。
- 对发片自由边不要建立假的缝合边；对被遮住的根部也要记录真实固定位置。

## 地标与验收层

记录头顶、下巴、眼线、刘海下缘、侧发内缘、肩/腕/腿根、头发根部、围裙下缘；采用统一的模型或图稿坐标。比较形变前后使用同一尺度、相机与坐标系。

将“有来源”“几何已连接”“多视角已检查”“缝制已打样”作为不同状态。若必须比较数值误差，先确定单位和与成品尺度相适应的阈值，不把示例阈值当通用标准。
