# 目标与证据 · 0.4.0-rc.5

本候选重写 opening、demo、recap、grid、chart、metric、overview、brand 八类场景的具体画面与动画；保留另外九类表达。旧包不覆盖。

八类新表达依次为：目标聚焦、证据展台（四种不同动作）、要点归并、四象限定位、差值轨迹、指标游标、三指标关系图、署名落款。绘制基础层与产品场景分离，移除旧浏览器框、输入栏及原镜头函数。证据图等比容纳，字体等比缩放。

## 使用

需要现有 Python 3.11+、Node 22+、Playwright、Chrome/Chromium、FFmpeg/ffprobe。不自动安装，不联网。

```text
python src/adapter.py plan --inputs presets/product-demo.json --out NEW_PLAN_DIR
python src/adapter.py render --inputs presets/product-demo.json --out NEW_RENDER_DIR --playwright-module PLAYWRIGHT_MODULE --browser CHROME_EXECUTABLE
```

输出目录必须不存在。图片、口播与字幕路径相对输入 JSON。默认 product-demo 为72秒，product-alternate 为78秒替换文案与极值数据示范；rich-demo 为五类丰富动作回归示范。无口播示范不能当作口播匹配验收。

保持16:9、1280×720、24fps；全片12–180秒还受每场容量限制。新版八场最短3–5秒，与旧固定38秒编排不直接兼容；不能压缩动作套用旧时间轴。真实口播用 mode=voiceover 及完整原声/SRT，sourceRefs 顺序完整覆盖原字幕，动作按本场真实句起点绑定。

图表为六组0–100数值的独立前后比较；三指标均为百分比，雷达关系图不代表综合评分。证据页无图片时显示抽象示意，不冒充真实证据。坍塌、炸裂与另外七类场景合同见 references/rich-effects.md。

## 来源与许可

见 references/rewrite-provenance.md。此版本是从旧工程演进后重新设计八场，不能称为未接触参考的独立开发。历史参考记录保留。新演示只用新写文案与自绘几何，不含原视频、原音轨、截图或品牌图标。

随包 Noto Sans SC 使用 SIL OFL1.1，保留 licenses/font-OFL.txt；字体加载失败或缺字停止，不回退到未知许可字体。用户图片/视频中的烧录字体需单独核对。

本版本模板代码与发布者有权许可的原创模板内容采用MIT，完整文本见licenses/TEMPLATE-LICENSE.txt。允许商业使用、修改、免费或有偿分发、再许可和售卖模板及修改版；复制或分发模板代码及其重要部分时须保留版权与许可声明。不强制视频成片显示模板署名；项目署名可自愿保留。Noto字体独立适用SIL OFL1.1，用户素材、商标及第三方内容不因MIT自动获授权。真实来源与历史参考记录保留。

## 配色更新

0.4.0-rc.2 按用户指定 https://open-design.ai/plugins/example-tweaks/ 的公开CSS颜色变量适配：#fafafa底、#262626主文字、#595959次文字、#63fe13荧光绿强调、#218c00可读绿色、#d9d9d9分隔线。荧光绿用于色块和装饰线，绿色小字使用深绿。保留随包Noto字体、动作、时长、文案与声音。未引入网站代码、字体或媒体。

0.4.0-rc.3：依据用户上传的纯色图，将画布底色修正为RGB(246,244,239)/#F6F4EF暖灰米白；保留绿色强调、卡片层次与文字。图片684×192共131328像素均为该值，非从官网样式推测。

## 0.4.0-rc.4

仅定稿许可、项目署名与来源状态，画面运行逻辑、暖灰米白底、全部动作、时钟、声音与字体沿用0.4.0-rc.3。当前仍为候选版；最新连续样片人工验收与平台审核分别记录，不因许可证定稿自动标为通过。

## 0.4.0-rc.5 · MIT

用户于2026-10-19明确选择MIT并允许模板转售。本版本替代0.4.0-rc.4的自定义限制性许可；旧版本授权文本作为历史保留，不把MIT的变更追写进旧包。画面、字体、时钟和音效不变，平台作者身份以实际账号为准。
