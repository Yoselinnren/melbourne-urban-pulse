# Melbourne Urban Pulse 逐页面中英文内容架构

> 状态：用户已审核并批准实施（2026-08-16）。
> 日期：2026-08-16。
> 依据：已审核的 `project-positioning.zh-CN.md`、用户提供的 `review-input/methodology-notes.zh-CN.txt`、当前生成数据与公开界面。
> 规则：本文件获批前，不修改公开英文页面。

## 1. 怎样审核这份文件

每个公开位置同时提供：

- **传播任务**：这一位置必须让读者知道什么；
- **拟用英文**：最终准备放到英文网站的文字；
- **中文含义**：用于确认英文实际表达的意思；
- **修改原因**：为什么不保留当前写法；
- **状态**：默认全部为“待审核”。

审核时可以：

1. 直接修改本文件；
2. 在条目后写批注；
3. 将该节的 `[ ]` 改为 `[x]`；
4. 在对话中指出需要改的编号。

批准某一节，只代表批准该节内容，不会自动批准其他页面。

## 2. 全站统一语言规则

### 2.1 项目身份

**拟用英文**

> An interpretable urban data study and interactive research project.

**中文含义**

> 一个可解释的城市数据研究与交互式研究项目。

不使用 `AI-powered platform`、`smart city product` 或 `predictive system`。

### 2.2 研究网络

**拟用英文**

> 12 purposively selected central-Melbourne research sensors with near-complete 2025 coverage.

**中文含义**

> 12 个经过目的性选择、2025 年数据覆盖近乎完整的中央墨尔本研究传感器。

公开界面不再单独使用 `representative sensors`，避免暗示统计代表性。

### 2.3 425 的固定口径

**拟用英文**

> Under the v1 sensor scope, baseline and threshold definitions, the workflow detected 425 cross-location Pulses.

**中文含义**

> 在 v1 的传感器范围、基线和阈值定义下，这套工作流检测到 425 个跨地点 Pulse。

首次出现 425 时必须带口径。后续导航和操作标签可以简写为 `425 Pulses`。

### 2.4 因果边界

主页面只保留一条简洁声明：

**拟用英文**

> Reviewed context records overlap with a signal; it does not establish its cause.

**中文含义**

> 经审查的背景资料记录它与信号的重叠，但不能据此确定原因。

案例不再重复不同版本的口号式免责声明。具体限制放进案例正文或方法论页面。

### 2.5 Pulse 的定义

**拟用英文**

> A Pulse is a rule-defined period in which at least three research sensors show strong departures in the same direction during every included hour.

**中文含义**

> Pulse 是规则定义的时间段：在其中每个纳入小时，至少三个研究传感器都出现同方向的强偏离。

### 2.6 范围标签

`localized`、`broad` 和 `network-wide` 可以保留，但首次出现时必须说明它们依据 Pulse 期间的**峰值同时参与数**分类，不表示全时段持续，也不表示空间聚类。

### 2.7 语调

- 使用具体地点、时间、数据单位和规则；
- 不使用连续的 `not X, but Y` 句型；
- 不把系统拟人化；
- 不用口号代替方法；
- 不把未来研究写成当前能力；
- 不把当前研究范围写成失败或道歉。

---

## 3. 全局 Metadata

### 3.1 网站默认 Metadata

位置：`src/app/layout.tsx`

**拟用英文标题**

> Yoreny | Research Portfolio

**中文含义**

> Yoreny 研究作品集。

**拟用英文描述**

> Research portfolio featuring Melbourne Urban Pulse, an interpretable urban data study built from public pedestrian sensor data.

**中文含义**

> 研究作品集，收录 Melbourne Urban Pulse——一个基于公共行人传感器数据建立的可解释城市数据研究。


状态：[ ] 待审核
这个也不是不行，但是yoreny是我买的域名，未来公司的品牌名，但是我的名字是Siyang，这个在学习阶段还是强调我的真名吧，yoreny在个人主页上在提。但是siyang和yoreny保留也挺好

### 3.2 项目页 Metadata

位置：`/projects/melbourne-urban-pulse`

**拟用英文标题**

> Melbourne Urban Pulse | Yoreny | Siyang

**拟用英文描述**

> An interpretable urban data study that turns 2025 hourly pedestrian counts into local departures, Episodes and cross-location Pulses, with manually reviewed context and explicit uncertainty.

**中文含义**

> 一个可解释的城市数据研究：将 2025 年逐小时行人计数转换为本地偏离、Episode 和跨地点 Pulse，并保留人工审查背景与明确的不确定性。

状态：[ ] 待审核

### 3.3 Explorer Metadata

位置：`/explore`

**拟用英文标题**

> Explore 2025 | Melbourne Urban Pulse

**拟用英文描述**

> Inspect 425 rule-defined Pulses across 12 central-Melbourne research sensors, including direction, duration, hourly participation and evidence-review status.

**中文含义**

> 检查中央墨尔本 12 个研究传感器中的 425 个规则定义 Pulse，包括方向、时长、逐小时参与和证据审查状态。

状态：[ ] 待审核

### 3.4 方法论页 Metadata

位置：`/projects/melbourne-urban-pulse/methodology`

**拟用英文标题**

> Methodology | Melbourne Urban Pulse

**拟用英文描述**

> A plain-language account of how hourly pedestrian observations become local baselines, Episodes, cross-location Pulses and manually reviewed cases.

**中文含义**

> 用普通语言解释逐小时行人观测怎样形成本地基线、Episode、跨地点 Pulse 和人工审查案例。

状态：[ ] 待审核

---

## 4. Portfolio 首页

当前首页仍是个人 Portfolio 占位页。本轮不重做首页，也不把 Melbourne Urban Pulse 的项目级艺术效果迁移过去。

保留现有项目入口，等个人 Portfolio 单独启动时再统一处理首页身份、艺术表达和其他项目。

本轮唯一要求：项目入口继续链接到 `/projects/melbourne-urban-pulse`。

状态：[ ] 同意本轮不修改 Portfolio 首页文案与视觉

---

## 5. 项目页：导航与 Hero

### 5.1 顶部导航

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 项目标识 | Melbourne Urban Pulse | 项目名称 |
| 项目页入口 | Project | 项目叙事 |
| 方法论入口 | Method | 完整方法论页面 |
| Explorer 按钮 | Explore data | 打开数据探索器 |

