import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("diagrams", exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9

def generate_pipeline():
    # 2 rows layout or wide horizontal flow
    # A 2-row serpentine or multi-tier pipeline layout gives plenty of space for descriptive text!
    # Let's do a crisp, structured 2-tier pipeline or 7-stage horizontal-vertical workflow.
    # 7 stages:
    # Row 1 (Left to Right): Step 1 -> Step 2 -> Step 3 -> Step 4
    # Flow down to Row 2: Step 4 -> Step 5
    # Row 2 (Right to Left or Left to Right with connector):
    # Step 4 -> Step 5 -> Step 6 -> Step 7
    # Even better: Left to Right across 2 rows with clear sweeping connector!
    # Stage 1 to 4 on top (x=5, 29, 53, 77; y=58)
    # Stage 5 to 7 on bottom (x=17, 41, 65; y=12) with a smooth right-to-left downward flow or clean wrap.
    # Or a 7-column landscape layout (figsize 16 x 7) which displays beautifully on A4 or 16:9 slides!
    
    fig, ax = plt.subplots(figsize=(16, 8.5), dpi=300)
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 95)
    ax.axis('off')

    # Background canvas tint
    bg_rect = patches.FancyBboxPatch((1, 1), 158, 93, boxstyle="round,pad=1.0", facecolor="#F8FAFC", edgecolor="#E2E8F0", linewidth=1.5)
    ax.add_patch(bg_rect)

    # Title Banner
    ax.text(80, 89, "QKRAFT: END-TO-END SCHEMA & QUERY OPTIMIZATION WORKFLOW", 
            fontsize=15, fontweight='bold', ha='center', va='center', color="#0F172A", family='sans-serif')
    ax.text(80, 85.2, "Automated Pre-Production DDL Analysis, Synthetic Sandboxing, Empirical Benchmarking & Profiling Pipeline", 
            fontsize=9.5, ha='center', va='center', color="#475569")

    # Define the 7 Stages
    # Stage layout: Top row (Steps 1, 2, 3, 4), Bottom row (Steps 5, 6, 7)
    stages = [
        {
            "num": "01",
            "title": "Developer DDL\nInput",
            "subtitle": "Raw SQL Script Ingestion",
            "details": ["• Ingest PostgreSQL / MySQL DDL", "• Syntax pre-cleaning & normalization", "• Web GUI / Monaco code editor"],
            "box": (6, 45, 33, 33),
            "theme": {"bg": "#EEF2FF", "border": "#4F46E5", "tag_bg": "#4F46E5", "text": "#312E81", "badge": "INPUT STAGE"}
        },
        {
            "num": "02",
            "title": "DDL Parsing &\nER Diagram",
            "subtitle": "AST Normalization & Graph",
            "details": ["• Table & column entity extraction", "• PK / FK relationship resolution", "• Dynamic SVG / Canvas schema visualizer"],
            "box": (44, 45, 33, 33),
            "theme": {"bg": "#E0F2FE", "border": "#0284C7", "tag_bg": "#0284C7", "text": "#0C4A6E", "badge": "VISUALIZATION"}
        },
        {
            "num": "03",
            "title": "Schema\nOptimisation",
            "subtitle": "Rules + Gemini AI Engine",
            "details": ["• Deterministic FK & join index rules", "• Contextual Gemini 1.5/2.0 AI audit", "• Generates optimized DDL delta"],
            "box": (82, 45, 33, 33),
            "theme": {"bg": "#FEF3C7", "border": "#D97706", "tag_bg": "#D97706", "text": "#78350F", "badge": "AI & HEURISTICS"}
        },
        {
            "num": "04",
            "title": "Sandbox Creation &\nSynthetic Data",
            "subtitle": "Isolated SQLite DB Seeding",
            "details": ["• Postgres -> SQLite dialect translation", "• Dynamic sandbox_{id}.db creation", "• Semantic mock rows synthesis (users/orders)"],
            "box": (120, 45, 33, 33),
            "theme": {"bg": "#F3E8FF", "border": "#9333EA", "tag_bg": "#9333EA", "text": "#581C87", "badge": "SANDBOX ENGINE"}
        },
        {
            "num": "05",
            "title": "Query\nAdvisory",
            "subtitle": "NL2SQL & Anti-Pattern Check",
            "details": ["• Natural Language -> Optimized SQL", "• Detects non-SARGable clauses", "• Query rewrite suggestions & hints"],
            "box": (120, 6, 33, 31),
            "theme": {"bg": "#FCE7F3", "border": "#DB2777", "tag_bg": "#DB2777", "text": "#831843", "badge": "QUERY ADVISOR"}
        },
        {
            "num": "06",
            "title": "Side-by-Side\nBenchmarking",
            "subtitle": "Empirical Execution Timing",
            "details": ["• Concurrent unopt vs opt test run", "• High-resolution millisecond timer", "• EXPLAIN plan scan/search diff"],
            "box": (82, 6, 33, 31),
            "theme": {"bg": "#DCFCE7", "border": "#16A34A", "tag_bg": "#16A34A", "text": "#14532D", "badge": "BENCHMARKING"}
        },
        {
            "num": "07",
            "title": "Metrics &\nHistory",
            "subtitle": "Analytics & Session Storage",
            "details": ["• Speedup % & absolute ms saved", "• Query history logs & comparisons", "• Persisted in metadata qkraft.db"],
            "box": (44, 6, 33, 31),
            "theme": {"bg": "#CCFBF1", "border": "#0D9488", "tag_bg": "#0D9488", "text": "#115E59", "badge": "ANALYTICS & AUDIT"}
        }
    ]

    for st in stages:
        x, y, w, h = st["box"]
        t = st["theme"]
        # Outer card
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8", 
                                      facecolor=t["bg"], edgecolor=t["border"], linewidth=2.0)
        ax.add_patch(card)

        # Header Pill / Badge
        pill = patches.FancyBboxPatch((x + 2, y + h - 4.5), 13, 3.6, boxstyle="round,pad=0.3",
                                      facecolor=t["tag_bg"], edgecolor=t["tag_bg"], linewidth=1.0)
        ax.add_patch(pill)
        ax.text(x + 8.5, y + h - 2.7, f"STEP {st['num']}", fontsize=7.5, fontweight='bold', ha='center', va='center', color='#FFFFFF')

        # Category Tag (Right side of header)
        ax.text(x + w - 2, y + h - 2.7, t["badge"], fontsize=6.8, fontweight='bold', ha='right', va='center', color=t["border"])

        # Title
        ax.text(x + 2.5, y + h - 8.2, st["title"], fontsize=10.5, fontweight='bold', ha='left', va='top', color=t["text"], linespacing=1.1)

        # Subtitle
        ax.text(x + 2.5, y + h - 14.2, st["subtitle"].upper(), fontsize=7.2, fontweight='bold', ha='left', va='top', color="#64748B")

        # Divider line
        ax.plot([x + 2.5, x + w - 2.5], [y + h - 16, y + h - 16], color=t["border"], alpha=0.35, linewidth=1.0)

        # Bullet details
        y_text = y + h - 18.5
        for detail in st["details"]:
            ax.text(x + 2.5, y_text, detail, fontsize=7.6, ha='left', va='top', color="#1E293B")
            y_text -= 3.8

    # Connecting Arrows
    arrow_style = dict(arrowstyle="-|>", lw=2.4, mutation_scale=16)

    # 1 -> 2
    ax.annotate("", xy=(43.5, 61.5), xytext=(39.5, 61.5), arrowprops=dict(**arrow_style, color="#0284C7"))
    ax.text(41.5, 63.5, "Raw SQL", fontsize=7.2, ha='center', fontweight='bold', color="#0284C7")

    # 2 -> 3
    ax.annotate("", xy=(81.5, 61.5), xytext=(77.5, 61.5), arrowprops=dict(**arrow_style, color="#D97706"))
    ax.text(79.5, 63.5, "Parsed Schema", fontsize=7.2, ha='center', fontweight='bold', color="#D97706")

    # 3 -> 4
    ax.annotate("", xy=(119.5, 61.5), xytext=(115.5, 61.5), arrowprops=dict(**arrow_style, color="#9333EA"))
    ax.text(117.5, 63.5, "Optimized DDL", fontsize=7.2, ha='center', fontweight='bold', color="#9333EA")

    # 4 -> 5 (Downward Turn on Right)
    # Curved path from bottom of 4 to top of 5
    ax.annotate("", xy=(136.5, 37.5), xytext=(136.5, 44.5), arrowprops=dict(**arrow_style, color="#DB2777"))
    ax.text(143.5, 41.0, "Isolated SQLite DB\n& Seeded Data", fontsize=7.0, ha='left', va='center', fontweight='bold', color="#DB2777")

    # 5 -> 6 (Right to Left on Bottom Row)
    ax.annotate("", xy=(115.5, 21.5), xytext=(119.5, 21.5), arrowprops=dict(**arrow_style, color="#16A34A"))
    ax.text(117.5, 23.5, "Candidate SQL", fontsize=7.2, ha='center', fontweight='bold', color="#16A34A")

    # 6 -> 7 (Right to Left on Bottom Row)
    ax.annotate("", xy=(77.5, 21.5), xytext=(81.5, 21.5), arrowprops=dict(**arrow_style, color="#0D9488"))
    ax.text(79.5, 23.5, "Execution Latency (ms)", fontsize=7.0, ha='center', fontweight='bold', color="#0D9488")

    # Leftmost Summary / Output Box (Aligns with Step 1 on the bottom left)
    summary_box = patches.FancyBboxPatch((6, 6), 33, 31, boxstyle="round,pad=0.8",
                                         facecolor="#FFFFFF", edgecolor="#3B82F6", linewidth=1.8, linestyle="--")
    ax.add_patch(summary_box)
    
    # Checkmark badge
    badge_circle = patches.Circle((22.5, 31.5), radius=3.2, facecolor="#3B82F6", edgecolor="#2563EB", linewidth=1.5)
    ax.add_patch(badge_circle)
    ax.text(22.5, 31.5, "✓", fontsize=11, fontweight='bold', ha='center', va='center', color="#FFFFFF")

    ax.text(22.5, 25.5, "DEVELOPER VALUE DELIVERED", fontsize=8.5, fontweight='bold', ha='center', va='center', color="#1E3A8A")
    
    val_points = [
        "✦ 40% - 95% Query Speedup",
        "✦ Zero Hallucination Risk (Verified)",
        "✦ Zero Manual Sandbox Config",
        "✦ Production-Ready DDL Delta"
    ]
    y_val = 21.5
    for vp in val_points:
        ax.text(8.5, y_val, vp, fontsize=7.8, ha='left', va='center', color="#0F172A", fontweight='bold')
        y_val -= 3.6

    # 7 -> Output summary arrow
    ax.annotate("", xy=(39.5, 21.5), xytext=(43.5, 21.5), arrowprops=dict(**arrow_style, color="#3B82F6"))

    plt.tight_layout()
    out_file = "diagrams/qkraft_pipeline_workflow.png"
    plt.savefig(out_file, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"[OK] High-resolution pipeline workflow diagram saved to: {out_file}")

if __name__ == "__main__":
    generate_pipeline()
