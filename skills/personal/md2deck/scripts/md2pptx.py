#!/usr/bin/env python3
"""
md2pptx — 投研报告 Markdown → 可编辑 PowerPoint 转换器

用法:
    python md2pptx.py --input report.md --output output.pptx [--template template.pptx]

依赖:
    pip install python-pptx Pillow
"""

import argparse
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ============================================
# Design Tokens (与 Marp CSS 主题保持一致)
# ============================================

COLORS = {
    'primary': RGBColor(0x1A, 0x73, 0xE8),
    'primary_dark': RGBColor(0x0D, 0x47, 0xA1),
    'accent': RGBColor(0xFF, 0x6D, 0x00),
    'bg': RGBColor(0xFF, 0xFF, 0xFF),
    'bg_alt': RGBColor(0xF5, 0xF7, 0xFA),
    'text': RGBColor(0x21, 0x21, 0x21),
    'text_secondary': RGBColor(0x75, 0x75, 0x75),
    'success': RGBColor(0x2E, 0x7D, 0x32),
    'danger': RGBColor(0xC6, 0x28, 0x28),
    'white': RGBColor(0xFF, 0xFF, 0xFF),
    'table_header': RGBColor(0x1A, 0x73, 0xE8),
    'table_border': RGBColor(0xE0, 0xE0, 0xE0),
}

FONTS = {
    'title': 'Inter',
    'title_cn': 'Noto Sans SC',
    'body': 'Inter',
    'body_cn': 'Noto Sans SC',
    'mono': 'JetBrains Mono',
}

SLIDE_WIDTH = Inches(13.333)   # 16:9
SLIDE_HEIGHT = Inches(7.5)


# ============================================
# Markdown Parser
# ============================================

def parse_markdown_sections(md_text):
    """解析 Markdown 为模块列表，每个模块包含标题和内容块"""
    sections = []
    current = None
    
    for line in md_text.split('\n'):
        # 二级标题 = 新模块
        m = re.match(r'^##\s+(.+)', line)
        if m:
            if current:
                sections.append(current)
            current = {
                'title': m.group(1).strip(),
                'content': [],
                'tables': [],
                'bullets': [],
                'quotes': [],
            }
            continue
        
        if current is None:
            # 文件头部（封面信息）
            m_h1 = re.match(r'^#\s+(.+)', line)
            if m_h1:
                current = {
                    'title': m_h1.group(1).strip(),
                    'content': [],
                    'tables': [],
                    'bullets': [],
                    'quotes': [],
                    'is_cover': True,
                }
            continue
        
        # 表格行
        if '|' in line and not line.strip().startswith('```'):
            current['content'].append(line)
            # 提取表格数据
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells and not all(re.match(r'^[-:]+$', c) for c in cells):
                current['tables'].append(cells)
        # Bullet
        elif re.match(r'^\s*[-*]\s+', line):
            text = re.sub(r'^\s*[-*]\s+', '', line)
            current['bullets'].append(text)
        # Blockquote
        elif line.startswith('>'):
            text = line.lstrip('> ').strip()
            if text:
                current['quotes'].append(text)
        else:
            current['content'].append(line)
    
    if current:
        sections.append(current)
    
    return sections


def extract_table(rows):
    """从表格行列表中提取 header 和 data"""
    if len(rows) < 2:
        return None, []
    header = rows[0]
    data = rows[1:]  # 跳过分隔行（已在 parse 中过滤）
    return header, data


# ============================================
# Slide Builders
# ============================================

def _set_font(run, size=18, bold=False, color=None, font_name=None):
    """设置文字格式"""
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    if font_name:
        run.font.name = font_name


