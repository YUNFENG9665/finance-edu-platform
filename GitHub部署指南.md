# GitHub 部署指南

## 📋 准备工作

✅ 代码已经初始化为Git仓库
✅ 所有文件已提交到本地仓库
✅ 分支名称：main

---

## 🚀 步骤1: 在GitHub上创建仓库

### 方法1: 使用GitHub网页

1. 访问 https://github.com
2. 登录您的GitHub账户
3. 点击右上角的 **"+"** → **"New repository"**
4. 填写信息：
   - **Repository name**: `finance-edu-platform` （或您喜欢的名称）
   - **Description**: "金融教学平台 - 基于盈米MCP的交互式金融投资教学应用"
   - **Public** 或 **Private**: 选择 **Public**（Streamlit Cloud免费版需要公开仓库）
   - ❌ **不要勾选** "Add a README file"
   - ❌ **不要勾选** "Add .gitignore"
   - ❌ **不要勾选** "Choose a license"
5. 点击 **"Create repository"**

### 方法2: 使用GitHub CLI

```bash
# 如果已安装gh命令行工具
gh repo create finance-edu-platform --public --source=. --push
```

---

## 📤 步骤2: 推送代码到GitHub

### 使用HTTPS（推荐）

在GitHub创建仓库后，运行以下命令：

```bash
# 进入项目目录
cd /Users/ethen/Documents/MAC/金融教学应用/web_app

# 添加远程仓库（将YOUR_USERNAME替换为您的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/finance-edu-platform.git

# 推送代码
git push -u origin main
```

**示例**：
```bash
# 如果您的GitHub用户名是 ethen123
git remote add origin https://github.com/ethen123/finance-edu-platform.git
git push -u origin main
```

### 使用SSH

```bash
# 添加远程仓库
git remote add origin git@github.com:YOUR_USERNAME/finance-edu-platform.git

# 推送代码
git push -u origin main
```

---

## ☁️ 步骤3: 部署到Streamlit Cloud

### 3.1 访问Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 使用GitHub账号登录
3. 授权Streamlit访问您的GitHub仓库

### 3.2 创建新应用

1. 点击 **"New app"** 按钮
2. 填写部署信息：
   - **Repository**: 选择 `YOUR_USERNAME/finance-edu-platform`
   - **Branch**: 选择 `main`
   - **Main file path**: 输入 `app.py`
3. 点击 **"Deploy!"**

### 3.3 配置密钥（重要！）

应用部署后，需要配置API密钥：

1. 在Streamlit Cloud控制台，点击应用右上角的 **"⋮"** 菜单
2. 选择 **"Settings"**
3. 切换到 **"Secrets"** 标签
4. 粘贴以下内容：

```toml
MCP_API_KEY = "EXWHE1CGIZRPRXY8NPoC0w"
JWT_SECRET = "finance-edu-secret-key-2026-secure-random-string"
DB_TYPE = "sqlite"
DEBUG = false
LOG_LEVEL = "INFO"
```

5. 点击 **"Save"**
6. 应用会自动重启

---

## ✅ 验证部署

部署完成后：

1. 访问Streamlit Cloud提供的应用URL（格式：`https://YOUR_APP_NAME.streamlit.app`）
2. 使用演示账户登录：
   - 用户名: `demo_student`
   - 密码: `demo123`
3. 测试各项功能

---

## 🔄 后续更新代码

每次修改代码后：

```bash
# 1. 添加修改的文件
git add .

# 2. 提交修改
git commit -m "描述您的修改"

# 3. 推送到GitHub
git push

# Streamlit Cloud会自动检测到更改并重新部署
```

---

## 🐛 常见问题

### Q1: 推送失败：权限被拒绝

**A**: 需要配置GitHub身份验证

**使用Personal Access Token (推荐)**:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 "repo" 权限
4. 生成token并保存
5. 推送时使用token作为密码

### Q2: Streamlit Cloud部署失败

**A**: 检查以下几点：
- ✅ 仓库是Public
- ✅ requirements.txt 文件存在
- ✅ app.py 路径正确
- ✅ Secrets配置正确

### Q3: 应用无法访问数据库

**A**: Streamlit Cloud的文件系统是临时的
- 建议使用外部数据库（如Supabase、PlanetScale）
- 或接受每次重启后数据会丢失

### Q4: 如何查看日志

**A**:
1. 在Streamlit Cloud控制台
2. 点击应用卡片
3. 查看 "Logs" 标签

---

## 📞 需要帮助？

如果遇到问题，可以：

1. 查看 Streamlit 文档: https://docs.streamlit.io/streamlit-cloud
2. 查看 部署指南.md
3. 检查应用日志

---

## 🎉 部署成功！

完成部署后，您的应用将：

- ✅ 自动HTTPS加密
- ✅ 全球CDN加速
- ✅ 自动重启和监控
- ✅ 免费托管（公开应用）

**应用地址将类似于**: `https://finance-edu-platform.streamlit.app`

分享给学生和老师使用吧！🎓📊
