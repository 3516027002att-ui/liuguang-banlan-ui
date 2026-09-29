# liuguang-banlan-ui

## 验证

- 脚本测试：`python -m unittest discover -s tests`。
- manifest：`python scripts/validate_manifest.py assets/starter/opal/theme-config.js`，obsidian 同理；结果应为 valid，且没有 warnings。
- 渲染器语法：`node --check assets/starter/shared/spectral-field.js`。
- 页面：`python scripts/serve_preview.py . --port 8780`，用真实浏览器打开两个 starter，在 1440×900 和 390×844 下各看一遍，console 不能有 error 或 warning。
- 像素：对纯色场截图运行 `scripts/measure_preview.py`，判读方法见 `references/verification.md`。

## 约定

- 改了 `assets/starter/shared/spectral-field.js`，要告诉用户：用这个 skill 做的站点里如果有这个文件的副本，需要各自决定是否同步。