`Method` 直接链接新方法论路由，不再链接页面内的四步简介。

状态：[ ] 待审核

### 5.2 Hero 眉题

**拟用英文**

> INTERPRETABLE URBAN DATA STUDY · CENTRAL MELBOURNE · 2025

**中文含义**

> 可解释的城市数据研究 · 中央墨尔本 · 2025。

状态：[ ] 待审核

### 5.3 Hero 主标题

**拟用英文**

> When does a place depart from its usual rhythm?

**中文含义**

> 一个地点什么时候会偏离它通常的节律？

修改原因：直接提出研究问题，替换目前较诗化的 `The city keeps a rhythm. We study where it departs.`。

状态：[ ] 待审核

### 5.4 Hero 摘要

**拟用英文**

> This project compares 2025 hourly pedestrian counts from 12 purposively selected central-Melbourne sensors with each location's own weekday–hour baseline. Strong consecutive departures become Episodes; same-direction co-occurrence across at least three sensors becomes a Pulse. Under the v1 definitions, the workflow produced 425 Pulses, with 16 cases selected for manual evidence review.

**中文含义**

> 本项目把中央墨尔本 12 个目的性选择传感器的 2025 年逐小时行人计数，与每个地点自己的星期—小时基线比较。连续的强偏离形成 Episode；至少三个传感器的同方向共现形成 Pulse。在 v1 定义下，工作流产生 425 个 Pulse，其中 16 个案例被选作人工证据审查。

状态：[ ] 待审核

### 5.5 Hero 因果边界

**拟用英文**

> Reviewed context records overlap with a signal; it does not establish its cause.

**中文含义**

> 经审查的背景资料记录它与信号的重叠，但不能据此确定原因。

状态：[ ] 待审核

### 5.6 Hero 操作按钮

| 拟用英文 | 中文含义 |
|---|---|
| Explore the 2025 Pulses | 探索 2025 年 Pulse 结果集 |
| Read the full method → | 阅读完整方法 → |

状态：[ ] 待审核

### 5.7 Hero 数字

| 数字 | 拟用英文标签 | 中文含义 |
|---:|---|---|
| 12 | Central-city research sensors | 中央城区研究传感器 |
| 425 | Pulses under v1 rules | v1 规则下的 Pulse |
| 16 | Manually reviewed cases | 人工审查案例 |

状态：[ ] 待审核

### 5.8 滚动提示

| 拟用英文 | 中文含义 |
|---|---|
| SCROLL TO FOLLOW THE STUDY | 向下阅读研究过程 |
| Detection first · context reviewed afterwards | 先检测 · 后审查背景 |

状态：[ ] 待审核

---

## 6. Hero 数据图注

当前 Hero 图展示每个成员传感器在所选 Pulse 中的峰值偏离标记，不是 12 条逐小时轨迹，也不是城市连续表面。

### 6.1 标题区

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 眉题 | SELECTED PULSE · NEW YEAR, PHASE 1 | 所选 Pulse · 新年第一阶段 |
| 标题 | Above local baselines across the research network | 研究网络中多个地点高于各自本地基线 |
| 时间与参与 | 1 JAN 2025 · 00:00–05:00 · 9–12 ACTIVE SENSORS PER HOUR · 12 INVOLVED | 2025 年 1 月 1 日 · 00:00–05:00 · 每小时 9–12 个活动传感器 · 全时段共 12 个参与 |

### 6.2 图形无障碍说明

**拟用英文**

> Twelve sensor-level peak-deviation marks for the selected Pulse.

**中文含义**

> 所选 Pulse 中 12 个传感器各自的峰值偏离标记。

### 6.3 图脚

| 拟用英文 | 中文含义 |
|---|---|
| Discrete sensor results · no interpolated city surface | 离散传感器结果 · 没有插值生成城市连续表面 |
| ▲ ABOVE BASELINE · ● SELECTED PULSE | 高于基线 · 所选 Pulse |
| 06:00–10:00 → below-baseline phase | 06:00–10:00 → 转为低于基线阶段 |

加载和静态后备提示保持功能性语言，不增加宣传语。

状态：[ ] 待审核

---

## 7. 项目页：研究问题

### 7.1 章节标题

**拟用英文**

> 01 · RESEARCH QUESTION
> When does a place depart from its own usual rhythm?

**中文含义**

> 01 · 研究问题
> 一个地点什么时候会偏离它自己的通常节律？

### 7.2 正文

**拟用英文**

> A pedestrian count has little meaning without a local reference. The same value may be ordinary at one place and unusual at another, or ordinary on a weekday morning and unusual late at night. This study asks how far an hourly observation departs from the usual distribution for the same sensor, weekday and hour; how long that departure persists; and whether the same direction appears across several research locations.

**中文含义**

> 没有本地参照时，一个行人计数很难产生明确含义。同一个数值在一个地点可能普通，在另一个地点可能异常；在工作日上午可能普通，在深夜则可能不同。本研究关注每小时观测与相同传感器、星期和小时的通常分布相差多远，这种偏离持续多久，以及相同方向是否同时出现在多个研究地点。

### 7.3 Pulse 定义卡

**拟用英文标签**

> LOCAL BASELINE → HOURLY DEPARTURE → EPISODE → PULSE

**拟用英文正文**

> A Pulse is a rule-defined period in which at least three research sensors show strong departures in the same direction during every included hour. It describes temporal co-occurrence across geolocated sensors; the v1 grouping does not use distance or spatial adjacency.

**中文含义**

> Pulse 是规则定义的时间段：其中每个纳入小时，至少三个研究传感器都出现同方向强偏离。它描述有地理位置传感器之间的时间共现；v1 分组不使用距离或空间邻接关系。

状态：[ ] 待审核

---

## 8. 项目页：方法简介

### 8.1 章节标题与正文

**拟用英文**

> 02 · METHOD IN BRIEF
> From hourly observations to reviewed Pulses.

> The workflow keeps measurement, baseline construction, deviation detection, cross-location grouping and evidence review separate. The rules remain visible so that each result can be traced back to the observations and decisions that produced it.

**中文含义**

