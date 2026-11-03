# 月白图形表达 0.7.0-rc.2

延续已确认的四场分类、搭配、变形和条件判断，增加12种短图解方法。所有short页面3–5秒；16:9、1280×720、24fps。旧模块仅显式legacy重放，原字节保持。

## 制作

读取guide.json、params.schema.json与graphic-contracts.json，根据本期语义组织scene。editorial-demo.json仅为无旁白视觉演示；graphic-demo.json保留旧四场连续样片。私人音频和SRT放在实例assets目录，SRT只用于依据，不显示全片字幕。

```
python src/adapter.py plan /path/inputs.json /path/new-output
python src/adapter.py render /path/new-output --playwright-module /existing/playwright --browser /existing/chrome
```

无需安装新依赖；沿用已有Python、Node、FFmpeg、Chrome和Playwright。无BGM，保留轻动作音效。输入只能使用package/instance相对路径；禁止变速、循环声音或漏掉来源单元。narration.gainDb可在-12至0之间衰减，不能用提高峰值遮盖问题。

## 结构与边界

新图解对象与数量依variant合同选择；参数实际消费标题、图标、标签、说明、动作帧和原文编号。图片可替换为本期PNG/JPG/WebP。缺真实定量依据不生成营养数值；示意原料不声称实际配方。单一标题16字、标签8字、说明24字。新方法不带机器人和引出线。

无carryFrom的graphic页用12帧叠化；四场已支持的carryFrom关系保持实体身份与图形接续。不能给新图解随意声明carryFrom。支持独立随机seek；质量报告区分阅读停留和动作前停顿，不能代替语义或连续声画验收。

新图解与人物画中画组合尚未实测；本次完整口播是纯音频+图形。支持范围仅为横屏中文，不追认任意文案自动高质量编排。

模板原创代码MIT；字体Noto Sans SC按OFL，YuNet按独立MIT，详见licenses。包内无本期私人口播与文稿。已确认的0.7.0-rc.1保持原样。本候选的完整成片与验收证据保存在发行包之外。
`label-question`、`selection`、`calendar`还需提供本期`caption`（最多12字）；其它图解可选，显示文字不从历史成片硬编码。
