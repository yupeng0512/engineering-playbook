#!/bin/bash
# Engineering Playbook — 一键安装 / 卸载脚本
# 通过 symlink 将仓库内的 Skills 链接到 Cursor 识别的目录
#
# 用法:
#   ./setup.sh               安装（建立 symlink）
#   ./setup.sh --uninstall   卸载（移除由本仓库创建的 symlink）
#   ./setup.sh --status      查看当前链接状态
#   ./setup.sh --help        显示帮助

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURSOR_SKILLS_DIR="$HOME/.cursor/skills"
CURSOR_SYSTEM_DIR="$HOME/.cursor/skills-cursor"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok()   { echo -e "  ${GREEN}[✓]${NC} $1"; }
log_skip() { echo -e "  ${YELLOW}[–]${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
log_rm()   { echo -e "  ${RED}[✗]${NC} $1"; }

link_skill() {
    local src="$1" target="$2" name="$3"

    if [ -L "$target" ]; then
        local current
        current=$(readlink -f "$target" 2>/dev/null || readlink "$target")
        local expected
        expected=$(cd "$src" && pwd)
        if [ "$current" = "$expected" ]; then
            log_skip "$name (已链接，指向正确)"
        else
            rm "$target"
            ln -s "$src" "$target"
            log_ok "$name (已更新 symlink)"
        fi
    elif [ -d "$target" ]; then
        mv "$target" "${target}.local-backup"
        log_warn "$name → 已备份到 ${name}.local-backup"
        ln -s "$src" "$target"
        log_ok "$name"
    else
        ln -s "$src" "$target"
        log_ok "$name"
    fi
}

unlink_skill() {
    local target="$1" name="$2"

    if [ -L "$target" ]; then
        local link_target
        link_target=$(readlink -f "$target" 2>/dev/null || readlink "$target")
        if [[ "$link_target" == "$SCRIPT_DIR"* ]]; then
            rm "$target"
            log_rm "$name (symlink 已移除)"
            if [ -d "${target}.local-backup" ]; then
                mv "${target}.local-backup" "$target"
                log_ok "$name → 已还原 local-backup"
            fi
        else
            log_skip "$name (非本仓库 symlink，跳过)"
        fi
    else
        log_skip "$name (不是 symlink，跳过)"
    fi
}

show_status() {
    echo "=== Skills 链接状态 ==="
    echo ""
    echo "--- 个人 Skills (→ $CURSOR_SKILLS_DIR) ---"
    for skill_dir in "$SCRIPT_DIR/skills/personal"/*/; do
        [ -d "$skill_dir" ] || continue
        local name
        name=$(basename "$skill_dir")
        local target="$CURSOR_SKILLS_DIR/$name"
        if [ -L "$target" ]; then
            local dest
            dest=$(readlink "$target")
            echo -e "  ${GREEN}●${NC} $name → $dest"
        else
            echo -e "  ${RED}○${NC} $name (未链接)"
        fi
    done

    echo ""
    echo "--- 系统 Skills (→ $CURSOR_SYSTEM_DIR) ---"
    for skill_dir in "$SCRIPT_DIR/skills/cursor-system"/*/; do
        [ -d "$skill_dir" ] || continue
        local name
        name=$(basename "$skill_dir")
        local target="$CURSOR_SYSTEM_DIR/$name"
        if [ -L "$target" ]; then
            local dest
            dest=$(readlink "$target")
            echo -e "  ${GREEN}●${NC} $name → $dest"
        else
            echo -e "  ${RED}○${NC} $name (未链接)"
        fi
    done

    echo ""
    echo "--- project-retrospective (特殊处理) ---"
    local retro_dir="$CURSOR_SKILLS_DIR/project-retrospective"
    if [ -d "$retro_dir" ]; then
        for item in SKILL.md knowledge-base templates; do
            local target_path="$retro_dir/$item"
            if [ -L "$target_path" ]; then
                echo -e "  ${GREEN}●${NC} $item → $(readlink "$target_path")"
            else
                echo -e "  ${RED}○${NC} $item (未链接)"
            fi
        done
    else
        echo -e "  ${RED}○${NC} 目录不存在"
    fi
}

do_install() {
    echo "=== Engineering Playbook 安装 ==="
    echo "仓库路径: $SCRIPT_DIR"
    echo ""

    echo "--- 链接个人 Skills ---"
    mkdir -p "$CURSOR_SKILLS_DIR"
    for skill_dir in "$SCRIPT_DIR/skills/personal"/*/; do
        [ -d "$skill_dir" ] || continue
        local name
        name=$(basename "$skill_dir")
        link_skill "$skill_dir" "$CURSOR_SKILLS_DIR/$name" "$name"
    done

    local retro_src="$SCRIPT_DIR/skills/personal/project-retrospective.md"
    local retro_dir="$CURSOR_SKILLS_DIR/project-retrospective"
    if [ -f "$retro_src" ]; then
        mkdir -p "$retro_dir"
        ln -sf "$retro_src" "$retro_dir/SKILL.md"
        ln -sf "$SCRIPT_DIR/knowledge-base" "$retro_dir/knowledge-base"
        ln -sf "$SCRIPT_DIR/templates" "$retro_dir/templates"
        log_ok "project-retrospective (SKILL.md + knowledge-base + templates)"
    fi

    echo ""
    echo "--- 链接系统 Skills ---"
    mkdir -p "$CURSOR_SYSTEM_DIR"
    for skill_dir in "$SCRIPT_DIR/skills/cursor-system"/*/; do
        [ -d "$skill_dir" ] || continue
        local name
        name=$(basename "$skill_dir")
        link_skill "$skill_dir" "$CURSOR_SYSTEM_DIR/$name" "$name"
    done

    echo ""
    echo -e "${GREEN}=== 安装完成 ===${NC}"
    echo ""
    echo "使用方式:"
    echo "  沉淀经验  → 在 Cursor 中说\"沉淀项目经验\""
    echo "  查阅经验  → 在 Cursor 中说\"查看相关经验\""
    echo "  引用文件  → @patterns/dynamic-config.md"
    echo "  更新仓库  → cd $SCRIPT_DIR && git pull"
}

do_uninstall() {
    echo "=== Engineering Playbook 卸载 ==="
    echo ""

    echo "--- 移除个人 Skills ---"
    for skill_dir in "$SCRIPT_DIR/skills/personal"/*/; do
        [ -d "$skill_dir" ] || continue
        local name
        name=$(basename "$skill_dir")
        unlink_skill "$CURSOR_SKILLS_DIR/$name" "$name"
    done

    local retro_dir="$CURSOR_SKILLS_DIR/project-retrospective"
    if [ -d "$retro_dir" ]; then
        for item in SKILL.md knowledge-base templates; do
            [ -L "$retro_dir/$item" ] && rm "$retro_dir/$item"
        done
        rmdir "$retro_dir" 2>/dev/null && log_rm "project-retrospective (目录已清理)" || true
    fi

    echo ""
    echo "--- 移除系统 Skills ---"
    for skill_dir in "$SCRIPT_DIR/skills/cursor-system"/*/; do
        [ -d "$skill_dir" ] || continue
        local name
        name=$(basename "$skill_dir")
        unlink_skill "$CURSOR_SYSTEM_DIR/$name" "$name"
    done

    echo ""
    echo -e "${GREEN}=== 卸载完成 ===${NC}"
}

show_help() {
    echo "Engineering Playbook 安装脚本"
    echo ""
    echo "用法: ./setup.sh [选项]"
    echo ""
    echo "选项:"
    echo "  (无参数)       安装 — 建立 symlink 到 ~/.cursor/"
    echo "  --uninstall    卸载 — 移除由本仓库创建的 symlink"
    echo "  --status       查看当前链接状态"
    echo "  --help         显示此帮助信息"
}

case "${1:-}" in
    --uninstall) do_uninstall ;;
    --status)    show_status ;;
    --help|-h)   show_help ;;
    "")          do_install ;;
    *)           echo "未知参数: $1"; show_help; exit 1 ;;
esac
