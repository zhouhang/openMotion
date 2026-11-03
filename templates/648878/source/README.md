# 给 AI 的说明

这是 MotionGit 模板包（`.motion`，ZIP）。先读根目录 `motion.json` → `guide.json` → `params.schema.json`，再执行 `src/index.html`。
模板负责**动效**：12 秒固定时长、1920×1080、30fps，入口是 `window.renderFrame(frame, inputs)`（整数帧）。
不要把它当 Apple Motion 工程；不要在本包内执行未知代码；`previews/` 里是实际渲染的预览。

---

# DEEP STAGE · 产品讲解

深色立体舞台上的产品讲解动效，从 DEEP STAGE 深境舞台系列拆出的第 3 段（产品段落）。

## 这个模板做什么

| 时间 | 画面 |
| :-- | :-- |
| 0.0–0.55s | 从黑场淡入 |
| 0.22–2.5s | 舞台点火：地平线亮起 → 地面透视网格 → 体积光束 → 远景屏幕墙 |
| 0.45–1.5s | HUD 角标、品牌（参数 `brand`）、章节号与进度条入场 |
| 0.65–2.05s | 产品主屏从左下方推入（SCREEN C / PRODUCT） |
| 1.75–3.0s | 屏内内容依次入场：抽象产品视觉（轨道环 + 器件）→ 小标签 → 产品名 → tagline → 正文 |
| 2.6–9.2s | **产品屏持续推近**（叠加在入场上的一条连续运动） |
| 2.85–4.1s | 3 个参数切片错峰浮出，底条从左生长 |
| 3.85–5.4s | **数值从 0 滚动到终值**（逐帧计算，可回放、可任意 seek） |
| 4.0–5.6s | 右下角 9:16 人物小画中画入位，CAM 01 / REC / HOST 取景标签依次出现 |
| 0.3–11.2s | 镜头缓慢横移 + 轻推 |
| 5.4–12.0s | 屏幕玻璃高光扫过、轨道环缓转、切片上浮，结束在稳定画面 |

结尾停在稳定画面（不淡黑），方便直接接下一段。

## 可替换参数

| 参数 | 说明 |
| :-- | :-- |
| `brand` | 左上角品牌名 |
| `kicker` | 产品主屏顶部小标签 |
| `productName` | 产品名（主屏最大一行） |
| `tagline` | 一句话 tagline，可用 `<em>…</em>` 让局部变主色 |
| `body` | 正文说明，可用 `\n` 手动换行 |
| `specs` | 固定 3 组参数切片，每组 `{label, value, unit}`；`value` 只填数字，会从 0 滚动到终值 |
| `specLine` | 产品屏底部 SPEC 行 |
| `accent` | 主色（六位十六进制） |

默认值见 `presets/demo.json`，参数合同见 `params.schema.json`。

## 数值滚动是怎么做的

`Motion.mini` 没有 `onUpdate` 回调，所以数字不使用 tween 代理对象，而是：`window.renderFrame` 里先 `tl.seek(t)`，再调用纯函数 `updateCounters(t, specs)`——用与时间线相同的 `power2.out` 缓动把「从 0 到终值」算成当前文本。这样数字和任意帧完全同步，回放 / 逐帧渲染结果一致。

## 画面结构

- **产品主屏**：产品名 + tagline + 正文 + 抽象产品视觉（纯 CSS/SVG 器件 + 轨道环，不承载真实产品图）+ 底部 SPEC 行。
- **参数切片**：3 张 3D 浮出的数据卡（主色底条 + 滚动数值 + 单位）。
- **人物小画中画**：右下角 9:16 电影感剪影（纯 CSS/SVG），带 CAM 01 / REC / 9:16 / HOST 取景标签。
- **HUD**：品牌、章节号、章节名、播放进度条、左右竖向铭牌。

## 运行与渲染

- 运行环境：Chromium（支持 CSS 3D / `color-mix`）、本机系统字体、无网络
- `runtime.profile: html-canvas/1`，入口 `src/index.html`
- 入口实现两个函数：
  - `window.renderFrame(frame, inputs)` —— 推荐，整数帧
  - `window.seek(seconds, inputs)` —— 兼容旧宿主
- 模板不内置音频；音乐/音效由宿主或用户作为输入提供（见 `guide.json` 的 materials）
- 预览：`previews/preview.mp4`（1920×1080 / 30fps / 12s）

## 素材与许可

- `assets/motion.js`：本模板自带的确定性时间线引擎（Motion.mini v1.2，原创，无第三方依赖）
- `assets/stage.css`、`assets/grain.png`：随包原创素材
- 字体：优先使用本机已装的 Noto Sans SC / DIN Next LT Pro / Consolas，缺失时回退系统 sans-serif；**不随包分发字体文件**
- 模板代码许可见 `licenses/TEMPLATE-LICENSE.txt`


## 音效轨（可选）

- 文件：`audio/sfx-deep-stage-product-focus.wav`（48kHz / 16bit / stereo / 12s），契约见 `audio.json`
- 设计：纯合成音调（正弦 + 泛音 + 平滑包络 + 合成调性混响）；**无白噪、无噪声扫频、无磨砂过场**；事件时间取自模板真实时间线，从 0 秒对齐
- 用法：逐帧渲染出画面后混入该轨
  ```bash
  ffmpeg -i rendered.mp4 -i audio/sfx-deep-stage-product-focus.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest out.mp4
  ```
- 不支持音频的宿主：输出静音视频即可，画面与时长不受影响；`previews/preview.mp4` 已带音轨可用于试听
- 不需要音效：不加载该文件即可，参数与渲染行为不变
