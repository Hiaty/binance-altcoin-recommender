import json
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

# 读取分析数据
with open("altcoin_analysis_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 创建图片 - 增大尺寸以容纳更多列
width = 1800
height = 1200
img = Image.new('RGB', (width, height), color='#0d1117')
draw = ImageDraw.Draw(img)

# 字体设置
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    font_data = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
except:
    font_title = ImageFont.load_default()
    font_header = ImageFont.load_default()
    font_data = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_tiny = ImageFont.load_default()

# 颜色定义
colors = {
    'bg_dark': '#0d1117',
    'bg_card': '#161b22',
    'bg_header': '#21262d',
    'text_primary': '#c9d1d9',
    'text_secondary': '#8b949e',
    'accent_green': '#238636',
    'accent_red': '#da3633',
    'accent_yellow': '#d29922',
    'accent_blue': '#58a6ff',
    'border': '#30363d'
}

# 标题区域
draw.rectangle([(0, 0), (width, 80)], fill='#161b22')
draw.text((width//2, 25), "山寨币智能推荐系统", fill='#ffffff', font=font_title, anchor="mm")
draw.text((width//2, 55), "市值3000万+活跃币种 | 智能筛选 | K线形态分析", fill='#8b949e', font=font_small, anchor="mm")

# 图例说明区域
legend_y = 90
draw.text((30, legend_y), "【指标说明】", fill='#58a6ff', font=font_header)
legend_items = [
    ("历史最大回调", "从历史最高点下跌的幅度，数值越大说明回调越充分"),
    ("底部最大反弹", "从历史最低点上涨的幅度，反映底部反弹力度"),
    ("换手率", "24h交易量/市值，5-50%为健康区间"),
    ("本周/本月反弹", "相对于7天/30天前的涨跌幅"),
    ("持仓集中度", "前10大持有者占比，>80%为高度控盘"),
    ("日线/周线形态", "K线技术分析，识别趋势和买卖信号"),
    ("是否强庄币", "判断是否有庄家控盘迹象"),
    ("推荐评级", "综合评分: 推荐(40+分) 观望(20-40分) 不推荐(<20分)")
]

for i, (title, desc) in enumerate(legend_items):
    x = 30 + (i % 2) * 850
    y = legend_y + 25 + (i // 2) * 20
    draw.text((x, y), f"• {title}:", fill='#d29922', font=font_small)
    draw.text((x + 100, y), desc, fill='#8b949e', font=font_tiny)

# 表格起始位置
table_start_y = 210
row_height = 70

# 列定义: (标题, 宽度, 说明)
columns = [
    ("排名", 40, ""),
    ("代币", 70, ""),
    ("市值\n(万美元)", 70, ""),
    ("历史最大\n回调(%)", 70, "从高点下跌"),
    ("底部最大\n反弹(%)", 70, "从低点上涨"),
    ("换手率\n(%)", 60, "24h交易活跃度"),
    ("本周\n反弹(%)", 60, "7天涨跌幅"),
    ("本月\n反弹(%)", 60, "30天涨跌幅"),
    ("持仓\n集中度(%)", 70, "前10大持有者"),
    ("日线形态", 100, "K线技术分析"),
    ("周线形态", 100, "趋势判断"),
    ("币种分析\n点评", 180, "综合分析"),
    ("强庄币", 50, ""),
    ("推荐\n评级", 60, "")
]

# 计算列起始位置
col_starts = [20]
for col in columns[:-1]:
    col_starts.append(col_starts[-1] + col[1])

# 表头背景
draw.rectangle([(20, table_start_y), (width-20, table_start_y + 50)], fill='#21262d')

# 绘制表头
for i, (header, width_col, desc) in enumerate(columns):
    x = col_starts[i] + width_col // 2
    y = table_start_y + 25
    # 主标题
    lines = header.split('\n')
    for j, line in enumerate(lines):
        draw.text((x, y - 10 + j*12), line, fill='#ffffff', font=font_header, anchor="mm")
    # 副标题说明
    if desc:
        draw.text((x, y + 18), desc, fill='#8b949e', font=font_tiny, anchor="mm")

# 绘制数据行
for idx, r in enumerate(data[:12], 1):  # 只显示前12个
    y = table_start_y + 50 + (idx - 1) * row_height
    
    # 行背景（斑马纹）
    bg_color = '#161b22' if idx % 2 == 1 else '#0d1117'
    draw.rectangle([(20, y), (width-20, y + row_height)], fill=bg_color)
    
    # 排名
    draw.text((col_starts[0] + 20, y + 35), str(r['rank']), fill='#ffffff', font=font_data, anchor="mm")
    
    # 代币
    draw.text((col_starts[1] + 35, y + 25), r['symbol'], fill='#58a6ff', font=font_data, anchor="mm")
    draw.text((col_starts[1] + 35, y + 45), r['name'][:10], fill='#8b949e', font=font_tiny, anchor="mm")
    
    # 市值
    mc_str = f"{r['market_cap']/10000:.0f}"
    draw.text((col_starts[2] + 35, y + 35), mc_str, fill='#ffffff', font=font_data, anchor="mm")
    
    # 历史最大回调
    dd_color = '#238636' if r['max_drawdown'] > 50 else '#d29922' if r['max_drawdown'] > 30 else '#8b949e'
    draw.text((col_starts[3] + 35, y + 35), f"{r['max_drawdown']:.1f}", fill=dd_color, font=font_data, anchor="mm")
    
    # 底部最大反弹
    rb_color = '#238636' if r['max_rebound'] > 100 else '#d29922'
    draw.text((col_starts[4] + 35, y + 35), f"{r['max_rebound']:.0f}", fill=rb_color, font=font_data, anchor="mm")
    
    # 换手率
    turn_color = '#238636' if 5 < r['turnover_rate'] < 50 else '#da3633' if r['turnover_rate'] > 100 else '#8b949e'
    draw.text((col_starts[5] + 30, y + 35), f"{r['turnover_rate']:.1f}", fill=turn_color, font=font_data, anchor="mm")
    
    # 本周反弹
    week_color = '#238636' if r['week_change'] > 0 else '#da3633'
    draw.text((col_starts[6] + 30, y + 35), f"{r['week_change']:+.1f}", fill=week_color, font=font_data, anchor="mm")
    
    # 本月反弹
    month_color = '#238636' if r['month_change'] > 0 else '#da3633'
    draw.text((col_starts[7] + 30, y + 35), f"{r['month_change']:+.0f}", fill=month_color, font=font_data, anchor="mm")
    
    # 持仓集中度
    conc_color = '#da3633' if r['concentration'] > 80 else '#d29922' if r['concentration'] > 60 else '#238636'
    draw.text((col_starts[8] + 35, y + 35), f"{r['concentration']:.1f}", fill=conc_color, font=font_data, anchor="mm")
    
    # 日线形态
    daily_color = '#238636' if r['pattern_strength'] > 60 else '#d29922' if r['pattern_strength'] > 40 else '#8b949e'
    daily_text = r['daily_pattern'][:12] if len(r['daily_pattern']) > 12 else r['daily_pattern']
    draw.text((col_starts[9] + 50, y + 35), daily_text, fill=daily_color, font=font_tiny, anchor="mm")
    
    # 周线形态
    weekly_text = r['weekly_pattern'][:12] if len(r['weekly_pattern']) > 12 else r['weekly_pattern']
    draw.text((col_starts[10] + 50, y + 35), weekly_text, fill='#8b949e', font=font_tiny, anchor="mm")
    
    # 币种分析点评
    analysis_text = r['analysis'][:35] + "..." if len(r['analysis']) > 35 else r['analysis']
    # 分行显示
    words = analysis_text
    for i in range(0, min(len(words), 70), 35):
        line = words[i:i+35]
        draw.text((col_starts[11] + 90, y + 20 + (i//35)*15), line, fill='#c9d1d9', font=font_tiny, anchor="mm")
    
    # 是否强庄币
    whale_text = "是" if r['is_whale'] else "否"
    whale_color = '#da3633' if r['is_whale'] else '#238636'
    draw.text((col_starts[12] + 25, y + 35), whale_text, fill=whale_color, font=font_data, anchor="mm")
    
    # 推荐评级
    rec_colors = {'推荐': '#238636', '观望': '#d29922', '不推荐': '#da3633'}
    rec_color = rec_colors.get(r['recommendation'], '#8b949e')
    draw.rectangle([(col_starts[13] + 10, y + 20), (col_starts[13] + 50, y + 50)], fill=rec_color)
    draw.text((col_starts[13] + 30, y + 35), r['recommendation'], fill='#ffffff', font=font_tiny, anchor="mm")

# 底部统计区域
stats_y = table_start_y + 50 + len(data[:12]) * row_height + 20
draw.line([(50, stats_y), (width-50, stats_y)], fill='#30363d', width=2)

# 统计信息
rec_count = sum(1 for r in data if r['recommendation'] == '推荐')
watch_count = sum(1 for r in data if r['recommendation'] == '观望')
avoid_count = sum(1 for r in data if r['recommendation'] == '不推荐')
whale_count = sum(1 for r in data if r['is_whale'])

stats_text = f"统计: 共分析 {len(data)} 个代币 | 推荐: {rec_count} 个 | 观望: {watch_count} 个 | 不推荐: {avoid_count} 个 | 强庄币: {whale_count} 个"
draw.text((width//2, stats_y + 25), stats_text, fill='#8b949e', font=font_small, anchor="mm")

# 风险提示
draw.text((width//2, stats_y + 50), "⚠️ 风险提示: 本分析仅供参考，不构成投资建议。加密货币投资有风险，入市需谨慎。", fill='#da3633', font=font_small, anchor="mm")
draw.text((width//2, stats_y + 70), "数据来源: 币安Web3 | 分析时间: " + datetime.now().strftime('%Y-%m-%d %H:%M'), fill='#6e7681', font=font_tiny, anchor="mm")

# 保存图片
img.save("altcoin_recommendation_system.png", "PNG")
print("[OK] 推荐系统图片已生成: altcoin_recommendation_system.png")
