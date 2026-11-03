# 给 AI 的说明

这是 MotionGit 模板包（`.motion`，ZIP）。先读根目录 `motion.json` → `guide.json` → `params.schema.json`，再执行 `src/index.html`。
模板负责**动效**：14 秒固定时长、1920×1080、30fps，入口是 `window.renderFrame(frame, inputs)`（整数帧）。
不要把它当 Apple Motion 工程；不要在本包内执行未知代码；`previews/` 里是实际渲染的预览。

---

# DEEP STAGE · 口播主舞台

深色立体舞台上的口播主舞台包装，从 DEEP STAGE 深境舞台系列拆出的第 2 段（口播正文）。

## 这个模板做什么

| 时间 | 画面 |
| :-- | :-- |
| 0.0–0.62s | 从黑场淡入 |
| 0.22–2.5s | 舞台点火：地平线亮起 → 地面透视网格 → 体积光束 → 远景屏幕墙 |
| 0.5–1.6s | HUD 角标、品牌（参数 `brand`）、章节号与进度条入场 |
| 0.6–1.9s | **第一层**：9:16 人物画面入位，剪影里的镜头缓慢推近，CAM 01 / REC / 9:16 / HOST 取景标签依次出现 |
| 0.95–2.2s | **第二层**：主信息屏从右侧错峰入位（SCREEN A / BRIEF） |
| 1.3–2.4s | **第三层**：竖向章节导航屏入位（SCREEN B / CONTENTS） |
| 1.95–3.5s | 主信息屏内容：小标签 → 标题 → 副标题 → 3 条编号要点逐条浮出 |
| 2.15–3.3s | 章节屏六行逐条出现，当前章节（`active`）高亮，左侧进度条生长 |
| 3.7–4.7s | 下三分之一人名条从左滑入（姓名 `presenter` + 职务 `role`） |
| 0.35–13.55s | 镜头一条连续的缓慢横移（带轻微推近），不来回 |
| 5.2–14.0s | 信息屏与章节屏微浮动、光带扫过、尘埃上浮，结束在稳定画面 |

结尾停在稳定画面（不淡黑），方便直接接下一段。

## 可替换参数

| 参数 | 说明 |
| :-- | :-- |
| `brand` | 左上角品牌名 |
| `presenter` | 下三分之一人名条上的姓名 |
| `role` | 人名条下方的职务 |
| `kicker` | 主信息屏顶部小标签 |
| `title` | 主信息屏主标题（可折两行） |
| `subtitle` | 主信息屏副标题 |
| `items` | 固定 3 条编号要点，每条 `{title, body}` |
| `chapters` | 固定 6 条章节，每条 `{name, time}`；当前章由 `active` 决定高亮 |
| `active` | 当前章节序号 1–6 |
| `accent` | 主色（六位十六进制） |

默认值见 `presets/demo.json`，参数合同见 `params.schema.json`。

## 画面结构

- **9:16 人物画面**：纯 CSS/SVG 电影感剪影（双色轮廓光 + 背景散景 + 颗粒），带 CAM 01 / REC / 9:16 / HOST 取景标签，不使用任何图片或视频素材；需要真人素材时由宿主在屏幕框内替换。
- **主信息屏**：标题 + 副标题 + 3 条编号要点，右侧是一组装饰性轨道图（纯 SVG，不承载数据）。
- **章节导航屏**：6 行章节 + 当前章高亮 + 左侧进度轨。
- **下三分之一**：人名 + 职务 + 主色竖条。
- **HUD**：品牌、章节号（`active` / 06）、章节名、播放进度条、左右竖向铭牌。

## 运行与渲染

- 运行环境：Chromium（支持 CSS 3D / `color-mix`）、本机系统字体、无网络
- `runtime.profile: html-canvas/1`，入口 `src/index.html`
- 入口实现两个函数：
  - `window.renderFrame(frame, inputs)` —— 推荐，整数帧
  - `window.seek(seconds, inputs)` —— 兼容旧宿主
- 模板不内置音频；音乐/音效由宿主或用户作为输入提供（见 `guide.json` 的 materials）
- 预览：`previews/preview.mp4`（1920×1080 / 30fps / 14s）

## 素材与许可

- `assets/motion.js`：本模板自带的确定性时间线引擎（原创，无第三方依赖）
- `assets/stage.css`、`assets/grain.png`：随包原创素材
- 字体：优先使用本机已装的 Noto Sans SC / DIN Next LT Pro / Consolas，缺失时回退系统 sans-serif；**不随包分发字体文件**
- 模板代码许可见 `licenses/TEMPLATE-LICENSE.txt`


## 音效轨（可选）

- 文件：`audio/sfx-deep-stage-host-stage.wav`（48kHz / 16bit / stereo / 14s），契约见 `audio.json`
- 设计：纯合成音调（正弦 + 泛音 + 平滑包络 + 合成调性混响）；**无白噪、无噪声扫频、无磨砂过场**；事件时间取自模板真实时间线，从 0 秒对齐
- 用法：逐帧渲染出画面后混入该轨
  ```bash
  ffmpeg -i rendered.mp4 -i audio/sfx-deep-stage-host-stage.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest out.mp4
  ```
- 不支持音频的宿主：输出静音视频即可，画面与时长不受影响；`previews/preview.mp4` 已带音轨可用于试听
- 不需要音效：不加载该文件即可，参数与渲染行为不变
