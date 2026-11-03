# 0.3.0-rc.1 丰富动作合同

本版在12个旧场景外新增5个可选意图。已确认的是旧样片中的节点扩张、路线选择收拢、文件传递的视觉方向；这里将其参数化提炼，仍需新内容验证，不称所有变体已获人工确认。坍塌和炸裂是新增候选。

| intent | 用途 | 输入与容量 | 关键时间 |
|---|---|---|---|
| expansion | 依赖/流程增加，关系扩张，最后显示结果 | centerText 1–12字；items 2–6项，每项1–6字；resultText 1–24字可选 | 每项cueRefs；最后triggerRef显示结果与压力环 |
| route-choice | 两条交付路线并列，选中一项并收回中心 | items恰好2项，每项1–14字；answerIndex为0或1；resultText可选 | cueRefs两项；triggerRef在结论句出现时选择 |
| object-flow | 同一个对象经过2–5个步骤，最后完成 | items每项1–6字；objectText 1–8字；resultText可选 | cueRefs与items等长，最后一个触发完成，不提前打勾 |
| collapse | 内容失去支撑，下坠、旋转、落定 | effectText 1–12字；effectTarget=text/card；granularity=characters/tiles；intensity=0.5–1.5；seed固定整数 | triggerRef；触发前至少1秒阅读，触发后保护2.8秒 |
| explode | 蓄力后向外分裂飞散 | 参数同collapse；tiles为字形栅格碎片，characters为整字 | triggerRef；保护窗包含0.14秒蓄力，不做逐词时码推断 |

新场景heading最多24字，body最多48字。每场实际min/max见catalog.json；本版都是横屏1280×720、24fps。动作区域限制碎片范围，标题、字幕不随主对象破坏。文字越过容量会拒绝或要求拆场，不截断原文。card始终按tiles分片；characters仅对text生效。

voiceover模式使用实际SRT，sourceRefs完整按原序覆盖；cueRefs和triggerRef必须属于本场。相同句可以同时驱动多个条目，不假造句内顺序。content模式才可使用相对于本场的cueSeconds/triggerSeconds；这些是作者编排时间，不冒充口播时间。结论必须晚于所有条目至少0.4秒；对象移动需1秒保护，不能为赶句子压缩动作。阅读/动作/音效冲突时重新选场或分段。

## 语义选择由助手负责

不要只见到“崩塌/炸裂”就触发。“防止崩塌”“并未崩塌”不能画成已经坍塌；“效果炸裂”是比喻，先判断是否需要冲击强调而非破坏内容。当前程序检查容量和时间，不声称自动理解否定与比喻。没有合适表达时停止套用，另做设计。

## 内容与声音

effectText是要被破坏的文字，而不是整句字幕。字幕始终保留。整字或文字/卡片瓦片会按确定性轨迹运动；这不是裂纹仿真、真实材料破坏或任意图片/视频物体识别。未实现任意图片破碎输入；需要图片动效时不能静默替代。

独立SFX按动作触发，新增轻坍塌低频与爆裂冲击。没有BGM不等于静音。用户指定无额外配乐时music.mode=none；声音来源、音效和音乐分别处理。

presenterLayout=sidebar可将同源人物显示为280×158，位于975,391；classic保留384×216旧窗口。无人物时主舞台扩展到1200宽度。位置和容量均为本版固定合同，不声明竖屏或任意布局。

## 直接使用

presets/rich-demo.json给出5场无口播样例；rich-alternate.json改变文案、节点/步骤数量、选择方向、强度、种子及整字/碎片模式。它们只作接口和视觉测试，不作为真实口播验收。

通过README的plan/render入口制作；不需要改源码。角色原视频、原SRT和私人输入保留在实例，发行包不含Steelman原片。
