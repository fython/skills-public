# 平面图与 3D 的交接约定

本约定用于组织证据，不假设任何文件已经可生产。未知项填 null 或明确写 unknown，不填看似精确的数字。

模板版本 1.1 在 1.0 基础上增加记录项，保留原有字段。读取旧清单时，缺失的新字段视为未记录，不能推断为已验证或已获许可；不适用的项目明确写 not_applicable 并说明原因。

## 项目层

记录 `schema_version`、`design_id`、`deliverable_level`（concept / print-layout / sewing-pattern）、`units`、`target_height`、比例来源、面料与伸缩方向/实测数据、参考文件、证据类型和假设。

- `pattern_version`：本次纸样或图稿版本，与清单格式的 `schema_version` 分开。
- `references`：每项记录 `id`、`author`、`title`、`locator`（文件或原链接）、`checked_at`、`evidence_type`（direct-observation / secondary-notes / design-inference / unconfirmed）、`checked_scope`、`usage_scope`、`license_status` 和 `permission_evidence`。转述笔记须标明转述，链接和可见素材不构成再分发许可；公开附件另核对许可范围。
- `print_setup`：记录 `output_size`、`page_or_fabric_size`（均按项目单位给宽高）、`print_scale_percent`、`calibration_mark`（位置与预期实测长度）和 `raster_dpi`（仅光栅）。印花图与制作纸样均需填写适用项，未知时不得声称可直接按尺寸打印。

## 部件层

每个部件使用稳定的 `id`，记录：

- `role`：head / torso / limb / hair / garment / accessory；`filled`；`quantity`。
- `source`：文件、页码、图层或图集区域；坐标单位、原点及轴方向。
- `front_art` 与 `back_art`：独立来源、镜像规则；同色反面也须明确指定。
- `outline`、`seam_line`、`cut_line`、`seam_allowance`、折线/省道、对位点；缺失不等同于零。
- `material`、布纹/伸缩方向、厚度依据；概念模型可用注明为假设的值。`nap_direction` 与 `stretch_direction` 分别记录，`layout_rotation_constraints` 记录排版可旋转范围或限制；方向均对应来源坐标系，无绒材料的毛向标为不适用。
- `side`、`mirror_rule`：明确左右与翻面/镜像规则，不能从数量或正反图案自行推断。
- `construction`：记录 `method`（如 adhesive-laminate / sewn-and-turned / heat-bonded）、`layer_count`、`layers`、`edge_treatment`、`edge_allowance`、`seam_allowance_included` 和 `turning_opening`。`layers` 逐层记录材料、朝外布面、毛向和伸缩方向；边缘留量须说明用途，不能将胶合留量当作翻面缝份。材料处理条件与证据记入小样记录。
- `attachment_ids`、层级与正反朝向，形变时应固定的边界及特征点。

## 连接层

每个连接记录两端 `part_id` 与 `edge_id`/顶点组、类型（seam / inserted-seam / surface-attach / fold）、配对方向、对位点、已知长度或未知状态、允许吃势/活动性，以及依据。

- 整体封闭网格与分体缝合结构都可以表达成品；不能仅凭对象是否合并判定真实连接。
- 一体躯干纸样已有腿和裆部时，在清单中显式标记，不再另加脚体积。
- 对发片自由边不要建立假的缝合边；对被遮住的根部也要记录真实固定位置。

## 地标与验收层

记录头顶、下巴、眼线、刘海下缘、侧发内缘、肩/腕/腿根、头发根部、围裙下缘；采用统一的模型或图稿坐标。比较形变前后使用同一尺度、相机与坐标系。

将“有来源”“几何已连接”“多视角已检查”“缝制已打样”作为不同状态。若必须比较数值误差，先确定单位和与成品尺度相适应的阈值，不把示例阈值当通用标准。

`validation.views` 分别记录 front / side / back / top 的检查状态；缺少视角不能标为全部通过。改头高、头宽后重新核对五官、发片覆盖和固定位置，改刘海时保持五官图层独立。

`sample_records` 按次记录，未做小样时保留空数组，不虚构结果：

- `id`、`pattern_version`、`kind`（material-test / sewn-sample）、`part_ids`、`material`、`material_directions`、`seam_allowance_handling`、`construction_conditions`、`filling`。
- `measurements` 与 `observations`：缝制样记录头宽、头高、眼距、下巴及头顶/侧脸覆盖；材料样记录适用的粘合、渗胶、掉色、受热与手感结果。尺寸按项目单位记录，必要时附测量方法和照片位置。
- `diagnosis`：区分结构、填充、遮挡或材料工艺问题；`changed_variable`、`compared_to_sample_id`、`result` 与 `pending_checks` 保留本轮改动、前后对照、结果和未验证项。

`validation.physical_sample` 为本版本的实际打样状态，另用 `validation.physical_sample_result` 区分结果；做过小样不等于验证通过。只要影响适用性的结构、尺寸、材料或工艺改变，就重置受影响的当前验证状态并保留旧样记录。交接给 3D 时携带新增字段；3D 检查不能把实样状态提升为通过。
