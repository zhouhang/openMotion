# 给 AI 的说明

这是 MotionGit 模板包（`.motion`，ZIP）。先读根目录 `motion.json` → `guide.json` → `params.schema.json`，再执行 `src/index.html`。
模板负责**动效**：13 秒固定时长、1920×1080、30fps，入口是 `window.renderFrame(frame, inputs)`（整数帧）。
不要把它当 Apple Motion 工程；不要在本包内执行未知代码；`previews/` 里是实际渲染的预览。

---

# DEEP STAGE · 案例数据屏

深色立体舞台上的「案例讲解」数据屏，从 DEEP STAGE 深境舞台系列拆出的第 4 段（案例数据）。

## 这个模板做什么

| 时间 | 画面 |
| :-- | :-- |
| 0.0–0.5s | 从黑场淡入（入场余量） |
| 0.2–1.5s | 地平线亮起 → 地面透视网格 → 体积光束 → 远景屏幕墙点亮；主数据屏从纵深推入 |
| 0.9–2.0s | 屏内小标签、标题入场；3 张 KPI 卡片依次浮出 |
| 1.3–3.1s | KPI 数字从 0 滚动到目标值（按帧纯函数计算，逐帧可寻址） |
| 1.9–3.2s | 图表骨架：图表标题、y 轴刻度（0 / 50 / 100）、虚线网格、改版标记线、月份轴 |
| 2.3–4.6s | 6 根柱图逐根从底部生长（`scaleY` + `transformOrigin: 50% 100%`），最高一根自动主色高亮，柱顶数值随之滚动 |
| 3.5–6.0s | 右侧「改造前 / 改造后」对比副屏滑入；前卡、箭头、后卡依次入场 |
| 4.9–5.8s | 底部字幕带上浮（`caption` 为空时整条隐藏） |
| 3.4–13.0s | 镜头持续缓慢横移 + 轻微推近（一条连续运动），结尾停在稳定画面，便于拼接下一段 |

## 可替换参数

| 参数 | 说明 |
| :-- | :-- |
| `brand` | 左上角品牌名（同时作为左侧竖排小字） |
| `kicker` | 数据屏左上角小标签 |
| `title` | 案例标题 |
| `kpis` | 3 条 `{label, value, prefix, suffix}`，可加 `decimals` |
| `bars` | 6 条 `{label, value}`，`value` 为 0–100 的柱高 |
| `footnote` | 数据脚注（口径 / 范围 / 样本量） |
| `before` | 改造前三行 `{label, value}` |
| `after` | 改造后三行 `{label, value}`（行名与 before 对应） |
| `beforeTitle` / `afterTitle` | 对比卡标题，默认「改造前 / 改造后」 |
| `kpiNote` | KPI 右下角对照说明，默认「VS 2025 同期」 |
| `chartLabel` / `chartRange` | 柱图左上标题 / 右上区间小字 |
| `chartMarker` | 柱图竖虚线标记文案，留空则隐藏标记线 |
| `lockLabel` | 数据屏右上角数据锁定标签 |
| `compareLabel` | 对比副屏顶部小标题 |
| `footTag` | 脚注右侧来源标签 |
| `chapter` / `screenLabel` | 右上角章节号（`04 / 06`）/ 章节名 |
| `meta` | 右下角角标 |
| `caption` | 底部字幕，可用 `<em>…</em>` 让局部变主色 |
| `accent` | 主色（六位十六进制） |

默认值见 `presets/demo.json`，参数合同见 `params.schema.json`。

## 数据与布局约束

- KPI 固定 3 条、柱图固定 6 根、前后对比固定各 3 行；超出请先在文案层合并，不要硬塞。
- 柱图最高的一根会自动切到主色高亮（`cd-bar--hot`），其余为中性蓝。
- 主屏设计尺寸 1160×652，显示为 1050×590；副屏 330×460。文字按显示尺寸排，别靠缩字号解决长文本。
- 标题 20 字以内、KPI 指标名 12 字以内、柱图标签 6 字以内，避免换行溢出。

## 运行与渲染

- 运行环境：Chromium（支持 CSS 3D / `color-mix`）、本机系统字体、无网络
- `runtime.profile: html-canvas/1`，入口 `src/index.html`
- 入口实现两个函数：
  - `window.renderFrame(frame, inputs)` —— 推荐，整数帧
  - `window.seek(seconds, inputs)` —— 兼容旧宿主
- 数字与柱顶数值在 `seek` 之后由纯函数 `updateCounters(t)` 同步，不依赖任何时钟，逐帧可寻址
- 模板不内置音频；音乐/音效由宿主或用户作为输入提供（见 `guide.json` 的 materials）

## 素材与许可

- `assets/motion.js`：本模板自带的确定性时间线引擎（原创，无第三方依赖）
- `assets/stage.css`、`assets/grain.png`：随包原创素材
- 字体：优先使用本机已装的 Noto Sans SC / DIN Next LT Pro / Consolas，缺失时回退系统 sans-serif；**不随包分发字体文件**
- 模板代码许可见 `licenses/TEMPLATE-LICENSE.txt`


## 音效轨（可选）

- 文件：`audio/sfx-deep-stage-case-data.wav`（48kHz / 16bit / stereo / 13s），契约见 `audio.json`
- 设计：纯合成音调（正弦 + 泛音 + 平滑包络 + 合成调性混响）；**无白噪、无噪声扫频、无磨砂过场**；事件时间取自模板真实时间线，从 0 秒对齐
- 用法：逐帧渲染出画面后混入该轨
  ```bash
  ffmpeg -i rendered.mp4 -i audio/sfx-deep-stage-case-data.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest out.mp4
  ```
- 不支持音频的宿主：输出静音视频即可，画面与时长不受影响；`previews/preview.mp4` 已带音轨可用于试听
- 不需要音效：不加载该文件即可，参数与渲染行为不变
