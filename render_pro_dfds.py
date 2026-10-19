import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 9

def draw_entity(ax, x, y, w, h, title, subtitle="", color="#F8FAFC", border="#334155"):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", facecolor=color, edgecolor=border, lw=2)
    ax.add_patch(rect)
    rect_inner = patches.FancyBboxPatch((x+0.6, y+0.6), w-1.2, h-1.2, boxstyle="square,pad=0", facecolor="none", edgecolor=border, lw=0.8, linestyle="--")
    ax.add_patch(rect_inner)
    if subtitle:
        ax.text(x + w/2, y + h*0.62, title, fontsize=9.5, fontweight='bold', ha='center', va='center', color='#0F172A')
        ax.text(x + w/2, y + h*0.35, subtitle, fontsize=8, ha='center', va='center', color='#475569')
    else:
        ax.text(x + w/2, y + h/2, title, fontsize=9.5, fontweight='bold', ha='center', va='center', color='#0F172A')

def draw_process(ax, x, y, w, h, proc_id, name, color="#E0F2FE", border="#0284C7"):
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.5", facecolor=color, edgecolor=border, lw=2)
    ax.add_patch(box)
    header_y = y + h * 0.68
    ax.plot([x+0.5, x+w-0.5], [header_y, header_y], color=border, lw=1.2)
    ax.text(x + w/2, y + h*0.84, f"PROCESS {proc_id}", fontsize=8, fontweight='bold', ha='center', va='center', color=border)
    ax.text(x + w/2, y + h*0.34, name, fontsize=8.2, fontweight='bold', ha='center', va='center', color='#0C4A6E')

def draw_store(ax, x, y, w, h, store_id, name):
    ax.plot([x, x+w], [y+h, y+h], color='#334155', lw=1.8)
    ax.plot([x, x+w], [y, y], color='#334155', lw=1.8)
    ax.plot([x, x], [y, y+h], color='#334155', lw=1.8)
    id_w = 4.5
    ax.plot([x+id_w, x+id_w], [y, y+h], color='#334155', lw=1.2)
    ax.fill_between([x, x+w], y, y+h, color='#F8FAFC')
    ax.text(x + id_w/2, y + h/2, store_id, fontsize=8, fontweight='bold', ha='center', va='center', color='#0F172A')
    ax.text(x + id_w + (w-id_w)/2, y + h/2, name, fontsize=8.2, fontweight='bold', ha='center', va='center', color='#1E293B')

