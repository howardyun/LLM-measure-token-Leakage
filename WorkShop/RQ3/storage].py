import matplotlib.pyplot as plt
import numpy as np

# 数据
platforms = ['MongoDB', 'PostgreSQL']
active_leaks = [31, 4]
total_leaks = [106, 105]
inactive_leaks = [total - active for total, active in zip(total_leaks, active_leaks)]

# 配色
colors = ['#FF6F61', '#D3D3D3']  # 红色：Active，灰色：Inactive

# 字体大小设置
font_label = 14
font_legend = 12
font_tick = 12
font_bar = 12

# 绘图
fig, ax = plt.subplots(figsize=(8, 6))
bar_width = 0.3  # 窄柱子

# 堆叠柱状图
bar1 = ax.bar(platforms, active_leaks, bar_width, label='Active Leaks', color=colors[0])
bar2 = ax.bar(platforms, inactive_leaks, bar_width, bottom=active_leaks, label='Inactive Leaks', color=colors[1])

# 添加柱子上的数值标签
for i in range(len(platforms)):
    ax.text(i, active_leaks[i] / 2, f'{active_leaks[i]}',
            ha='center', va='center', color='white', fontsize=font_bar, weight='bold')
    ax.text(i, active_leaks[i] + inactive_leaks[i] / 2, f'{inactive_leaks[i]}',
            ha='center', va='center', color='black', fontsize=font_bar)

# 设置轴标签
ax.set_ylabel('Number of Leaks', fontsize=font_label)
ax.tick_params(axis='x', labelsize=font_tick)
ax.tick_params(axis='y', labelsize=font_tick)

# ✅ 图注放右上角
ax.legend(loc='upper right', fontsize=font_legend)

# 保存为 PDF
plt.savefig("secret_leak_stackbar.pdf", format='pdf', bbox_inches='tight')

plt.tight_layout()
plt.show()