> 02 · 方法简介
> 从逐小时观测到经过审查的 Pulse。

> 工作流将测量、基线构建、偏离检测、跨地点分组和证据审查分开。规则保持可见，使每项结果都能追溯到产生它的观测和决定。

### 8.2 四步方法卡

| 步骤 | 拟用英文标题 | 拟用英文细节 | 中文含义 |
|---|---|---|---|
| 01 | Observe hourly counts | SENSOR · LOCAL TIME · COUNT · MISSINGNESS | 记录传感器、本地时间、计数和缺失 |
| 02 | Establish a local baseline | SENSOR × WEEKDAY × HOUR · MEDIAN · RAW MAD | 按传感器、星期和小时计算中位数与原始 MAD |
| 03 | Detect consecutive departures | HIGH-CONFIDENCE BASELINE · `|SCORE| ≥ 3` · SAME DIRECTION | 仅保留高置信度基线、绝对分数至少 3、同方向的连续偏离 |
| 04 | Group and review | ≥3 SENSORS PER HOUR · CONTEXT REVIEWED AFTER DETECTION | 每小时至少三个传感器；检测后再审查背景 |

### 8.3 方法说明与入口

**拟用英文**

> The score is the observed count minus the local baseline median, divided by the raw MAD. It is a relative deviation measure, not a probability. Read the full methodology for sensor selection, exclusions, thresholds, sensitivity tests and a worked example.

**中文含义**

> 分数等于观测计数减去本地基线中位数，再除以原始 MAD。它是相对偏离尺度，不是概率。完整方法论将解释传感器选择、排除规则、阈值、敏感性检验和完整算例。

**按钮**

> Read the full methodology →
> 阅读完整方法论 →

状态：[ ] 待审核

---

## 9. 项目页：案例 1 / 新年方向转换

### 9.1 章节引言

**拟用英文**

> 03 · CASE 01 / NEW YEAR
> One date, two directions.

> Across the selected research network, a six-hour above-baseline Pulse from 00:00 to 05:00 was followed by a five-hour below-baseline Pulse from 06:00 to 10:00. The hourly number of participating sensors changed throughout both periods; the result is a direction change with an evolving participation pattern.

**中文含义**

> 03 · 案例 1 / 新年
> 同一个日期，两个方向。

> 在所选研究网络中，00:00–05:00 的六小时高于基线 Pulse，随后转为 06:00–10:00 的五小时低于基线 Pulse。两个阶段的逐小时参与传感器数始终在变化；这里的结果是方向转换及其不断变化的参与结构。

### 9.2 第一阶段

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 标签 | PHASE 1 · ABOVE BASELINE | 第一阶段 · 高于基线 |
| 时间 | 00:00–05:00 | 凌晨 0 点至 5 点 |
| 事实 | 6 HOURS · 9–12 ACTIVE SENSORS PER HOUR · 12 INVOLVED · NETWORK-WIDE AT PEAK | 6 小时 · 每小时 9–12 个活动传感器 · 全时段共 12 个参与 · 峰值达到 network-wide |
| 背景 | Reviewed context: New Year events, early-morning crowds, extended public transport and road closures | 审查背景：新年活动、凌晨人群、延长公共交通和道路封闭 |
| 链接 | Inspect this Pulse → | 检查这个 Pulse → |

### 9.3 第二阶段

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 标签 | PHASE 2 · BELOW BASELINE | 第二阶段 · 低于基线 |
| 时间 | 06:00–10:00 | 上午 6 点至 10 点 |
| 事实 | 5 HOURS · 7–12 ACTIVE SENSORS PER HOUR · 12 INVOLVED · NETWORK-WIDE AT PEAK | 5 小时 · 每小时 7–12 个活动传感器 · 全时段共 12 个参与 · 峰值达到 network-wide |
| 背景 | Reviewed context: public-holiday morning, business closures and the end of overnight transport changes | 审查背景：公共假日上午、商业关闭和夜间交通安排结束 |
| 链接 | Inspect this Pulse → | 检查这个 Pulse → |

### 9.4 案例结论

**拟用英文**

> The reviewed sources overlap different parts of the sequence. They help describe its context but do not identify one cause for either phase.

**中文含义**

> 经审查来源覆盖这一连续过程中的不同部分。它们帮助描述背景，但不能为任一阶段确定单一原因。

状态：[ ] 待审核

---

## 10. 项目页：案例 2 / 湿天气

### 10.1 章节引言

**拟用英文**

> 04 · CASE 02 / WET WEATHER
> Two wet periods, two temporal structures.

> Both selected Pulses are below baseline and overlap recorded rain. One lasts three morning hours; the other continues for nine hours from midday. The comparison describes different durations and participation patterns within two purposively selected cases. It does not estimate a general rainfall response.

**中文含义**

> 04 · 案例 2 / 湿天气
> 两个湿天气时段，两种时间结构。

> 两个所选 Pulse 都低于基线并与降雨记录重叠。一个持续三个早晨小时，另一个从中午开始持续九小时。这一比较描述两个目的性案例中不同的持续时间和参与结构，不估计普遍的降雨响应。

### 10.2 1 月 6 日

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 标签 | 6 JAN · WET MORNING | 1 月 6 日 · 湿天气早晨 |
| 时间 | 07:00–09:00 | 上午 7 点至 9 点 |
| 事实 | 3 HOURS · 6–9 ACTIVE SENSORS PER HOUR · 10 INVOLVED | 3 小时 · 每小时 6–9 个活动传感器 · 全时段共 10 个参与 |
| 背景 | 3.6 mm rain across 3 hours · school holiday · Australian Open qualifying in the wider context | 3 个小时累计降雨 3.6 mm · 学校假期 · 更广背景包含澳网资格赛 |

### 10.3 7 月 2 日

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 标签 | 2 JUL · SUSTAINED WET PERIOD | 7 月 2 日 · 持续湿天气时段 |
| 时间 | 12:00–20:00 | 中午 12 点至晚上 8 点 |
| 事实 | 9 HOURS · 3–11 ACTIVE SENSORS PER HOUR · 12 INVOLVED | 9 小时 · 每小时 3–11 个活动传感器 · 全时段共 12 个参与 |
| 背景 | 10.4 mm rain across 8 rainy hours · cold conditions · limited later transport context | 8 个降雨小时累计 10.4 mm · 寒冷条件 · 后半段仅有有限交通背景资料 |

