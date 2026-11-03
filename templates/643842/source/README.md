# 月白图形表达 0.8.1-rc.1

本候选以0.8.0-rc.2为基线，新增OpenMoji同系列7种食物图片资料。基线清除邮箱后已审核通过（用户确认）；本候选尚未上传或提交审核。

## 本次图片资料更新

- `corn`、`milk`、`carrot`沿用原参数，自动显示随包同系列SVG；对象ID、动作时钟、位置、旋转与缩放入口保持。
- 鸡蛋、地瓜、蛋糕、饮料杯通过已有`kind:image`接口绑定`assets/food/openmoji/*.png`；完整示例见`presets/food-library.json`。
- SVG与660×660透明PNG副本随包，来源、固定版本和摘要见`food-library.json`。牛奶对应牛奶杯，不是牛奶包装；蛋糕不自动替换饼干。
- 原食材组合及碗到饼干的轮廓形变保留，未把图片替换宣称为新增形变能力。
- 背景渐变、字体、动作窗、转场、音效、人物卡片与原场景能力保持。本轮没有合并单独试验的右下角圆形人物布局，也没有导出新视频。
- 图标为CC BY-SA 4.0，须保留署名与该许可；原创代码仍为MIT。见`licenses/OPENMOJI-ATTRIBUTION.md`。
- `previews/food-library.png`为本次静态检查图；`previews/demo.mp4`与原封面是0.8系列历史演示，未重渲染为本次图片库演示。

## 制作入口

需要Python 3.11+、Node.js 22+、FFmpeg/ffprobe及Chrome/Chromium。渲染需要可用的Playwright模块；人物卡片准备需要NumPy、Pillow和OpenCV FaceDetectorYN。请使用自己环境的实际可执行文件与依赖路径；不要照抄作者机器配置。未实际验证的平台见QA.md。

```text
python src/adapter.py plan presets/editorial-card.json /new/instance
python src/adapter.py render /new/instance --playwright-module /installed/playwright-core --browser /installed/chrome
```

第二条命令输出实例目录中的video.mp4。已有输出目录不覆盖，修订请使用新目录。原包可只读；渲染、缓存、声音和人物帧全部写入实例。缺环境依赖时明确报告，禁止假装已经导出。

## 编辑式讲解

在现有输入的根目录加入`presentation`，只支持现有`graphic`短场景。每页3–5秒，最多32页；总时长必须等于逐页帧数合计。场景来源、数量、语义、SRT原文归属与动作窗继续按原合同检查。

```json
{
  "mode": "editorial-card",
  "resolution": "1080p",
  "heading": "知识观察",
  "footer": "本期栏目说明",
  "roleLabel": "讲解 / Presenter",
  "nameLabel": "姓名 / Name",
  "portraitSize": [256, 356],
  "logo": {"scope": "instance", "path": "assets/logo.png"},
  "pageLabels": ["提出问题", "梳理关系", "行动计划"],
  "videos": [
    {"source": {"scope": "instance", "path": "assets/part-01.mp4"}, "crop": "auto"},
    {"source": {"scope": "instance", "path": "assets/part-02.mp4"}, "crop": "auto"}
  ]
}
```

这是根输入中`presentation`字段的示例，不是完整输入。完整结构见params.schema.json和presets/editorial-card.json；pageLabels项数应与本期实际页数一致，也可省略。Logo、页眉、页脚和标注可以省略或按合同置空。文本有字数上限，也会按真实字形测宽；超宽直接停止，不压扁字体或偷偷缩小。编辑式舞台还会逐帧检查实际可见像素；若某个原场景的大容量标签超出新舞台边界，须缩短标签、调整场景或使用原版式，不能默默裁掉内容。

人物窗口固定在右侧，正文独立位于左侧；不宣称此新风格支持任意自动漂浮位置或人物/素材全屏交替。portraitSize为1280×720逻辑坐标，支持宽180–266、高260–366；输出1080p时整体乘1.5，保持比例。输入图片采用等比cover，不拉伸人脸。旧版自动避让圆窗仍通过根`presenter`字段调用，两种人物模式不可同时开启。

### 人物分段、声音和时间

人物画面不会自动生成或调用付费服务。用户自行提供有权使用的人物视频。`videos`按顺序提供，最多64段；单段也适用。

未设置`at`时，必须在根输入绑定独立`narration`原声。每段人物视频音轨与该原声进行波形匹配，相关系数不足0.95即停止。此匹配适合使用同一录音生成的数字人或同源剪辑，不是语义ASR，也不能保证匹配重新配音。若已知准确时码，可为全部分段设置非负`at`（秒），此时不自动匹配；`offset`和`sourceDuration`选择源区间。禁止一部分自动、一部分手动而不说明。

人物素材声音只用于定位，最终不加入第二路人声。根narration为唯一口播，模板动作音效保留；默认不自动添加背景音乐或字幕。没有narration的公开demo只含动作音效；随包角色为原创几何动画，不是真人，不构成真人口播验收。

分段必须覆盖整片；最多允许0.25秒邻近帧延伸用于真实短停顿，不循环、不变速、不用长冻帧补缺。分段重叠、乱序、音频不匹配、源区间不足都会阻止输出。

### 人脸裁切

auto使用包内MIT许可YuNet模型，以每0.5秒采样进行人脸定位，覆盖不足80%或连续超过2秒失追即停止。每段取稳定中值构图，这是分段定位，不是逐帧跟踪、身份识别或背景抠像。用户也可明确提供`crop:{"cx":0.5,"cy":0.5,"width":0.8,"height":0.9}`，所有值为源画面归一化比例，必须完整位于画面内。多人物自动选角不在本候选范围内。

## 转场与分辨率

非接续graphic页面采用同样12帧时长的先淡出、后淡入，不复用透明转场历史缓存。声明兼容的carryFrom对象交接保留。最终渲染会对所有页面接缝关键帧做顺序/逆序绘制对比，生成transition-regression.json。

设置presentation时默认1920×1080，可选1280×720；矢量和字体以实际输出尺寸重新绘制。没有presentation的旧路线保持1280×720，不将其未验证能力冒称1080p。帧率保持24fps。

## 许可与发布边界

模板原创代码与中性示例标识采用MIT；Noto Sans SC依OFL，YuNet依其MIT许可。保留licenses中的文件、作者和来源说明。新内容、Logo、真人形象、声音、客户素材及官方文件截图的权利由输入方自行确认，不因代码采用MIT就自动获得再分发许可。

本包不含作者API凭据、个人下载Key、本期幼儿园标识、人物视频、声音、SRT和文稿。预览必须准确区分中性示意与实际口播。公开上传前仍需平台静态检查和审核；个人下载包应由平台签发，不作为作者源重新上传。
