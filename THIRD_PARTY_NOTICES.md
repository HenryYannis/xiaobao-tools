# 第三方声明 (Third-Party Notices)

本仓库自己的代码按根目录 [LICENSE](./LICENSE)（MIT）发布。下面这些内容来自第三方，**不属于**本仓库的 MIT 授权范围，各自遵循原作者的许可证。

---

## 1. QRCode.js（内嵌在 Bitwarden 密码库清理工具里）

- **使用位置**：`productivity/Bitwarden-Vault-Cleaner/index.html` 中内嵌的压缩版二维码库（`var QRCode;...`）
- **原项目**：QRCode.js — https://github.com/davidshimjs/qrcodejs
- **说明**：内嵌的代码与该项目 `qrcode.min.js` 逐字节一致，未做修改。
- **许可证**：MIT License

```
The MIT License (MIT)
---------------------
Copyright (c) 2012 davidshimjs

Permission is hereby granted, free of charge,
to any person obtaining a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

QRCode.js 基于 Kazuhiko Arase 的 “QRCode for JavaScript”：

```
QRCode for JavaScript
Copyright (c) 2009 Kazuhiko Arase
URL: http://www.d-project.com/
Licensed under the MIT license:
  http://www.opensource.org/licenses/mit-license.php
The word "QR Code" is registered trademark of DENSO WAVE INCORPORATED
  http://www.denso-wave.com/qrcode/faqpatent-e.html
```

---

## 2. Scratch 3.0 素材库（`scratch-assets/`）

- **内容**：`scratch-assets/` 目录下的角色造型、背景图片（SVG / PNG）和声音（WAV），来自 Scratch 3.0 官方素材库。
- **版权方**：Scratch Foundation（Scratch 由 MIT 媒体实验室终身幼儿园小组开发，现由 Scratch Foundation 维护）— https://scratch.mit.edu/ 、https://www.scratchfoundation.org/
- **许可证**：按 Scratch 帮助中心的说明，Scratch 网站上的大部分支持素材（角色、图片、声音等）以 Creative Commons 署名-相同方式共享（CC BY-SA）许可提供，Scratch 使用条款中对应的是 CC BY-SA 2.0：
  - 说明页：https://mitscratch.freshdesk.com/en/support/solutions/articles/4000156892
  - 许可证全文：https://creativecommons.org/licenses/by-sa/2.0/
- **例外**：Scratch Logo、Scratch Cat（小猫）、Gobo、Pico、Nano、Giga、Tera 是 Scratch 的商标，**不在**上述许可范围内，未经 Scratch 团队明确许可不能使用。素材库中也可能有第三方拥有商标权的图片或声音。
- **说明**：这些素材原样保存，我没有修改，也不在本仓库的 MIT 授权范围内。如需二次使用，请遵守 CC BY-SA 的署名和相同方式共享要求，并避开上面的商标素材。

---

如果你发现这里遗漏了某个第三方组件，欢迎提 Issue 告诉我。