### 10.4 案例结论

**拟用英文**

> The two reviewed wet-weather cases differ in duration and hourly sensor participation. Because they were selected for comparison and other conditions were not controlled, the study treats this as a descriptive contrast rather than a causal weather effect.

**中文含义**

> 两个经过审查的湿天气案例在持续时间和逐小时传感器参与上不同。由于案例为比较而选择，且没有控制其他条件，本研究将其视为描述性对照，而不是天气的因果效应。

状态：[ ] 待审核

---

## 11. 项目页：案例 3 / 活动背景

### 11.1 章节引言

**拟用英文**

> 05 · CASE 03 / ACTIVITY CONTEXT
> Event-overlapping signals do not share one form.

> The selected Melbourne Marathon Pulse is concentrated in one early-morning hour. The 17 December case extends across eight evening and overnight hours. Both are above baseline and overlap documented activities, but their durations and participation structures differ.

**中文含义**

> 05 · 案例 3 / 活动背景
> 与活动重叠的信号并不具有单一形态。

> 所选 Melbourne Marathon Pulse 集中在一个清晨小时；12 月 17 日案例延续八个傍晚和夜间小时。两者都高于基线并与有记录活动重叠，但持续时间和参与结构不同。

### 11.2 Melbourne Marathon

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 标签 | MELBOURNE MARATHON · 06:00 | 墨尔本马拉松 · 06:00 |
| 标题 | One-hour Pulse | 一小时 Pulse |
| 事实 | 1 HOUR · 9 ACTIVE SENSORS · 9 INVOLVED · ABOVE BASELINE | 1 小时 · 9 个活动传感器 · 共 9 个参与 · 高于基线 |
| 背景 | Reviewed context: marathon access, road closures and public-transport arrangements | 审查背景：马拉松入场、道路封闭和公共交通安排 |

### 11.3 12 月 17 日

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 标签 | 17 DEC · 18:00–01:00 | 12 月 17 日 · 18:00–01:00 |
| 标题 | Eight-hour evening Pulse | 八小时晚间 Pulse |
| 事实 | 8 HOURS · 3–8 ACTIVE SENSORS PER HOUR · 10 INVOLVED · ABOVE BASELINE | 8 小时 · 每小时 3–8 个活动传感器 · 全时段共 10 个参与 · 高于基线 |
| 背景 | Reviewed context: RMIT graduation and two Christmas activities with partial time overlap | 审查背景：RMIT 毕业典礼和两个圣诞活动，时间仅部分重叠 |

### 11.4 案例结论

**拟用英文**

> Within this purposively selected case pair, documented activity context overlaps two substantially different temporal forms. The comparison does not estimate attendance-normalised effects or event causation.

**中文含义**

> 在这组目的性选择案例中，有记录的活动背景与两种明显不同的时间形态重叠。这一比较不估计按参与人数标准化的效应，也不判断活动因果关系。

状态：[ ] 待审核

---

## 12. 项目页：案例 4 / 未解释 Episode

### 12.1 章节引言

**拟用英文**

> 06 · CASE 04 / UNRESOLVED
> A detected signal can remain unexplained.

> An eight-hour above-baseline Episode at QVM–Therry Street South remained confined to one sensor. No matching night event was identified within the reviewed sources. The result is retained as unresolved because source coverage cannot prove that no local circumstance occurred.

**中文含义**

> 06 · 案例 4 / 未解释
> 检测到的信号可以仍然无法解释。

> QVM–Therry Street South 出现一个持续八小时、仅限单个传感器的高于基线 Episode。在已审查来源中没有找到匹配的夜间活动。由于来源覆盖无法证明当地没有发生其他情况，结果被保留为未解释。

### 12.2 图形与审查卡

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 地点 | QVM–Therry St (South) | 地点名称 |
| 时间 | 20:00–03:00 · 8 HOURS · ONE SENSOR | 晚上 8 点至凌晨 3 点 · 8 小时 · 单个传感器 |
| 类型 | ISOLATED ABOVE-BASELINE EPISODE | 孤立的高于基线 Episode |
| 卡片标题 | No matching night event identified in reviewed sources | 已审查来源中未识别到匹配夜间活动 |
| 市场常规时间 | No temporal match | 时间不匹配 |
| 夜间活动搜索 | No matching source identified | 未识别到匹配来源 |
| 方向判断 | Indeterminate | 无法判断 |
| 搜索边界 | Limited negative search · not evidence that no local circumstance occurred | 有限的负向搜索 · 不能证明没有本地情况发生 |
| 链接 | Inspect the sensor → | 检查该传感器 → |

### 12.3 案例结论

**拟用英文**

> Unresolved signals remain visible so that a missing explanation is not replaced by an invented one.

**中文含义**

> 未解释信号继续保持可见，避免用虚构解释填补证据缺口。

状态：[ ] 待审核

---

## 13. 项目页：当前范围、来源与未来研究

当前 `LIMITATIONS + PROVENANCE` 改成中性研究范围，不再以连续否定句组织。

### 13.1 章节引言

**拟用英文**

> 07 · CURRENT SCOPE + FURTHER STUDY
> What the v1 framework establishes.

> The current study provides a reproducible result for a defined 2025 sensor network and transparent rule set. Its boundaries describe how the findings should be read and where later research could add resolution.

**中文含义**

> 07 · 当前范围与进一步研究
> v1 框架已经建立了什么。

> 当前研究为一个明确的 2025 年传感器网络和透明规则集提供可复现结果。研究边界说明这些发现应怎样阅读，以及后续研究可以在哪些方面增加分辨率。

### 13.2 三栏内容

#### 当前可以检查

**拟用英文标题**

> Established in v1

**拟用英文条目**

- Direction relative to each local weekday–hour baseline
- Duration and hourly sensor participation
- Cross-location co-occurrence under explicit thresholds
- Manually reviewed context overlap and unresolved cases

**中文含义**

- 相对各地点星期—小时基线的方向；
- 持续时间和逐小时传感器参与；
- 明确阈值下的跨地点共现；
- 人工审查背景重叠和未解释案例。

#### 当前解释范围

