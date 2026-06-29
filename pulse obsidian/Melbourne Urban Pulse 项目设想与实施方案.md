
## 1. 项目简介

**Melbourne Urban Pulse** 是一个面向智慧城市基础设施的交互式城市数据可视分析项目。它不是一个普通的人流 dashboard，也不是单纯展示图表的作品集页面，而是一个研究型原型：通过多源城市信号解释墨尔本 CBD 的活动节奏、空间差异、异常变化和潜在基础设施压力。

项目第一阶段会以 **City of Melbourne pedestrian sensors** 作为主要可观测信号，因为人流数据公开、稳定、时空粒度清晰，适合建立完整的数据管道和分析方法。但项目本体不应被限制为“人流分析”。人流只是第一个被实现的 urban signal。后续同一套框架可以扩展到车流、公共交通、骑行、停车、事件、天气、环境压力和边缘 AI 传感器信号。

项目希望回答的核心问题是：

**城市在不同时间、地点和背景条件下如何产生不同的“脉冲”？这些脉冲是日常节奏、环境影响、节假日效应、特殊事件，还是潜在基础设施压力的表现？**

---

## 2. 研究定位

本项目可以定位为：

**一个面向智慧城市基础设施的可视分析研究原型，用于把公共城市数据与未来可扩展的边缘感知信号转化为可解释的城市活动模式。**

它处在以下几个方向的交叉处：

- Smart Infrastructure
    
- Urban Computing
    
- HCI / UX for Complex Systems
    
- Data Visualisation / Visual Analytics
    
- Lightweight Urban Data Engineering
    
- Edge-AI-ready Urban Sensing Interfaces
    

项目不应该虚假宣称已经实现真正的 Edge AI 推理。更合理的说法是：当前版本会设计一个 **edge-signal-ready data model**，让未来可以接入来自摄像头、IoT 节点或资源受限边缘设备的信号，例如人流密度估计、车流异常、环境舒适度和基础设施压力指标。

也就是说，当前项目主要做的是：

**城市感知信号的解释层与可视化层。**

---

## 3. 核心概念：Urban Signal Interpretation System

项目不应从“有什么数据就画什么图”出发，而应从“我们想解释什么城市现象”出发。

建议将系统抽象为五个层次：

### 3.1 Mobility Pulse

表示城市活动本身。

第一版实现：

- Pedestrian flow
    

后期扩展：

- Vehicle flow
    
- Public transport activity
    
- Cycling activity
    
- Parking occupancy
    
- Crowd density proxy
    

重点是设计统一的 signal schema，让不同类型的城市活动都可以接入同一框架。

### 3.2 Environmental Context

表示天气与环境背景。

可包含：

- Temperature
    
- Apparent temperature
    
- Rainfall
    
- Wind speed
    
- Humidity
    
- Weather condition
    

输出指标可以包括：

- Weather Comfort Score
    
- Weather Disruption Flag
    

### 3.3 Calendar Rhythm

表示制度性时间节奏。

可包含：

- Weekday / weekend
    
- Public holidays
    
- School terms
    
- University semesters
    
- Daylight saving time
    
- Season
    

这层用于解释为什么某些看似异常的城市活动其实可能是日历结构导致的正常变化。

### 3.4 Event and Disruption Layer

表示特殊事件或扰动。

可包含：

- Festivals
    
- Sports matches
    
- Concerts
    
- Protests
    
- Transport disruptions
    
- Road closures
    
- Extreme weather warnings
    
- Construction works
    

第一版可以先做手动标注或有限事件记录，后续再考虑自动化数据源。

### 3.5 Infrastructure Pressure Interpretation

这是最终解释层。

它回答：

- 当前活动是否高于正常基线？
    
- 这是常规城市节奏，还是异常？
    
- 是否可能与天气、假期、学期、事件有关？
    
- 是否形成局部基础设施压力？
    
- 如果这些信号来自未来 edge sensors，界面应如何解释？
    

这一层输出：

- Urban Pulse Index
    
- Baseline Deviation
    
- Anomaly Score
    
- Infrastructure Pressure Proxy
    
- Confidence Score
    
- Explanation Card
    

---

## 4. 核心视觉设想：2.5D Urban Pulse Field

项目可以设计一个核心视觉模块：

**2.5D Urban Pulse Field**

不同 sensor 有不同地理位置。我们可以将传感器的位置映射到城市平面上，并用高度、光晕、波纹或柱状峰值表示某个时刻的活动强度、异常程度或基础设施压力。

