#!/bin/bash
# Engineering Playbook — 一键安装脚本
# 创建 symlink 将仓库内容链接到 Cursor Skills 目录

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURSOR_SKILLS_DIR="$HOME/.cursor/skills"
CURSOR_SYSTEM_DIR="$HOME/.cursor/skills-cursor"

echo "=== Engineering Playbook Setup ==="
echo "仓库路径: $SCRIPT_DIR"
echo ""

# 1. 链接个人 Skills
echo "--- 链接个人 Skills ---"
mkdir -p "$CURSOR_SKILLS_DIR"

for skill_dir in "$SCRIPT_DIR/skills/personal"/*/; do
    skill_name=$(basename "$skill_dir")
    target="$CURSOR_SKILLS_DIR/$skill_name"

    if [ -L "$target" ]; then
        echo "  [跳过] $skill_name (symlink 已存在)"
    elif [ -d "$target" ]; then
        echo "  [备份] $skill_name → ${target}.local-backup"
        mv "$target" "${target}.local-backup"
        ln -s "$skill_dir" "$target"
        echo "  [链接] $skill_name"
    else
        ln -s "$skill_dir" "$target"
        echo "  [链接] $skill_name"
    fi
done

# project-retrospective 是单文件 Skill，需要特殊处理
RETRO_SRC="$SCRIPT_DIR/skills/personal/project-retrospective.md"
RETRO_DIR="$CURSOR_SKILLS_DIR/project-retrospective"
if [ -f "$RETRO_SRC" ] && [ ! -L "$RETRO_DIR" ]; then
    mkdir -p "$RETRO_DIR"
    ln -sf "$RETRO_SRC" "$RETRO_DIR/SKILL.md"
    # 链接 knowledge-base 和 templates
    ln -sf "$SCRIPT_DIR/knowledge-base" "$RETRO_DIR/knowledge-base"
    ln -sf "$SCRIPT_DIR/templates" "$RETRO_DIR/templates"
    echo "  [链接] project-retrospective (+ knowledge-base, templates)"
fi

# 2. 链接 Cursor 系统级 Skills
echo ""
echo "--- 链接 Cursor 系统级 Skills ---"
mkdir -p "$CURSOR_SYSTEM_DIR"

for skill_dir in "$SCRIPT_DIR/skills/cursor-system"/*/; do
    skill_name=$(basename "$skill_dir")
    target="$CURSOR_SYSTEM_DIR/$skill_name"

    if [ -L "$target" ]; then
        echo "  [跳过] $skill_name (symlink 已存在)"
    elif [ -d "$target" ]; then
        echo "  [备份] $skill_name → ${target}.local-backup"
        mv "$target" "${target}.local-backup"
        ln -s "$skill_dir" "$target"
        echo "  [链接] $skill_name"
    else
        ln -s "$skill_dir" "$target"
        echo "  [链接] $skill_name"
    fi
done

echo ""
echo "=== 安装完成 ==="
echo ""
echo "使用方式:"
echo "  - 在 Cursor 中说\"沉淀项目经验\"触发经验生成"
echo "  - 在 Cursor 中说\"查看相关经验\"查询历史经验"
echo "  - 直接 @ 引用 patterns/ 或 knowledge-base/ 中的文件"
echo ""
echo "更新仓库: cd $SCRIPT_DIR && git pull"
