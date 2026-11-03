# 给 AI 的说明

这是 MotionGit 模板包（.motion，ZIP）。先读 `motion.json` → `guide.json` → `params.schema.json`，再执行 `src/index.html`。
模板为 **完整模板（full-template）**：46 秒整条口播包装视频，运行时入口 `window.renderFrame(frame, inputs)`（整数帧）。
`src/index.source.html` 是原 HyperFrames 合成留档；真正入口是 `src/index.html`（含 .motion 运行时 shim）。
本包不处理真人素材，人物画面为 CSS/SVG 占位，可在宿主里替换屏内内容。

---

# DEEP STAGE · 深境舞台完整版（46s / full-template）

六个镜头一条连续镜头运动：开场点火 → 口播主舞台 → 产品讲解 → 案例数据 → 媒体素材墙 → 收尾锁版。

## 可替换参数

共 30 个参数，覆盖整条视频的文案与主色：品牌、片头标题/副标题/角标、口播人名与职务、主信息屏标题与三条要点、产品屏文案与规格、案例屏标题、片尾锁版文案、10 句口播字幕、主色。默认值见 `presets/demo.json`。

## 运行

- 1920×1080 / 30fps / 46 秒固定时长；无网络、无第三方库外链
- `window.renderFrame(frame, inputs)`：按帧渲染；`window.seek(seconds, inputs)` 兼容秒
- 人物画面是纯 CSS/SVG 建模的剪影占位；需要真人视频时在宿主里替换对应屏内容

## 可选音效轨

`audio/sfx-deep-stage-full.wav`（48kHz/16bit/stereo/46s）+ `audio.json` 契约；纯合成音调，无白噪、无噪声扫频。渲染后混入：

```bash
ffmpeg -i rendered.mp4 -i audio/sfx-deep-stage-full.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest out.mp4
```

## 许可

模板代码与随包素材 MIT（`licenses/TEMPLATE-LICENSE.txt`）；GSAP 按 GreenSock 标准许可；字体不随包分发。
