import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("diagrams", exist_ok=True)

# Set common styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

# -------------------------------------------------------------
# 1. DFD Level 0 (Context Diagram)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Title
ax.text(50, 95, "DFD Level 0: Context Diagram for QKraft", fontsize=14, fontweight='bold', ha='center', color='#1E3A8A')

# Process 0: Central Circle
circle = patches.Circle((50, 50), radius=16, facecolor='#DBEAFE', edgecolor='#1E40AF', linewidth=2.5)
ax.add_patch(circle)
ax.text(50, 53, "0.0", fontsize=12, fontweight='bold', ha='center', color='#1E40AF')
ax.text(50, 48, "QKraft\nOptimizer System", fontsize=10, fontweight='bold', ha='center', va='center', color='#1E3A8A')

# Entity 1: User / Developer (Left)
rect_user = patches.FancyBboxPatch((4, 38), 18, 24, boxstyle="round,pad=0.5", facecolor='#F3F4F6', edgecolor='#374151', linewidth=2)
ax.add_patch(rect_user)
ax.text(13, 50, "Developer /\nDatabase Admin\n(User)", fontsize=9, fontweight='bold', ha='center', va='center', color='#111827')

# Entity 2: Google Gemini AI (Top Right)
rect_ai = patches.FancyBboxPatch((76, 64), 20, 20, boxstyle="round,pad=0.5", facecolor='#FEF3C7', edgecolor='#D97706', linewidth=2)
ax.add_patch(rect_ai)
ax.text(86, 74, "External AI Service\n(Google Gemini)", fontsize=9, fontweight='bold', ha='center', va='center', color='#92400E')

# Entity 3: Sandbox Storage / DB (Bottom Right)
rect_db = patches.FancyBboxPatch((76, 16), 20, 20, boxstyle="round,pad=0.5", facecolor='#E0E7FF', edgecolor='#4338CA', linewidth=2)
ax.add_patch(rect_db)
ax.text(86, 26, "Sandbox Engine\n& Metadata DB\n(SQLite Engine)", fontsize=9, fontweight='bold', ha='center', va='center', color='#312E81')

# Arrows & Labels: User <-> Process
# User to Process
ax.annotate("", xy=(34, 55), xytext=(22, 55),
            arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.8))
ax.text(28, 57, "1. Raw DDL / Query Prompt", fontsize=7.5, ha='center', color='#1E40AF', fontweight='semibold')

# Process to User
ax.annotate("", xy=(22, 45), xytext=(34, 45),
            arrowprops=dict(arrowstyle="->", color="#059669", lw=1.8))
ax.text(28, 41, "2. Visual ERD, Optimized DDL,\nBenchmark Latency & Stats", fontsize=7.5, ha='center', color='#065F46', fontweight='semibold')

# Process <-> Gemini AI
ax.annotate("", xy=(76, 72), xytext=(63, 60),
            arrowprops=dict(arrowstyle="->", color="#D97706", lw=1.8))
ax.text(67, 68, "Schema / Query Context", fontsize=7.5, rotation=35, color='#92400E', fontweight='semibold')

ax.annotate("", xy=(61, 56), xytext=(76, 68),
            arrowprops=dict(arrowstyle="->", color="#059669", lw=1.8))
ax.text(71, 59, "Recommendations & SQL", fontsize=7.5, rotation=35, color='#065F46', fontweight='semibold')

# Process <-> Sandbox DB
ax.annotate("", xy=(76, 28), xytext=(63, 40),
            arrowprops=dict(arrowstyle="->", color="#4338CA", lw=1.8))
ax.text(67, 36, "Translated DDL & Test Queries", fontsize=7.5, rotation=-35, color='#312E81', fontweight='semibold')

ax.annotate("", xy=(61, 44), xytext=(76, 32),
            arrowprops=dict(arrowstyle="->", color="#059669", lw=1.8))
ax.text(71, 41, "Execution Times & Row Counts", fontsize=7.5, rotation=-35, color='#065F46', fontweight='semibold')

plt.tight_layout()
dfd0_path = "diagrams/dfd_level_0.png"
plt.savefig(dfd0_path, bbox_inches='tight', dpi=300)
plt.close()
print("DFD Level 0 saved.")
