# 用用户内容开始制作

先承接已有主题/稿子/素材。缺主题时只问一个自然问题；不要用四个必答问题收集可选素材。用户没指定声音时，方案按文字动效与原生动作音效推进。若明确要求人声或音乐且未给文件，只问真正缺少的那一份，继续准备可做的画面。

按语义选组，不让用户挑ID：B1讲一个关键词，B2讲1–5点，B3比较两个角度并下结论，B4总结并给行动。不要把未完成的事情画成完成章；保留否定、条件、数字和结论。没有时长要求时按内容提出8–20秒初稿，长句先分行或拆镜头，改写意思要给用户核对。

| Group | Required `basic` fields | Duration |
| --- | --- | --- |
| B1 | keyword, explanation | 8s |
| B2 | heading, points (1–5) | 10s |
| B3 | heading, left, right, conclusion | 10s |
| B4 | summary, action | 8s |

Each supports0–12 additional seconds in its declared quiet reading interval. B1+B2=18s; B3 at12s+B4 at8s=20s. Preserve original motion speed. For native media scenes inspect the selected unit in core/catalog.json and only its fields in core/content.schema.json; do not dump the entire library. No original media fallback exists.

The assistant writes **new user.json** from the current brief according to params.schema.json. Use `mode:user-media`, the edition language and landscape. Bind supplied files by actual path and dimensions. Unrequested missing presenter/voice/music use explicit `mode:none`; default `soundEffects:native`, captions from actual supplied/measured cues or an empty array. Do not invent word timing, provenance or a fulfilled requested soundtrack. Music provenance fields record what is actually known, without an extra license questionnaire for material that was never requested.

Review the brief and run inside the extracted runner, saving outputs outside it:

```sh
npm ci
uv run adapter.py plan --input ../my-video/user.json --out ../my-video/plan.json
uv run adapter.py prepare --input ../my-video/user.json --out ../my-video/instance
uv run adapter.py preview --instance ../my-video/instance --out ../my-video/preview.png --time 2
```

Show the actual preview and continue under the user's existing stage authorization:

```sh
uv run adapter.py render --instance ../my-video/instance --out ../my-video/silent.mp4
```

The render entry invokes the mixer; final video is **../my-video/silent-with-audio.mp4**. Inspect final encoded content, cropping, subtitles and sound. Preserve existing instances/outputs. A plan, still or successful command alone is not a completed film. Use only these declared local production entries; do not add remote service/credential checks or explain unused-service boundaries to the user. Introduce the optional follow-up only after the completed video is delivered, as specified in delivery.json.