**拟用英文标题**

> Interpretation boundary

**拟用英文条目**

- The 12 sensors define a central-city study network, not a city-wide statistical sample
- Pulse scope uses peak simultaneous participation, not spatial clustering
- The 16 cases are purposive comparisons, not a representative sample of all Pulses
- Context overlap does not estimate causal effect, event size or effectiveness

**中文含义**

- 12 个传感器构成中央城区研究网络，不是全市统计样本；
- Pulse 范围使用峰值同时参与数，不是空间聚类；
- 16 个案例是目的性比较，不代表全部 Pulse；
- 背景重叠不估计因果效应、活动规模或有效性。

#### 可进一步研究

**拟用英文标题**

> Opportunities for further study

**拟用英文条目**

- Season-aware and event-aware baselines
- Distance-, precinct- or topology-aware grouping
- Threshold calibration with annotated or held-out data
- Larger sensor networks and causal study designs

**中文含义**

- 季节感知和活动感知基线；
- 距离、街区或拓扑感知分组；
- 使用标注或留出数据校准阈值；
- 更大的传感器网络和因果研究设计。

### 13.3 来源与方法入口

**拟用英文**

> The research trail includes City of Melbourne pedestrian observations, weather and calendar records, transport and event sources, versioned processing scripts, UI data contracts and manual evidence-review records.

> Read methods, sources and reproducibility notes →

**中文含义**

> 研究链包含墨尔本市行人观测、天气和日历记录、交通与活动来源、版本化处理脚本、UI 数据契约及人工证据审查记录。

> 阅读方法、来源和复现说明 →

状态：[ ] 待审核

---

## 14. 项目页：Explorer 入口

### 14.1 标题与正文

**拟用英文**

> 08 · EXPLORE THE 2025 RESULTS
> Inspect the complete Pulse set.

> The case studies show selected contrasts. The Explorer exposes all 425 v1 Pulses across the 12 research sensors, including filters, direction, scope, hourly participation, evidence status and sensor-level context.

**中文含义**

> 08 · 探索 2025 年结果
> 检查完整 Pulse 结果集。

> 案例研究展示经过选择的对照。Explorer 展示 12 个研究传感器中的全部 425 个 v1 Pulse，包括筛选、方向、范围、逐小时参与、证据状态和传感器层背景。

修改原因：替换 `The cases are an argument. The Explorer is the audit trail.` 这类口号。

### 14.2 按钮与图注

| 拟用英文 | 中文含义 |
|---|---|
| Open the New Year case | 打开新年案例 |
| INTERACTIVE 2025 RESULT EXPLORER | 2025 年交互式结果 Explorer |

删除开发路由提示 `SELECTED CASE HANDOFF → /explore?pulse=…`。

状态：[ ] 待审核

---

## 15. 项目页：作者与 AI 协作声明

根据用户在定位稿中的补充，公开表达采用“作者主导、AI 协助、确定性代码计算、人工最终控制”的结构。

### 15.1 章节标题与正文

**拟用英文**

> 09 · RESEARCH PROCESS
> Human-directed research, developed with AI assistance.

> Yoreny defined the research topic, designed the project and interaction architecture, directed each stage of development, and reviewed outputs against the intended research and visual direction. AI tools assisted with analytical implementation, code, source discovery, documentation and testing. The published results come from deterministic scripts and explicit rules rather than an AI prediction model.

**中文含义**

> 09 · 研究过程
> 由人主导、在 AI 协助下完成的研究。

> Yoreny 确定研究主题，设计项目与交互架构，指导各阶段开发，并持续依据预期研究和视觉方向审核输出。AI 工具协助分析实现、代码、来源发现、文档和测试。公开结果来自确定性脚本和明确规则，而不是 AI 预测模型。

### 15.2 四项分工

| 拟用英文标题 | 拟用英文细节 | 中文含义 |
|---|---|---|
| Research direction + design | Topic, project architecture, interaction design and final direction · Yoreny | 选题、项目架构、交互设计和最终方向由 Yoreny 负责 |
| Analytical + software implementation | Methods, data processing and interface development · AI-assisted, author-directed | 方法、数据处理和界面开发由作者指导并使用 AI 协助 |
| Evidence review | Public-source review, case interpretation and uncertainty decisions · Yoreny | 公开来源审查、案例解释和不确定性决定由 Yoreny 负责 |
| Verification + editorial control | Automated consistency tests, iterative review and final approval | 自动一致性测试、持续审核和最终批准 |

### 15.3 简短披露

**拟用英文**

> AI supported the research process; it was not the analytical model and did not independently determine causal explanations.

**中文含义**

> AI 支持了研究过程；它不是分析模型，也没有独立决定因果解释。

删除当前 `for research-degree applications` 和内部路由式页脚；项目应解释工作本身，不解释网页申请用途。

状态：[ ] 待审核

---

## 16. Explorer：顶栏与筛选器

### 16.1 顶栏

| 位置 | 拟用英文 | 中文含义 |
|---|---|---|
| 导航 | Project | 项目叙事 |
| 当前页 | Explore | 数据探索 |
| 方法 | Method | 独立方法论页 |
| 计数 | `{n} Pulses in view` | 当前视图中有 n 个 Pulse |
| 默认状态 | Annual overview | 年度概览 |
| 按钮 | Filters | 筛选器 |
| 按钮 | Clear selection | 清除当前选择 |
| 按钮 | Reset filters | 重置筛选条件 |

状态：[ ] 待审核

### 16.2 筛选器

| 分组 | 拟用英文 | 中文含义 |
|---|---|---|
| Month | All months / Jan…Dec | 月份 / 全部月份 |
| Direction | All / Above baseline / Below baseline | 全部 / 高于基线 / 低于基线 |
| Peak scope | All scopes / Localized / Broad / Network-wide | 峰值范围 / 全部 / 局部 / 广泛 / 网络范围 |
| Evidence review | All review states / Manually reviewed / Outside manual review set | 证据审查 / 全部 / 已人工审查 / 不在人工审查案例集 |

删除 `none means all`，使用明确的 `All` 选项。Explorer 当前仍显示 `Match pending review`，但发布数据已经完成人工审查；应改成真实状态。

状态：[ ] 待审核

---

## 17. Explorer：空间视图

