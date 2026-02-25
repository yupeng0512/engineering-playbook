---
name: yt-dlp
description: YouTube 和视频下载助手。当用户需要下载视频、提取音频、下载播放列表时触发。支持 YouTube、B站等数千个网站，提供格式选择、质量控制、Cookie 认证等功能。
---

# yt-dlp

> YouTube 和视频下载神器 —— 把命令行复杂度翻译成自然语言

## 能力描述

yt-dlp 是功能丰富的命令行音视频下载工具，支持 [数千个网站](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)。这个 Skill 让你用自然语言描述下载需求，自动生成正确的命令。

**核心能力**：
- 下载视频/音频（支持格式选择、质量控制）
- 提取纯音频（MP3/AAC/FLAC）
- 下载播放列表/频道
- 处理需要登录的视频（Cookie 方式）
- 嵌入元数据、缩略图、字幕

## 环境要求

```bash
# 安装（推荐 pipx，隔离环境）
pipx install yt-dlp

# 或 pip
pip install yt-dlp

# 或 Homebrew (macOS)
brew install yt-dlp

# 验证安装
yt-dlp --version
```

**依赖**：
- Python 3.8+
- ffmpeg（合并视频音频、转码必需）

```bash
# 安装 ffmpeg
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# 验证
ffmpeg -version
```

## 核心命令模板

### 基础下载

```bash
# 默认下载（最佳质量视频+音频合并）
yt-dlp "VIDEO_URL"

# 指定输出文件名
yt-dlp -o "%(title)s.%(ext)s" "VIDEO_URL"

# 指定输出目录
yt-dlp -P ~/Downloads/videos "VIDEO_URL"
```

### 格式选择

```bash
# 查看所有可用格式
yt-dlp -F "VIDEO_URL"

# 下载最佳 MP4 格式
yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" "VIDEO_URL"

# 下载 1080p 或更低的最佳质量
yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" "VIDEO_URL"

# 下载 720p
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" "VIDEO_URL"

# 下载最小文件（质量最低）
yt-dlp -S "+size,+br" "VIDEO_URL"
```

### 提取纯音频

```bash
# 提取最佳音频并转为 MP3
yt-dlp -x --audio-format mp3 "VIDEO_URL"

# 提取音频保持原格式
yt-dlp -x "VIDEO_URL"

# 指定音频质量（0 最好，9 最差）
yt-dlp -x --audio-format mp3 --audio-quality 0 "VIDEO_URL"

# 使用预设别名（简写）
yt-dlp --preset-alias mp3 "VIDEO_URL"
```

### 播放列表/频道

```bash
# 下载整个播放列表
yt-dlp "PLAYLIST_URL"

# 下载播放列表指定范围（第 1-10 个）
yt-dlp --playlist-start 1 --playlist-end 10 "PLAYLIST_URL"

# 下载频道所有视频
yt-dlp "CHANNEL_URL"

# 只下载最新 5 个视频
yt-dlp --playlist-end 5 "CHANNEL_URL"
```

### Cookie 认证（会员/登录视频）

```bash
# 从浏览器导入 Cookie（推荐）
yt-dlp --cookies-from-browser chrome "VIDEO_URL"
yt-dlp --cookies-from-browser firefox "VIDEO_URL"

# 使用 Cookie 文件
yt-dlp --cookies cookies.txt "VIDEO_URL"
```

### 元数据嵌入

```bash
# 嵌入缩略图
yt-dlp --embed-thumbnail "VIDEO_URL"

# 嵌入元数据（标题、描述、上传日期等）
yt-dlp --embed-metadata "VIDEO_URL"

# 嵌入字幕
yt-dlp --embed-subs --sub-langs "en,zh" "VIDEO_URL"

# 全部嵌入
yt-dlp --embed-thumbnail --embed-metadata --embed-subs "VIDEO_URL"
```

### 输出模板