它不是完整 3D 城市模型，也不是精确地理地形，而是一个基于传感器信号生成的 **spatial-temporal activity field**。

基本逻辑是：

- x / y：传感器在城市平面中的位置
    
- z / height：活动强度、偏离程度、pulse score 或 anomaly score
    
- time：通过时间滑块展示城市脉冲如何随时间变化
    
- context：通过旁边的信息面板解释天气、假期、事件和异常原因
    

第一版建议不要直接做完整连续插值表面，而是先做：

- Sensor-based 2.5D pulse spikes
    
- Ripple circles
    
- Time slider
    
- Context explanation panel
    

后续再扩展为：

- Gaussian influence field
    
- Interpolated pulse surface
    
- Anomaly surface
    
- Edge signal simulation layer
    

方法论上必须说明：如果生成连续波动面，它是 derived / interpolated field，不是直接观测到的真实连续城市状态。远离 sensor 的区域应表现出更低 confidence。

---

## 5. 数据层设计

### 5.1 第一版核心数据

MVP 推荐使用：

1. **City of Melbourne pedestrian counts**
    
    - 每小时人流计数
        
    - 作为第一个 mobility signal
        
2. **Pedestrian sensor metadata**
    
    - sensor_id
        
    - sensor name
        
    - latitude / longitude
        
    - status
        
    - direction
        
    - installation context
        
3. **Historical weather**
    
    - temperature
        
    - apparent temperature
        
    - rainfall
        
    - wind speed
        
    - humidity
        
    - weather condition
        
4. **Victorian public holidays / important dates**
    
    - public holidays
        
    - school terms
        
    - daylight saving changes
        
    - potentially university semester markers
        
5. **Manually curated event / disruption notes**
    
    - only for selected anomalies
        
    - used for UI explanation
        
    - should be labelled as manually verified or exploratory
        

### 5.2 后续可扩展数据

后续可以加入：

- Vehicle flow
    
- Cycling data
    
- Public transport / GTFS
    
- Parking occupancy
    
- Road closures
    
- Major events
    
- Air quality
    
- Noise or environmental sensing
    
- Edge AI simulated outputs
    
- Real-time urban sensor streams
    

但第一版不应一开始就加入太多数据。第一阶段重点是建立清晰的方法论和可运行 vertical slice。

---

## 6. 指标与参数设计

项目的技术厚度不应来自堆工具，而应来自清晰的指标设计。

建议第一版包含以下指标：

### 6.1 Activity Intensity

表示某个地点和时间的活动强度。

可以基于：

- raw count
    
- normalized count
    
- percentile rank
    

### 6.2 Baseline Deviation

表示当前活动相对正常模式的偏离。

推荐 baseline 方式：

- group by sensor_id + weekday + hour
    
- 使用 median 作为正常基线
    
- 使用 IQR 或 standard deviation 表示波动范围
    

### 6.3 Anomaly Score

用于判断某个时间点是否异常。

可用方法：

- z-score
    
- IQR outlier
    
- rolling median deviation
    
- period-over-period comparison
    

第一版推荐使用可解释方法，不急着上黑箱机器学习模型。

### 6.4 Weather Comfort Score

表示天气对城市活动的影响。

可考虑：

- 18–24°C 为较舒适温度区间
    
- rainfall 降低舒适度
    
- strong wind 降低舒适度
    
- apparent temperature 比 raw temperature 更接近体感
    

### 6.5 Calendar Context Score

表示日历背景。

可包含：

- weekday / weekend
    
- public holiday
    
- school term / break
    
- daylight saving transition
    
- season
    

### 6.6 Urban Pulse Index

综合指标，用于 UI 总览。

它可以是一个 prototype-level composite index，例如：

- mobility activity
    
- baseline deviation
    
- weather comfort
    
- calendar context
    
- anomaly signal
    

需要在 methodology 中说明：权重是原型设计选择，不是经过大规模实证验证的城市科学指标。

### 6.7 Confidence Score

用于表达不确定性。

影响因素可以包括：

- sensor 是否 active
    
- missing data 比例
    
- 是否远离 sensor
    
- event explanation 是否手动验证
    
- 当前 signal 是 real / derived / simulated
    

---

## 7. UI 呈现逻辑

UI 不应该只是图表合集，而应该呈现一条解释链：

1. What happened?
    
2. Where did it happen?
    
3. How unusual is it?
    
4. What contextual factors might explain it?
    
5. How confident is the system?
    
6. What does it imply for smart infrastructure?
    

### 7.1 Landing Page

作用：建立项目概念和视觉基调。

内容：

- Melbourne Urban Pulse 标题
    