### 17.1 标题

**拟用英文**

> GEOGRAPHIC SENSOR POSITIONS
> 12 central-Melbourne research sensors

**中文含义**

> 传感器地理位置
> 12 个中央墨尔本研究传感器。

### 17.2 图例

| 拟用英文 | 中文含义 |
|---|---|
| Selected Pulse member | 所选 Pulse 成员 |
| Selected sensor | 所选传感器 |
| Ring size = participation in Pulses currently in view, not pedestrian volume | 圆环大小表示当前视图 Pulse 的参与次数，不表示行人数量 |

### 17.3 SVG 无障碍文字

**拟用英文标题**

> Central-Melbourne research sensor locations

**拟用英文描述**

> A longitude–latitude projection of 12 purposively selected sensor locations. Two near-coincident sensors are offset and connected to their geographic anchors. The display does not interpolate a continuous surface or show street boundaries.

**中文含义**

> 12 个目的性选择传感器位置的经纬度投影。两个几乎重合的传感器被视觉错开，并通过连线连接其真实地理锚点。视图不插值连续表面，也不显示街道边界。

### 17.4 传感器无障碍标签

**拟用英文模板**

> `{location}`, sensor `{id}`, `{coverage}%` 2025 coverage, member of `{count}` Pulses currently in view.

**中文含义**

> 地点、传感器 ID、2025 年数据覆盖率，以及它参与当前视图中多少个 Pulse。

状态：[ ] 待审核

---

## 18. Explorer：年度概览 Inspector

### 18.1 标题

> ANNUAL OVERVIEW
> 2025 study network

中文：年度概览 / 2025 研究网络。

### 18.2 数据字段

| 拟用英文 | 中文含义 |
|---|---|
| Study period | 研究时间范围 |
| Research sensors | 研究传感器数 |
| Pulses under v1 rules | v1 规则下 Pulse 总数 |
| Pulses in view | 当前视图 Pulse 数 |
| Above / below baseline | 高于 / 低于基线 |
| Localized / broad / network-wide at peak | 峰值范围为局部 / 广泛 / 网络范围 |
| Missing sensor-hours | 缺失传感器—小时 |
| Pulses in manual review set | 纳入人工审查案例集的 Pulse 数 |

注：人工审查共有 16 个案例，但 Pulse Explorer 中只有 15 个被审查 Pulse；另一个是孤立 Episode，不能在这里写成 16 个 Pulse。

### 18.3 当前筛选

| 拟用英文 | 中文含义 |
|---|---|
| Current filters | 当前筛选条件 |
| All 2025 Pulses are visible. | 全部 2025 年 Pulse 均可见 |
| `{visible}` of 425 Pulses are visible. | 425 个 Pulse 中当前显示多少个 |

### 18.4 边界说明

**拟用英文**

> Pulse counts describe rule-defined departures from local baselines, not total pedestrian volume or a count of verified city events.

**中文含义**

> Pulse 数量描述相对本地基线的规则定义偏离，不表示行人总量，也不表示经过确认的城市事件数量。

状态：[ ] 待审核

---

## 19. Explorer：传感器 Inspector

### 19.1 标题与操作

| 拟用英文 | 中文含义 |
|---|---|
| SENSOR DETAILS | 传感器详情 |
| Close sensor | 关闭传感器详情 |

### 19.2 基础字段

| 拟用英文 | 中文含义 |
|---|---|
| Sensor ID | 传感器 ID |
| Coordinates | 坐标 |
| 2025 coverage | 2025 数据覆盖率 |
| Available / missing hours | 有效 / 缺失小时 |
| Location type | 地点类型 |

### 19.3 与所选 Pulse 的关系

| 拟用英文 | 中文含义 |
|---|---|
| This sensor participates in the selected Pulse. | 该传感器参与所选 Pulse |
| This sensor does not participate in the selected Pulse. | 该传感器不参与所选 Pulse |

### 19.4 研究信息

| 章节 | 拟用英文 | 中文含义 |
|---|---|---|
| Selection | Selected for the central-Melbourne study network because: `{inclusionReason}` | 因相应覆盖和选择理由纳入中央墨尔本研究网络 |
| Baseline cells | `{n}` weekday–hour baseline cells | n 个星期—小时基线单元 |
| Sample size | Eligible sample size per cell: `{min}`–`{max}`; sample-sufficiency labels: `{labels}` | 每个单元有效样本范围及样本充足度标签 |
| Pulse participation | Member of `{n}` Pulses across the 2025 result set | 参与 2025 结果集中 n 个 Pulse |

删除两个开发占位提示：

- `Full rhythm visualisation follows in a later slice.`
- `No confirmed media mapping yet.`

它们不是研究内容，也不应出现在发布界面。

状态：[ ] 待审核

---

## 20. Explorer：Pulse Inspector

### 20.1 标题

> SELECTED PULSE
> `{start date and time}`

中文：所选 Pulse / 开始日期和时间。

### 20.2 核心字段

| 拟用英文 | 中文含义 |
|---|---|
| Direction | 方向 |
| Above baseline / Below baseline | 高于基线 / 低于基线 |
| Peak scope | 按峰值参与分类的范围 |
| Duration | 持续时间 |
| Peak simultaneous sensors | 峰值同时活动传感器数 |
| Sensors involved during period | 全时段参与过的传感器并集 |
| Sensor Episodes | 组成该 Pulse 的传感器 Episode 数 |
| Strength band | 强度分档 |
| Evidence-review state | 证据审查状态 |

字段下增加一条简短说明：

**拟用英文**

> Scope is classified from peak simultaneous participation; the number of active sensors can change each hour.

**中文含义**

> 范围根据峰值同时参与数分类；活动传感器数可以逐小时变化。

### 20.3 Context

| 拟用英文 | 中文含义 |
|---|---|
| Public holiday | 公共假期 |
| School holiday | 学校假期 |
| Daylight-saving transition | 夏令时切换 |
| Weather in Pulse window | Pulse 时间窗内天气 |
| Planned works | 计划工程 |
| No overlap recorded | 未记录到重叠 |
| Not assessed in v1 | v1 未评估 |

不再使用 `provisional weather disruption overlap`，因为界面展示的是当前发布背景状态。

### 20.4 Evidence