# -------------------------------------------------------------
# 1. DFD LEVEL 0 (CONTEXT DIAGRAM)
# -------------------------------------------------------------
def gen0():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    draw_process(ax, 38, 20, 24, 18, "0.0", "QKraft Core\nOptimization System", color="#E0F2FE", border="#0284C7")
    draw_entity(ax, 4, 19, 18, 20, "Developer / User", "Database Designer\n& App Engineer", color="#F8FAFC", border="#475569")
    draw_entity(ax, 76, 36, 20, 18, "Google Gemini AI", "LLM API Service\n(Advisory Engine)", color="#FEF3C7", border="#D97706")
    draw_entity(ax, 76, 6, 20, 18, "SQLite Sandbox Engine", "Local File Storage\n(sandbox_<id>.db)", color="#EEF2FF", border="#4F46E5")

    # In/Out Flows
    ax.annotate("", xy=(38, 33), xytext=(22, 33), arrowprops=dict(arrowstyle="-|>", color="#0284C7", lw=1.8))
    ax.text(30, 35.5, "Raw SQL DDL / Prompts", fontsize=8, fontweight='bold', ha='center', color='#0284C7')

    ax.annotate("", xy=(22, 25), xytext=(38, 25), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.8))
    ax.text(30, 21, "ER Diagrams, Optimized DDL,\nBenchmark Latency & Stats", fontsize=8, fontweight='bold', ha='center', color='#065F46')

    # AI
    ax.annotate("", xy=(76, 47), xytext=(62, 35), arrowprops=dict(arrowstyle="-|>", color="#D97706", lw=1.6))
    ax.text(65, 44, "Schema DDL & Query", fontsize=7.5, fontweight='bold', color='#B45309', rotation=25)

    ax.annotate("", xy=(62, 31), xytext=(76, 42), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.6))
    ax.text(71, 34, "Optimized DDL & Advice", fontsize=7.5, fontweight='bold', color='#047857', rotation=25)

    # Sandbox
    ax.annotate("", xy=(76, 17), xytext=(62, 25), arrowprops=dict(arrowstyle="-|>", color="#4F46E5", lw=1.6))
    ax.text(65, 17.5, "Translated DDL & Queries", fontsize=7.5, fontweight='bold', color='#4338CA', rotation=-22)

    ax.annotate("", xy=(62, 21), xytext=(76, 12), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.6))
    ax.text(72, 19.5, "Execution Time & Results", fontsize=7.5, fontweight='bold', color='#047857', rotation=-22)

    plt.tight_layout()
    plt.savefig("diagrams/dfd_level_0.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("[OK] Re-rendered DFD Level 0.")

# -------------------------------------------------------------
# 2. DFD LEVEL 1 (FUNCTIONAL DECOMPOSITION)
# -------------------------------------------------------------
def gen1():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 85)
    ax.axis('off')

    # External Entity: User
    draw_entity(ax, 3, 33, 16, 22, "Developer", "(User)", color="#F8FAFC", border="#475569")

    # Top Row Processes
    draw_process(ax, 28, 62, 21, 15, "1.0", "DDL Parsing &\nER Diagramming", color="#E0F2FE", border="#0284C7")
    draw_process(ax, 58, 62, 21, 15, "2.0", "Rule & AI Schema\nOptimization", color="#FEF3C7", border="#D97706")
    draw_process(ax, 87, 62, 20, 15, "3.0", "Sandbox Setup &\nMock Data Seeding", color="#EEF2FF", border="#4F46E5")

    # Middle Data Stores
    draw_store(ax, 43, 44, 20, 6, "D1", "Saved Schemas DB")
    draw_store(ax, 86, 36, 21, 6, "D2", "SQLite Sandboxes")
    draw_store(ax, 43, 25, 20, 6, "D3", "Query History & Metrics")

    # Bottom Row Processes
    draw_process(ax, 28, 6, 21, 15, "4.0", "Query Advisor &\nNL2SQL Engine", color="#FCE7F3", border="#DB2777")
    draw_process(ax, 58, 6, 21, 15, "5.0", "Performance\nBenchmarking", color="#DCFCE7", border="#16A34A")

    # Flows Top Row
    # User -> 1.0 (Raw DDL)
    ax.annotate("", xy=(28, 69), xytext=(19, 52), arrowprops=dict(arrowstyle="-|>", color="#0284C7", lw=1.6))
    ax.text(21, 63, "Raw DDL", fontsize=7.5, fontweight='bold', color="#0284C7")

    # 1.0 -> User (ER Nodes)
    ax.annotate("", xy=(19, 47), xytext=(28, 63), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.6))
    ax.text(21, 54, "ER Nodes", fontsize=7.5, fontweight='bold', color="#059669")

    # 1.0 -> 2.0 (Parsed DDL)
    ax.annotate("", xy=(58, 69), xytext=(49, 69), arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.5))
    ax.text(53.5, 71.5, "Parsed DDL", fontsize=7.5, fontweight='bold', ha='center', color="#334155")

    # 1.0 -> D1 & 2.0 -> D1
    ax.annotate("", xy=(47, 50), xytext=(38, 62), arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.3))
    ax.annotate("", xy=(57, 50), xytext=(65, 62), arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.3))

    # 2.0 -> 3.0 (Optimized DDL)
    ax.annotate("", xy=(87, 69), xytext=(79, 69), arrowprops=dict(arrowstyle="-|>", color="#4F46E5", lw=1.5))
    ax.text(83, 71.5, "Optimized DDL", fontsize=7.5, fontweight='bold', ha='center', color="#4F46E5")

    # 3.0 -> D2 (Seed Sandbox)
    ax.annotate("", xy=(96, 42), xytext=(96, 62), arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.5))
    ax.text(98, 51, "Seed Sandbox", fontsize=7.5, fontweight='bold', color="#475569")

    # Flows Bottom Row
    # User -> 4.0 (Natural Language Prompt / Query)
    ax.annotate("", xy=(28, 14), xytext=(19, 36), arrowprops=dict(arrowstyle="-|>", color="#DB2777", lw=1.6))
    ax.text(18, 24, "NL Prompt / SQL", fontsize=7.5, fontweight='bold', color="#DB2777")

    # 4.0 -> 5.0 (Target SQL)
    ax.annotate("", xy=(58, 13), xytext=(49, 13), arrowprops=dict(arrowstyle="-|>", color="#16A34A", lw=1.5))
    ax.text(53.5, 15.5, "Target SQL", fontsize=7.5, fontweight='bold', ha='center', color="#16A34A")

    # 5.0 -> D2 (Execute query against sandbox)
    ax.annotate("", xy=(86, 36), xytext=(79, 17), arrowprops=dict(arrowstyle="<|-|>", color="#4F46E5", lw=1.5))
    ax.text(82, 23, "Exec Test", fontsize=7.5, fontweight='bold', color="#4F46E5")

    # 5.0 -> D3 (Save Benchmark)
    ax.annotate("", xy=(56, 25), xytext=(63, 21), arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.3))

    # 5.0 -> User (Manhattan / Right-angle connection around bottom to avoid ANY overlapping!)
    ax.annotate("", xy=(11, 33), xytext=(58, 8),
                arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.6, connectionstyle="angle,angleA=-180,angleB=90,rad=4"))
    ax.text(26, 2, "Benchmark Latency & % Time Saved", fontsize=7.5, fontweight='bold', color="#059669")

    plt.tight_layout()
    plt.savefig("diagrams/dfd_level_1.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("[OK] Re-rendered DFD Level 1.")

# -------------------------------------------------------------
# 3. DFD LEVEL 2 (SANDBOX & BENCHMARKING DEEP DIVE)
# -------------------------------------------------------------
def gen2():
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 60)
    ax.axis('off')

    # Input Entity Box
    draw_entity(ax, 3, 20, 15, 20, "Process 2.0", "Schemas Output\n(Original + Opt)", color="#F8FAFC", border="#475569")

    # Process 3.1
    draw_process(ax, 24, 38, 17, 16, "3.1", "Postgres-to-SQLite\nDialect Translator", color="#EEF2FF", border="#4F46E5")

    # Process 3.2
    draw_process(ax, 52, 38, 17, 16, "3.2", "Sandbox DB\nInitializer", color="#EEF2FF", border="#4F46E5")

    # Process 3.3
    draw_process(ax, 80, 38, 18, 16, "3.3", "Synthetic Mock\nData Generator", color="#EEF2FF", border="#4F46E5")

    # Data Store: Sandbox File
    draw_store(ax, 78, 17, 23, 6, "D2", "sandbox_<id>.db")

    # Process 5.1
    draw_process(ax, 52, 4, 17, 16, "5.1", "Side-by-Side\nQuery Runner", color="#DCFCE7", border="#16A34A")

    # Process 5.2
    draw_process(ax, 24, 4, 17, 16, "5.2", "Latency & Speedup\nMetric Calculator", color="#DCFCE7", border="#16A34A")

    # Connectors
    # In -> 3.1
    ax.annotate("", xy=(24, 44), xytext=(18, 36), arrowprops=dict(arrowstyle="-|>", color="#4F46E5", lw=1.6))
    ax.text(19, 42, "Postgres DDL", fontsize=7.5, fontweight='bold', color="#4F46E5")

    # 3.1 -> 3.2 (Clean 11-unit gap)
    ax.annotate("", xy=(52, 44), xytext=(41, 44), arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.4))
    ax.text(46.5, 46.5, "SQLite SQL", fontsize=7.5, fontweight='bold', ha='center', color="#334155")

    # 3.2 -> 3.3 (Clean 11-unit gap)
    ax.annotate("", xy=(80, 44), xytext=(69, 44), arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.4))
    ax.text(74.5, 46.5, "Schema Tables", fontsize=7.5, fontweight='bold', ha='center', color="#334155")

    # 3.3 -> D2
    ax.annotate("", xy=(89, 23), xytext=(89, 38), arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.5))
    ax.text(91, 31, "Seed Mock Rows", fontsize=7.5, fontweight='bold', color="#475569")

    # D2 -> 5.1
    ax.annotate("", xy=(69, 14), xytext=(78, 19), arrowprops=dict(arrowstyle="<|-|>", color="#16A34A", lw=1.5))
    ax.text(75, 14, "Exec Test", fontsize=7.5, fontweight='bold', color="#16A34A")

    # 5.1 -> 5.2 (Clean 11-unit gap)
    ax.annotate("", xy=(41, 12), xytext=(52, 12), arrowprops=dict(arrowstyle="-|>", color="#16A34A", lw=1.5))
    ax.text(46.5, 14.5, "t_unopt, t_opt", fontsize=7.5, fontweight='bold', ha='center', color="#16A34A")

    # 5.2 -> Output Box
    ax.annotate("", xy=(18, 25), xytext=(24, 16), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.6))
    ax.text(17, 18, "% Saved & Metrics", fontsize=7.5, fontweight='bold', color="#059669")

    plt.tight_layout()
    plt.savefig("diagrams/dfd_level_2.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("[OK] Re-rendered DFD Level 2.")

if __name__ == "__main__":
    gen0()
    gen1()
    gen2()