- 城市作为 signal system 的解释
    
- 原创墨尔本摄影
    
- movement / weather / calendar / event 作为核心信号
    
- 进入 dashboard 的入口
    

### 7.2 Dashboard

作用：展示核心分析。

模块：

- Urban Pulse Index
    
- 2.5D Urban Pulse Field
    
- Sensor selector
    
- Time slider
    
- Time-series chart
    
- Weather and calendar context
    
- Anomaly explanation cards
    
- Location comparison panel
    

### 7.3 Methodology Page

作用：支撑研究可信度。

内容：

- 数据来源
    
- 数据管道
    
- 数据字段
    
- baseline 方法
    
- anomaly 方法
    
- Urban Pulse Index 计算逻辑
    
- edge signal layer 说明
    
- limitations
    
- future work
    

---

## 8. 图表设计方向

图表应围绕结论设计，而不是为了画图而画图。

### 8.1 Temporal Rhythm

回答：城市什么时候活跃？

图表：

- hourly line chart
    
- weekday-hour heatmap
    
- daily trend
    
- anomaly timeline
    

### 8.2 Spatial Pulse

回答：城市活动在哪里聚集？

图表：

- sensor map
    
- 2.5D pulse field
    
- location ranking bar chart
    
- precinct comparison
    

### 8.3 Context Explanation

回答：天气、假期、学期、事件是否解释变化？

图表：

- weather vs activity scatter
    
- holiday vs normal comparison
    
- school term vs break comparison
    
- event annotation timeline
    

### 8.4 Methodology and Data Quality

回答：这些结果可信吗？

图表或 UI：

- data pipeline diagram
    
- missing data summary
    
- confidence labels
    
- source provenance cards
    

---

## 9. 实施步骤

### Phase 0：Baseline Setup

已完成：

- Next.js scaffold
    
- TypeScript / Tailwind
    
- Python `.venv`
    
- Python packages
    
- JupyterLab
    
- lint / build
    
- GitHub baseline
    

### Phase 1：Project Framing

目标：

- 替换默认 README
    
- 定义研究问题
    
- 定义 MVP 范围
    
- 明确数据源
    
- 明确 signal schema
    
- 创建 docs 初稿
    

产出：

- `docs/data-model.md`
    
- `docs/methodology.md`
    
- `docs/design-rationale.md`
    
- 初版 README
    

### Phase 2：Mock Vertical Slice

目标：

先不抓真实数据，用 mock JSON 验证前端结构。

产出：

- `public/dashboard-data/dashboard_data.json`
    
- TypeScript types
    
- Landing page
    
- Dashboard basic layout
    
- One metric card
    
- One time-series view
    
- One sensor/location view
    
- One explanation card
    

### Phase 3：Real Pedestrian Data Pipeline

目标：

接入真实 pedestrian count 和 sensor metadata。

产出：

- fetch script
    
- validation script
    
- preprocessing script
    
- baseline calculation
    
- anomaly calculation
    
- exported dashboard JSON
    

### Phase 4：Context Data Integration

目标：

加入天气、公共假期、学期、夏令时和事件背景。

产出：

- weather fetcher
    
- calendar fetcher
    
- event annotation structure
    
- context-aware anomaly explanation
    

### Phase 5：Urban Pulse Field

目标：

实现项目核心视觉。

先做：

- sensor-based 2.5D spikes
    
- time slider
    
- pulse score rendering
    
- context explanation
    

后续做：

- interpolated pulse surface
    
- anomaly surface
    
- confidence surface
    

### Phase 6：Research and Portfolio Polish

目标：

让项目适合展示和 RA 申请。

产出：

- polished README
    
- methodology page
    
- screenshots
    
- deployment on Vercel
    
- final visual system
    
- accessibility checks
    
- performance check
    
- limitations and future work
    

---

## 10. 最终目标

项目最终应该呈现出：

1. 一个可运行的交互式城市数据可视分析网站
    
2. 一个清晰的数据处理管道
    
3. 一个可解释的 Urban Pulse 指标体系
    
4. 一个具有视觉识别度的 2.5D Urban Pulse Field
    
5. 一个合理的 edge-AI-ready sensing data model
    
6. 一套说明清楚的 methodology 和 limitations
    
7. 一个能够用于 GitHub portfolio 和 RA 申请的 research artefact
    

这个项目最终不只是为了说明“墨尔本人流哪里多”，而是为了展示：

**如何把分布式城市传感器信号、环境背景、日历节奏和异常事件转化为人可以理解的城市基础设施状态解释。**