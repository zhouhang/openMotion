# 给 AI 的说明

这是 MotionGit 模板包（`.motion`，ZIP）。先读根目录 `motion.json` → `guide.json` → `params.schema.json`，再执行 `src/index.html`。
模板负责**动效**：10 秒固定时长、1920×1080、30fps，入口是 `window.renderFrame(frame, inputs)`（整数帧）。
不要把它当 Apple Motion 工程；不要在本包内执行未知代码；`previews/` 里是实际渲染的预览。

---

# DEEP STAGE · 媒体素材墙

深色立体舞台上的「素材墙」动效，从 DEEP STAGE 深境舞台系列拆出的第 5 段（媒体素材）。

## 这个模板做什么

| 时间 | 画面 |
| :-- | :-- |
| 0.0–0.45s | 从黑场淡入（入场余量） |
| 0.1–2.2s | 地平线亮起 → 地面透视网格 → 体积光束 → 远景屏幕墙点亮 |
| 0.35–1.6s | HUD 与左上角标题角标入场 |
| 0.95–2.45s | 六张卡（2 行 3 列，各自不同 z 纵深 / rotateY）从深处错峰落位：opacity + scale + y 三段同步收 |
| 1.25–2.65s | 每张卡上方的 `MEDIA 0X` 挂签依次跟上 |
| 2.5–9.9s | 落位后六张卡各自极缓慢浮动（约 1.4px/s，错峰、幅度很小） |
| 0.8–10.0s | 镜头持续后拉（一条连续运动），结尾仍在缓慢移动，不会停成静态 PPT |
| 2.7–3.6s | 底部字幕带上浮（`caption` 为空时整条隐藏） |
| 4.2–9.6s | 一道高光缓慢掠过画面 |

## 六张卡是什么

缩略图不是外部图片，全部是**纯 CSS / SVG 程序化生成的抽象电影感静帧**（每张设计尺寸 420×236，显示 480×270）：

| 卡 | 手法 |
| :-- | :-- |
| 01 金属微距 | 三层 `conic-gradient` 圆环 + `mask` 挖空 + 高光斑点 |
| 02 城市夜景 | SVG 楼群剪影 + 模糊滤镜 + 暖色 bokeh 光斑 |
| 03 光轨 | SVG 贝塞尔曲线 + 多段渐变描边 + 模糊分层 |
| 04 丝绸褶皱 | SVG 渐变褶皱面 + 细高光脊线 + 织物纹理叠加 |
| 05 星云 | 多层径向渐变云团 + `blend-mode: screen` + 星点 |
| 06 建筑格栅 | 透视 `rotateY` 的重复渐变墙面 + 光束与光晕 |

## 可替换参数

| 参数 | 说明 |
| :-- | :-- |
| `wallTitle` | 素材墙标题（左上角角标） |
| `items` | 6 条 `{label, tag}`：卡片中文名 + 英文标签 |
| `wallKicker` | 标题上方小标签 |
| `brand` | 左上角品牌名（同时作为左侧竖排小字） |
| `chapter` / `screenLabel` | 右上角章节号（`05 / 06`）/ 章节名 |
| `meta` | 右下角角标 |
| `caption` | 底部字幕，可用 `<em>…</em>` 让局部变主色 |
| `accent` | 主色（六位十六进制） |

默认值见 `presets/demo.json`，参数合同见 `params.schema.json`。

## 布局约束

- 六张卡的位置、纵深、`rotateY` 是固定的（2 行 3 列的空间布局）；参数只换文案，不换画面。
- 中文名 8 字以内、英文标签 10 字以内，保持全大写最好看。
- 卡片底部的名字/标签是画在静帧上的小字，用来在动效里标出「这是第几张」。

## 运行与渲染

- 运行环境：Chromium（支持 CSS 3D / `color-mix` / SVG 滤镜）、本机系统字体、无网络
- `runtime.profile: html-canvas/1`，入口 `src/index.html`
- 入口实现两个函数：
  - `window.renderFrame(frame, inputs)` —— 推荐，整数帧
  - `window.seek(seconds, inputs)` —— 兼容旧宿主
- 所有动画由 `assets/motion.js` 的 `Motion.timeline()` 生成，`tl.seek(t)` 逐帧驱动，任意帧独立可渲染
- 模板不内置音频；音乐/音效由宿主或用户作为输入提供（见 `guide.json` 的 materials）

## 素材与许可

- `assets/motion.js`：本模板自带的确定性时间线引擎（原创，无第三方依赖）
- `assets/stage.css`、`assets/grain.png`：随包原创素材
- 六张抽象静帧：本模板原创 CSS / SVG 代码，不含任何第三方图片或视频
- 字体：优先使用本机已装的 Noto Sans SC / DIN Next LT Pro / Consolas，缺失时回退系统 sans-serif；**不随包分发字体文件**
- 模板代码许可见 `licenses/TEMPLATE-LICENSE.txt`


## 音效轨（可选）

- 文件：`audio/sfx-deep-stage-media-wall.wav`（48kHz / 16bit / stereo / 10s），契约见 `audio.json`
- 设计：纯合成音调（正弦 + 泛音 + 平滑包络 + 合成调性混响）；**无白噪、无噪声扫频、无磨砂过场**；事件时间取自模板真实时间线，从 0 秒对齐
- 用法：逐帧渲染出画面后混入该轨
  ```bash
  ffmpeg -i rendered.mp4 -i audio/sfx-deep-stage-media-wall.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest out.mp4
  ```
- 不支持音频的宿主：输出静音视频即可，画面与时长不受影响；`previews/preview.mp4` 已带音轨可用于试听
- 不需要音效：不加载该文件即可，参数与渲染行为不变