章节标题：

> REVIEWED EVIDENCE · `{count}` SOURCES

每条证据显示：

- 来源名称；
- 证据名称；
- 时间重叠小时；
- 空间相关性；
- 方向一致性；
- **人工 review status**；
- 必要时显示人工 notes 和 warnings；
- `Open source ↗`。

删除：

- `Automatic match confidence` 作为主要公开判断；
- 对已完成人工审查记录仍显示 `Pending review`。

无证据时：

**拟用英文**

> No evidence item is linked because this Pulse is outside the purposive manual-review set.

**中文含义**

> 该 Pulse 不在目的性人工审查案例集中，因此没有关联证据条目。

边界说明：

> Reviewed overlap describes documented context; it does not establish causation.
> 经审查的重叠描述有记录背景，但不能确定因果关系。

### 20.5 Quality + provenance

| 拟用英文 | 中文含义 |
|---|---|
| Baseline sample sufficiency | 基线样本充足度 |
| Weather data missing in `{n}` Pulse hours | Pulse 中 n 个小时缺少天气数据 |
| Processing version | 处理版本 |

不将 `high confidence` 单独翻译成科学置信度；界面使用 `baseline sample sufficiency: high`。

状态：[ ] 待审核

---

## 21. Explorer：年度时间轴

### 21.1 标题与图例

| 拟用英文 | 中文含义 |
|---|---|
| ANNUAL NAVIGATION | 年度导航 |
| 2025 Pulse timeline | 2025 Pulse 时间轴 |
| ▲ Above baseline | 高于基线 |
| ▼ Below baseline | 低于基线 |
| • Manually reviewed | 已人工审查 |

将目前已经过期的 `Pending evidence review` 改为真实发布状态。

### 21.2 轨道

| 拟用英文 | 中文含义 |
|---|---|
| Network-wide at peak | 峰值为 network-wide |
| Broad at peak | 峰值为 broad |
| Localized at peak | 峰值为 localized |

### 21.3 空结果与无障碍标签

**空结果英文**

> No Pulses match the current filters. Change or reset the filters to restore the annual view.

**中文含义**

> 当前筛选条件没有匹配 Pulse。修改或重置筛选条件即可恢复年度视图。

**Pulse 按钮英文模板**

> `{start}` to `{end}`; `{direction}` baseline; `{peak scope}`; `{duration}` hours; peak `{max}` simultaneous sensors; `{evidence-review state}`.

**中文含义**

> 开始至结束时间、相对基线方向、峰值范围、持续小时、峰值同时传感器数和证据审查状态。

状态：[ ] 待审核

---

## 22. Explorer：加载、错误和操作状态

这些是功能性文案，不承担研究叙事。

| 拟用英文 | 中文含义 |
|---|---|
| Loading sensor positions… | 正在加载传感器位置 |
| Loading annual summary… | 正在加载年度摘要 |
| Loading Pulse timeline… | 正在加载 Pulse 时间轴 |
| Loading details… | 正在加载详情 |
| Retry | 重试 |
| Return to project | 返回项目页 |
| `{n}` Pulses match the current filters. | n 个 Pulse 符合当前筛选条件 |
| The published UI data files are out of sync. Regenerate or redeploy the dataset. | 已发布 UI 数据文件版本不一致，需要重新生成或部署数据集 |

状态：[ ] 待审核

---

## 23. 独立方法论页面

### 23.1 页面定位

页面不是论文仿制品，也不是开发文档堆叠。它是一篇面向非专业读者的解释型研究文章：先说明问题，再逐步引入数据单位、基线、公式、Episode、Pulse、证据和结论边界。

用户上传的 `docs/review-input/methodology-notes.zh-CN.txt` 是英文正文主来源。除下列统一编辑外，不重新生成另一篇竞争性英文稿：

- 统一 `day of week` 为 `weekday`；
- 首次出现 `raw MAD` 时解释它不是传统概率 z-score；
- 将 `representative sensors` 改为 `research sensors`；
- 将 `spatial Pulse` 改为 `cross-location Pulse`，需要讨论空间时再具体解释；
- 将限制统一整理为 `Current scope and opportunities for further study`；
- 删除重复因果免责声明，只在相关章节保留完整解释；
- 删除与前文重复但没有新增信息的总结段；
- 保持 TXT 中所有数字和算例，实施前与当前数据再次核对。

### 23.2 Hero

**拟用英文**

> METHODOLOGY
> From hourly footfall to interpretable urban Pulses.

> A plain-language account of how 2025 pedestrian observations become local baselines, strong departures, sensor Episodes, cross-location Pulses and manually reviewed cases.

**中文含义**

> 方法论
> 从逐小时行人计数到可解释的城市 Pulse。

> 用普通语言说明 2025 年行人观测如何成为本地基线、强偏离、传感器 Episode、跨地点 Pulse 和人工审查案例。

### 23.3 文章章节映射

| 章节 | 拟用英文标题 | 中文标题与含义 | 英文正文来源 |
|---:|---|---|---|
| 1 | Why study urban rhythms? | 为什么研究城市节律：解释孤立计数为什么没有足够意义，以及本项目的核心问题 | 用户 TXT 第 1 节 |
| 2 | Why these 12 sensors? | 为什么选择这 12 个传感器：覆盖审查、目的性选择和总体边界 | 用户 TXT 第 2 节 |
| 3 | From raw data to an hourly panel | 从原始数据到逐小时面板：105,120 个传感器—小时、16 个缺失和 DST 简化 | 用户 TXT 第 3 节 |
| 4 | What does “usual” mean for a place? | 一个地点的“通常状态”是什么：传感器 × 星期 × 小时基线及排除规则 | 用户 TXT 第 4 节 |
| 5 | Why use the median and raw MAD? | 为什么使用中位数和原始 MAD：公式、解释和置信度含义 | 用户 TXT 第 5 节 |
| 6 | How does an hour become an Episode? | 一个小时怎样形成 Episode：分档、review-ready 和严格连续规则 | 用户 TXT 第 6 节 |
| 7 | How do multiple locations form a Pulse? | 多个地点怎样形成 Pulse：至少三个传感器、同方向、范围分类和非空间聚类边界 | 用户 TXT 第 7 节 |
| 8 | Why are there 425 Pulses? | 为什么结果是 425：规则链和传感器阈值敏感性 | 用户 TXT 第 8 节 |
| 9 | Worked example: Town Hall West on New Year's Day | 完整算例：Town Hall West 从 6,217 计数到 Episode 和 Pulse | 用户 TXT 第 9 节 |
| 10 | How is external evidence reviewed? | 外部证据怎样审查：先检测后解释、64 条记录和非因果边界 | 用户 TXT 第 10 节 |
| 11 | What can the project conclude? | 项目能够得出什么：直接结果、案例发现和方法贡献 | 用户 TXT 第 11 节 |
| 12 | Current scope and opportunities for further study | 当前研究范围和进一步研究：季节、空间、阈值、时间和网络扩展 | 用户 TXT 第 11 节后半部分重新编排 |
| 13 | Research process and AI assistance | 作者、AI、代码和人工审查：真实分工与责任边界 | 本文件第 15 节 |
| 14 | Reproduce and inspect | 复现与检查：数据版本、脚本顺序、验证命令和 GitHub 文档入口 | 当前仓库和 README |