def _add_background(slide, color):
    """设置幻灯片背景色"""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_rect(slide, left, top, width, height, color):
    """添加矩形色块"""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_cover_slide(prs, title, subtitle='', funding=''):
    """封面页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    _add_background(slide, COLORS['primary_dark'])
    
    # 标题
    txBox = slide.shapes.add_textbox(
        Inches(1), Inches(2), Inches(11.333), Inches(1.5)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = title
    _set_font(run, size=48, bold=True, color=COLORS['white'])
    
    # 副标题
    if subtitle:
        txBox2 = slide.shapes.add_textbox(
            Inches(1), Inches(3.5), Inches(11.333), Inches(1)
        )
        tf2 = txBox2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.alignment = PP_ALIGN.CENTER
        run2 = p2.add_run()
        run2.text = subtitle
        _set_font(run2, size=28, color=RGBColor(0xFF, 0xFF, 0xFF))
    
    # 融资信息
    if funding:
        txBox3 = slide.shapes.add_textbox(
            Inches(1), Inches(4.8), Inches(11.333), Inches(0.8)
        )
        tf3 = txBox3.text_frame
        p3 = tf3.paragraphs[0]
        p3.alignment = PP_ALIGN.CENTER
        run3 = p3.add_run()
        run3.text = funding
        _set_font(run3, size=24, bold=True, color=COLORS['accent'])
    
    return slide


def add_title_bullets_slide(prs, title, bullets):
    """标题 + 要点列表页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    
    # 标题
    txBox = slide.shapes.add_textbox(
        Inches(0.8), Inches(0.5), Inches(11.733), Inches(1)
    )
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title
    _set_font(run, size=36, bold=True, color=COLORS['primary_dark'])
    
    # 左侧装饰线
    _add_rect(slide, Inches(0.8), Inches(1.3), Inches(0.08), Inches(0.5), COLORS['accent'])
    
    # Bullets
    bullet_top = Inches(2.0)
    for i, bullet in enumerate(bullets[:8]):  # 最多 8 条
        txBox_b = slide.shapes.add_textbox(
            Inches(1.2), bullet_top + Inches(i * 0.6), Inches(10.8), Inches(0.55)
        )
        tf_b = txBox_b.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        
        # 解析 **加粗** 文本
        parts = re.split(r'(\*\*[^*]+\*\*)', bullet)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                run_b = p_b.add_run()
                run_b.text = part[2:-2]
                _set_font(run_b, size=20, bold=True, color=COLORS['accent'])
            else:
                run_b = p_b.add_run()
                run_b.text = part
                _set_font(run_b, size=20, color=COLORS['text'])
    
    return slide