```bash
# 常用输出模板变量
# %(title)s       - 视频标题
# %(id)s          - 视频 ID
# %(ext)s         - 扩展名
# %(uploader)s    - 上传者
# %(upload_date)s - 上传日期 (YYYYMMDD)
# %(playlist)s    - 播放列表名
# %(playlist_index)s - 播放列表序号

# 示例：按日期+标题命名
yt-dlp -o "%(upload_date)s-%(title)s.%(ext)s" "VIDEO_URL"

# 示例：按上传者分目录
yt-dlp -o "%(uploader)s/%(title)s.%(ext)s" "VIDEO_URL"

# 示例：播放列表带序号
yt-dlp -o "%(playlist)s/%(playlist_index)02d-%(title)s.%(ext)s" "PLAYLIST_URL"
```

## 使用示例

### 场景 1：下载 YouTube 视频为 1080p MP4

**用户说**："下载这个 YouTube 视频，1080p，MP4 格式"

```bash
yt-dlp -f "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]" \
  -o "%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 场景 2：从 B 站下载音频转 MP3

**用户说**："把这个 B 站视频的音频提取出来，转成 MP3"

```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 \
  -o "%(title)s.%(ext)s" \
  "https://www.bilibili.com/video/BV..."
```

### 场景 3：下载 YouTube 会员视频

**用户说**："下载这个需要会员的 YouTube 视频，用我 Chrome 的登录状态"

```bash
yt-dlp --cookies-from-browser chrome \
  -f "bv*+ba/b" \
  --embed-thumbnail --embed-metadata \
  "https://www.youtube.com/watch?v=MEMBER_VIDEO_ID"
```

### 场景 4：批量下载播放列表

**用户说**："下载这个播放列表，每个视频按序号命名，放到单独文件夹"

```bash
yt-dlp -o "%(playlist)s/%(playlist_index)02d-%(title)s.%(ext)s" \
  --embed-thumbnail --embed-metadata \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### 场景 5：下载最高质量视频+音频

**用户说**："下载这个视频，要最高画质，音质也要最好的"

```bash
yt-dlp -f "bv*+ba/b" \
  -S "res,br,asr" \
  --embed-thumbnail --embed-metadata \
  -o "%(title)s [%(height)sp].%(ext)s" \
  "VIDEO_URL"
```

## 常见问题

### Q1: 下载速度慢

```bash
# 使用多线程（实验性）
yt-dlp -N 4 "VIDEO_URL"

# 使用代理
yt-dlp --proxy "socks5://127.0.0.1:1080" "VIDEO_URL"
```

### Q2: 视频和音频没有合并

**原因**：缺少 ffmpeg

```bash
# 安装 ffmpeg 后重试
sudo apt install ffmpeg  # Ubuntu
brew install ffmpeg      # macOS
```

### Q3: 报错 "Unable to extract" 或 "Video unavailable"

```bash
# 更新 yt-dlp（网站经常更新反爬）
yt-dlp -U

# 或
pip install -U yt-dlp
```

### Q4: 想看支持哪些网站

```bash
# 查看支持的网站列表
yt-dlp --list-extractors | head -50

# 或查看完整列表
# https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
```

### Q5: Cookie 导入失败

```bash
# 确保浏览器已关闭（Chrome 会锁定 Cookie 数据库）
# 或尝试其他浏览器
yt-dlp --cookies-from-browser firefox "VIDEO_URL"
```

### Q6: 下载私有/年龄限制视频

```bash
# 需要登录的私有视频
yt-dlp --cookies-from-browser chrome "VIDEO_URL"

# 年龄限制视频（需要账号验证）
yt-dlp --cookies-from-browser chrome --age-limit 99 "VIDEO_URL"
```

## 高级技巧

### 配置文件

创建 `~/.config/yt-dlp/config` 保存常用配置：

```
# 默认输出目录
-P ~/Downloads/yt-dlp

# 默认输出模板
-o %(uploader)s/%(title)s.%(ext)s

# 总是嵌入元数据
--embed-metadata
--embed-thumbnail

# 默认格式选择
-f bv*[height<=1080]+ba/b[height<=1080]
```

### 存档功能（避免重复下载）

```bash
# 使用存档文件记录已下载视频
yt-dlp --download-archive archive.txt "PLAYLIST_URL"

# 后续运行会跳过已下载的
yt-dlp --download-archive archive.txt "PLAYLIST_URL"
```

## 参考资源

- [官方 GitHub](https://github.com/yt-dlp/yt-dlp)
- [支持的网站列表](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)
- [完整选项文档](https://github.com/yt-dlp/yt-dlp#usage-and-options)