### 23.4 阅读辅助组件

只增加服务理解的原生页面元素：

- 章节目录；
- 流程图；
- 公式卡；
- Town Hall West 逐步算例；
- 两张阈值敏感性表；
- `Observed / Derived / Manually reviewed` 三类信息标记；
- 当前范围与未来研究列表；
- 返回项目页和打开 Explorer 的链接。

不增加新视觉依赖，不建立复杂交互实验室，不重做现有设计系统。

### 23.5 方法论页底部操作

| 拟用英文 | 中文含义 |
|---|---|
| Return to the project | 返回项目页 |
| Inspect the 2025 Pulses | 检查 2025 年 Pulse |
| View source and reproducibility notes | 查看源码和复现说明 |

状态：[ ] 待审核

---

## 24. README 内容架构

README 服务于代码仓库，不复制整篇叙事页面。

### 24.1 开头定位

**拟用英文**

> Melbourne Urban Pulse is an interpretable urban data study and interactive research project built from 2025 public pedestrian sensor observations in central Melbourne.

> The workflow compares hourly counts with sensor-specific weekday–hour baselines, groups strong consecutive departures into Episodes, and identifies same-direction co-occurrence across at least three research sensors as Pulses. Under the v1 definitions, it produced 425 Pulses and a purposive set of 16 manually reviewed cases.

**中文含义**

> Melbourne Urban Pulse 是一个基于中央墨尔本 2025 年公共行人传感器观测建立的可解释城市数据研究与交互式研究项目。

> 工作流将逐小时计数与传感器自身的星期—小时基线比较，把连续强偏离组成 Episode，并把至少三个研究传感器的同方向共现定义为 Pulse。在 v1 定义下，它产生 425 个 Pulse 和一组包含 16 个案例的目的性人工审查集。

### 24.2 README 章节顺序

1. Research question
2. What the v1 workflow does
3. Published results and interpretation boundary
4. Data sources and sensor scope
5. Processing pipeline
6. Website routes
7. Research process and AI assistance
8. Current scope and opportunities for further study
9. Development and validation commands
10. Documentation

### 24.3 README 删除或改写

- 删除将项目描述为长期 `extensible urban signal interpretation system` 的产品路线；
- 删除尚未实现的 vehicle、cycling、edge-generated sensing 愿景；
- 删除 `Edge-AI-ready` 定位；
- 删除 `2.5D Urban Pulse Field` 作为核心研究概念的表述；
- 将 `64 automatic matches` 改为 `64 manually reviewed evidence records`；
- 将 `12-sensor representative study` 改为目的性中央城区研究网络；
- 将 `approved research thesis` 等内部里程碑语言改成公开可理解的结果；
- 保留数据来源、技术栈、运行命令、验证命令和文档入口；
- 将后续研究写成研究精细化方向，而不是产品功能路线图。

### 24.4 README 人机协作说明

使用项目页第 15 节的短版，不写贡献比例，不写 `AI-generated project`，也不声称所有代码逐行人工审核。

状态：[ ] 待审核

---

## 25. 实现时允许的最小界面修改

这份架构获批后，允许的界面改动只有：

- 新增独立方法论路由并复用现有项目设计语言；
- 替换和重新分段文案；
- 更新导航链接；
- 修正数字标签和证据状态；
- 删除发布界面的开发占位语；
- 为方法论添加原生目录、表格、公式卡和流程图；
- 必要时调整现有 CSS，使较长且准确的文字正常显示；
- 为 Explorer 的已审查状态补充正确的筛选和图例映射。

不允许：

- Figma 重绘；
- 全站视觉重构；
- 新动效系统；
- 新可视化依赖；
- 算法和数据管线扩展；
- 未经审核的新研究主张。

状态：[ ] 待审核

---

## 26. 总体审核清单

- [x] 同意全站语言和术语规则；
- [x] 同意 Metadata；
- [x] 同意本轮不修改 Portfolio 首页；
- [x] 同意项目页 Hero 与研究问题；
- [x] 同意方法简介及公式口径；
- [x] 同意新年案例文案和参与数口径；
- [x] 同意湿天气案例文案；
- [x] 同意活动背景案例文案；
- [x] 同意未解释 Episode 文案；
- [x] 同意“当前范围 + 进一步研究”结构；
- [x] 同意 Explorer 入口文案；
- [x] 同意作者与 AI 协作声明；
- [x] 同意 Explorer 顶栏、筛选、空间视图和 Inspector 文案；
- [x] 同意清除 Explorer 中过期的 pending-review 和开发占位语；
- [x] 同意独立方法论页面结构及以用户 TXT 为英文正文来源；
- [x] 同意 README 重写范围；
- [x] 同意只实施第 25 节列出的最小界面修改。

## 27. 审核通过后的执行顺序

1. 按批准内容修改项目页和 Hero 图注；
2. 修正 Explorer 术语、证据状态和开发占位语；
3. 建立独立方法论页；
4. 重写 README；
5. 核对所有数字和动态标签；
6. 运行 lint、生产构建和 UI 数据验证；
7. 在桌面与移动宽度进行浏览器检查；
8. 输出最终变更清单，由用户进行最后审查。
