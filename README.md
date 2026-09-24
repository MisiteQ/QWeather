# 天气预报 QWeather Widget
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-2.2.6-blue">
  <img alt="fnOS" src="https://img.shields.io/badge/fnOS-x86%20%7C%20arm-success">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-orange">
  <img alt="Data" src="https://img.shields.io/badge/data-Open--Meteo-green">
</p>

飞牛 fnOS 桌面天气预报小部件（FPK 原生应用）：直接注入飞牛桌面显示，**无窗口标题栏**，支持实时天气与未来 5 天预报、全球城市搜索切换、桌面自由拖动、卡片透明度调节、调整大小、隐藏 / 恢复。数据来源 [Open-Meteo](https://open-meteo.com/)（免费，**无需 API Key**），小部件前端直连 Open-Meteo，无需经 NAS 网关中转。

- 当前版本：**v2.2.6**
- 作者：**Misite齊**
- 适用平台：fnOS **x86 + arm**（最低系统版本 1.0.0）
- 服务端口：**5698**
- 运行身份：**root**（需操作 nginx 配置与系统恢复包）

## ✨ 功能

- **🌤️ 实时天气**：当前温度、体感温度、湿度、风速风向、气压、天气状况（WMO 代码图标化）
- **📅 5 天预报**：每日天气图标、最高 / 最低温、降水概率
- **🔍 城市切换**：全球城市搜索，支持中英文，结果含经纬度与国家
- **🖱️ 自由拖动**：按住卡片头部拖动，位置自动记忆（localStorage）
- **🎚️ 透明度调节**：设置面板中滑动调节卡片背景透明度
- **↔️ 调整大小**：拖动右下角手柄调整卡片尺寸
- **👁️ 隐藏 / 恢复**：可一键隐藏小组件，桌面右下角出现恢复按钮
- **🔄 自动刷新**：可配置刷新间隔（默认 30 分钟）
- **🖥️ 桌面注入**：无独立窗口，直接显示在飞牛桌面上，登录界面自动隐藏

## 🏗️ 技术实现

### 注入机制（零 `/usr/trim/www` 写入）

fnOS 的 nginx 内置 `trim_recover` 模块：直接修改 `/usr/trim/www` 会被系统自愈覆盖，持续写入还会触发「恢复风暴」；同时 nginx 每次 reload/restart 都会从加密的 `ng.conf.zip` 恢复 `conf.d/`，自定义配置会被抹掉。

对策：

1. 小组件注入页放在应用数据目录（`/vol1/@appdata/com.qweather.widget/desktop/index.html`），内容为系统 `index.html` + 一行 `<script src="/qweather-widget.js">`
2. `conf.d/qweather.conf` 用 `alias` 把 `GET /` 与 `GET /login` 指向该注入页
3. `ng.conf.zip` 的 ZipCrypto 密钥已通过 bkcrack 已知明文攻击恢复，应用把 `qweather.conf` 以相同密钥加密后写进 `ng.conf.zip`，nginx 每次恢复都会「恢复出」我们的配置，注入天然持久
4. 维护线程低频（30s）巡检，全部只在缺失时补写
5. **永远不写 `/usr/trim/www` 下任何文件**

### 层级策略

小组件挂载到飞牛桌面容器（`.desktop` 内的 `.relative.h-full`）内部，使用 `position:absolute + z-index:10`：

```
壁纸(0) ＜ 桌面图标(auto 非定位) ＜ 小组件(10) ＜ 原生窗口(10010+) ＜ 右键菜单(10022) ＜ 全屏界面(1000001)
```

因此所有原生界面天然覆盖小组件，小组件永远不会挡住任何原生控件；卡片之外的区域 `pointer-events:none`，完全点击穿透，不影响桌面操作。

## 📦 安装

### 方式一：FnDepot 应用源（推荐）

在飞牛 fnOS 上安装 [FnDepot](https://github.com/EWEDLCM/FnDepot) 客户端后，添加作者的应用源即可搜索「天气预报」一键安装 / 升级：

```
https://github.com/MisiteQ/FnDepot
```

### 方式二：手动安装 FPK

1. 到 [Releases](https://github.com/MisiteQ/QWeather/releases) 下载 `com.qweather.widget-2.2.6-x86.fpk`
2. 飞牛 OS → **应用中心** → 左下角 **手动安装** → 选择 fpk 文件
3. 安装完成后，天气卡片即显示在飞牛桌面上（若未显示，强制刷新桌面 `Ctrl+Shift+R`）

> 若「手动安装」入口被关闭，SSH 执行：`appcenter-cli manual-install enable`

## 🛠 从源码打包

需要 Python 3。打包产物架构由 `fpk/manifest` 中的 `platform` 字段决定（`x86` 或 `arm`）。

### 打包指定架构

```bash
# 修改 fpk/manifest 的 platform 字段为目标架构，然后：
python3 build_fp.py
```

### Windows（PowerShell）

```powershell
.\build.ps1
```

### Linux / fnOS

```bash
bash build.sh
```

> 双架构发布：分别将 `platform` 设为 `x86` 和 `arm` 各打包一次，产物为 `com.qweather.widget-2.2.5-x86.fpk` 和 `com.qweather.widget-2.2.5-arm.fpk`。

或直接运行：

```bash
python3 build_fp.py
```

产物：`com.qweather.widget-<version>-x86.fpk`

## 📁 项目结构

```
build_fp.py              FPK 打包脚本（纯 Python，无需 fnpack）
build.ps1 / build.sh     Windows / Linux 打包入口
manifest                 飞牛应用清单（版本、显示名、端口、权限、更新日志）
fpk/
├── app/
│   ├── app.py           Flask 后端：注入维护 + 天气 / 地理编码 API
│   ├── requirements.txt Python 依赖（Flask、requests、gunicorn）
│   ├── conf/
│   │   └── ng_keys.json ng.conf.zip ZipCrypto 密钥（bkcrack 恢复）
│   ├── static/
│   │   └── widget.js    桌面小组件前端（注入飞牛桌面运行）
│   └── ui/
│       ├── config       飞牛桌面入口配置（iframe -> http://127.0.0.1:5698）
│       └── images/      应用图标
├── cmd/                 飞牛生命周期脚本（安装 / 卸载 / 升级 / 启停 / 配置）
├── config/              飞牛权限与资源声明（以 root 运行）
└── wizard/              安装向导
```

## 🔒 隐私与安全

- 天气数据由浏览器前端直连 [Open-Meteo](https://open-meteo.com/) 公开 API 获取，**不经过 NAS 中转、不上传任何个人信息**
- 城市搜索同样直连 Open-Meteo Geocoding API
- 应用后端仅用于桌面注入维护与备用天气查询，不存储任何用户数据
- `ng_keys.json` 中的密钥为 fnOS 系统 `ng.conf.zip` 的 ZipCrypto 内部密钥（通过已知明文攻击恢复），仅用于在系统恢复包中持久化本应用的 nginx 配置

## 🙏 致谢

- 飞牛 fnOS 与 [FnDepot](https://github.com/EWEDLCM/FnDepot)
- [Open-Meteo](https://open-meteo.com/) 免费天气 API

## 📋 版本历史

| 版本 | 内容 |
|---|---|
| v2.2.6 | **字号优化**：日期时间字号 11px → 14px、底部更新时间 10px → 11px，提升可读性 |
| v2.2.5 | **卡片布局优化**：将「未来预报」区块移至「详情」区块之前，使预报信息更醒目 |
| v2.2.4 | 维护性更新 |
| v2.1.0 | **彻底修复遮挡问题**：小组件挂载到飞牛桌面容器内部（z-index:10），原生窗口 / 右键菜单 / 模态框天然覆盖小组件，永远不挡原生控件；默认位置自动避让桌面图标；卡片右键仍可调出飞牛桌面菜单且定位一致；注入机制重构——nginx 配置经加密 ng.conf.zip 同步以兼容系统自愈，widget.js 由 nginx 直接 alias 提供，维护线程仅「期望内容」核对、不写系统 www 目录，消除 v2.0.0 持续写入触发的系统恢复风暴 |
| v2.0.0 | z-index 降到 9999；pointer-events 隔离；模态设置面板；拖动调整大小；登录检测；www.zip 注入 |

完整日志见 [Releases](https://github.com/MisiteQ/QWeather/releases)。

## 📄 许可证

[MIT License](LICENSE) © 2026 Misite齊
