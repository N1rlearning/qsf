# PDF去水印 (PDF Watermark Remover)

免费在线PDF水印移除工具 - 支持中英文双语水印识别

## ✨ 功能特性

- 🧹 **去除水印** - 支持移除扫描全能王(CamScanner)中英文水印
- 📱 **移除二维码** - 自动清除右下角二维码水印
- 📑 **PDF合并** - 将多个PDF文件按顺序合并
- 🔒 **隐私安全** - 快速处理，本地存储
- 🌐 **中英双语** - 支持中文/英文界面切换

## 🌐 水印识别

支持识别以下水印：

### 中文水印
- 扫描全能王
- 全能扫描王
- CamScanner 中文版

### 英文水印
- "Scanned with CamScanner"
- "Created by CamScanner"
- "CamScanner"

## 🚀 快速开始

### 1. 安装依赖

```bash
cd pdf-tools
pip install -r requirements.txt
```

### 2. 本地运行

```bash
python app.py
```

访问 http://localhost:8000

### 3. 切换语言

- 中文: http://localhost:8000/cn
- English: http://localhost:8000/en

## ☁️ 部署到云端

### Render.com（推荐）- 免费层可用

**步骤 1：准备代码**

```bash
# 1. 进入项目目录
cd /Users/nirvirain/Desktop/wen/pdf-tools

# 2. 初始化 Git 仓库（如未初始化）
git init
git add .
git commit -m "Initial commit"

# 3. 创建 GitHub 仓库并推送
# 在 GitHub 网站创建仓库，然后：
git remote add origin https://github.com/你的用户名/pdf-watermark-remover.git
git branch -M main
git push -u origin main
```

**步骤 2：在 Render 上创建服务**

1. 访问 https://render.com 并注册/登录
2. 点击 **New +** → **Web Service**
3. 连接你的 GitHub 仓库
4. 配置构建设置：

| 配置项 | 值 |
|--------|-----|
| Name | `pdf-watermark-remover` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| Plan | Free（免费） |

5. 点击 **Create Web Service**

**步骤 3：等待部署完成**

- 首次部署需要 2-5 分钟
- 部署成功后，你会获得一个 URL，如：`https://pdf-watermark-remover.onrender.com`

**注意：Render 免费版的限制**
- 每月 750 小时运行时间
- 空闲 15 分钟后自动休眠
- 首次访问需要唤醒（可能需要 30-60 秒）

### Railway 部署（备选方案）

```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录并初始化
railway login
railway init

# 部署
railway up

# 查看 URL
railway open
```

### Vercel 部署（需要额外配置）

由于本项目需要后端处理 PDF，Vercel 需要配合 Serverless Functions 使用，建议使用 Render 或 Railway。

## 💰 Google AdSense 接入

在 `templates/index.html` 中添加广告代码：

```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-你的发布商ID" crossorigin="anonymous"></script>

<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-你的发布商ID"
     data-ad-slot="广告位ID"
     data-ad-format="auto">
</ins>
```

### 广告位建议

1. **页面顶部** - 高展示率
2. **上传区域下方** - 用户等待时展示
3. **结果区域下方** - 下载前展示

## 📂 项目结构

```
pdf-tools/
├── app.py              # FastAPI 主应用
├── pdf_processor.py    # PDF 处理核心逻辑
├── requirements.txt    # Python 依赖
├── templates/
│   └── index.html      # 前端页面 (TailwindCSS)
├── uploads/            # 上传临时文件
└── outputs/            # 输出文件
```

## 🛠️ 技术栈

- **后端**: FastAPI + Python
- **PDF处理**: PyMuPDF (fitz) + pypdf
- **前端**: TailwindCSS (CDN)
- **部署**: Render / Railway / Vercel

## 📝 许可证

MIT License