def add_table_slide(prs, title, header, rows):
    """数据表格页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    
    # 标题
    txBox = slide.shapes.add_textbox(
        Inches(0.8), Inches(0.5), Inches(11.733), Inches(0.8)
    )
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title
    _set_font(run, size=34, bold=True, color=COLORS['primary_dark'])
    
    if not header or not rows:
        return slide
    
    cols = len(header)
    # 过滤掉列数不匹配的行，并截取最多 10 行
    display_rows = [r for r in rows if len(r) == cols][:10]
    if not display_rows:
        return slide
    n_rows = len(display_rows) + 1  # +1 for header
    
    # 表格尺寸
    table_left = Inches(0.8)
    table_top = Inches(1.6)
    table_width = Inches(11.733)
    table_height = Inches(0.4 * n_rows + 0.2)
    
    table_shape = slide.shapes.add_table(
        n_rows, cols, table_left, table_top, table_width, table_height
    )
    table = table_shape.table
    
    # Header row
    for j, h in enumerate(header):
        cell = table.cell(0, j)
        cell.text = re.sub(r'\*\*([^*]+)\*\*', r'\1', h)  # 去除 markdown bold
        for paragraph in cell.text_frame.paragraphs:
            for run in paragraph.runs:
                _set_font(run, size=14, bold=True, color=COLORS['white'])
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLORS['table_header']
    
    # Data rows
    for i, row in enumerate(display_rows):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            clean_val = re.sub(r'\*\*([^*]+)\*\*', r'\1', val)
            cell.text = clean_val
            for paragraph in cell.text_frame.paragraphs:
                for run in paragraph.runs:
                    _set_font(run, size=13, color=COLORS['text'])
            # 交替行颜色
            if i % 2 == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLORS['bg_alt']
    
    return slide


def add_quote_slide(prs, quote_text):
    """核心洞察/引用页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_background(slide, COLORS['bg_alt'])
    
    # 大引号
    txBox_q = slide.shapes.add_textbox(
        Inches(1.5), Inches(1.5), Inches(1), Inches(1)
    )
    tf_q = txBox_q.text_frame
    p_q = tf_q.paragraphs[0]
    run_q = p_q.add_run()
    run_q.text = '\u201c'
    _set_font(run_q, size=72, bold=True, color=COLORS['accent'])
    
    # 引文
    txBox = slide.shapes.add_textbox(
        Inches(2), Inches(2.5), Inches(9.333), Inches(3)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = quote_text
    _set_font(run, size=28, color=COLORS['primary_dark'])
    
    return slide


def add_cta_slide(prs, vision, subtitle='', contact=''):
    """结束页 / CTA"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_background(slide, COLORS['primary_dark'])
    
    # 愿景
    txBox = slide.shapes.add_textbox(
        Inches(1), Inches(2.2), Inches(11.333), Inches(1.5)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = vision
    _set_font(run, size=40, bold=True, color=COLORS['white'])
    
    if subtitle:
        txBox2 = slide.shapes.add_textbox(
            Inches(1), Inches(3.8), Inches(11.333), Inches(1)
        )
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.alignment = PP_ALIGN.CENTER
        run2 = p2.add_run()
        run2.text = subtitle
        _set_font(run2, size=24, color=RGBColor(0xCC, 0xCC, 0xCC))
    
    # 感谢
    txBox3 = slide.shapes.add_textbox(
        Inches(1), Inches(5.5), Inches(11.333), Inches(0.8)
    )
    tf3 = txBox3.text_frame
    p3 = tf3.paragraphs[0]
    p3.alignment = PP_ALIGN.CENTER
    run3 = p3.add_run()
    run3.text = '感谢您的时间'
    _set_font(run3, size=20, color=COLORS['accent'])
    
    return slide


# ============================================
# Main Converter
# ============================================

def convert(input_path, output_path, template_path=None):
    """主转换流程"""
    md_text = Path(input_path).read_text(encoding='utf-8')
    sections = parse_markdown_sections(md_text)
    
    if template_path and Path(template_path).exists():
        prs = Presentation(template_path)
    else:
        prs = Presentation()
        prs.slide_width = SLIDE_WIDTH
        prs.slide_height = SLIDE_HEIGHT
    
    # === 生成 Slides ===
    
    for section in sections:
        title = section['title']
        is_cover = section.get('is_cover', False)
        
        # 封面
        if is_cover:
            # 从内容中提取副标题和融资信息
            subtitle = ''
            funding = ''
            for line in section['content']:
                if '融资' in line or '天使轮' in line or 'Pre-A' in line:
                    funding = re.sub(r'[*>#\-]', '', line).strip()
                elif line.strip() and not funding:
                    s = re.sub(r'[*>#\-]', '', line).strip()
                    if s and not subtitle:
                        subtitle = s
            add_cover_slide(prs, title, subtitle, funding)
            continue
        
        # 有表格的模块 → 表格页
        if section['tables']:
            header, data = extract_table(section['tables'])
            if header and data:
                add_table_slide(prs, title, header, data)
        
        # 有要点的模块 → 要点页
        elif section['bullets']:
            add_title_bullets_slide(prs, title, section['bullets'])
        
        # 有引用的模块 → 引用页
        elif section['quotes']:
            # 先做一个标题+要点页（如果有内容）
            quote = ' '.join(section['quotes'])
            add_quote_slide(prs, quote)
        
        # 纯文本模块 → 简单标题页
        else:
            text_lines = [l.strip() for l in section['content'] if l.strip()]
            if text_lines:
                add_title_bullets_slide(prs, title, text_lines[:6])
    
    # 结束页
    add_cta_slide(
        prs,
        vision='让每一个家庭都能找到好姻缘',
        subtitle='亲缘桥 — 父母安心、子女放心的婚恋平台',
        contact=''
    )
    
    prs.save(output_path)
    print(f'✅ 已生成: {output_path}')
    print(f'   Slides: {len(prs.slides)} 张')


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description='md2pptx — 投研报告 Markdown → 可编辑 PowerPoint'
    )
    parser.add_argument('--input', '-i', required=True, help='输入 Markdown 文件路径')
    parser.add_argument('--output', '-o', default='output.pptx', help='输出 .pptx 路径')
    parser.add_argument('--template', '-t', default=None, help='PowerPoint 模板文件路径')
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f'❌ 输入文件不存在: {args.input}')
        sys.exit(1)
    
    convert(args.input, args.output, args.template)


if __name__ == '__main__':
    main()
