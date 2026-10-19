import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

os.makedirs("diagrams", exist_ok=True)
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9

# ==============================================================================
# 1. GENERATE DFD LEVEL 0
# ==============================================================================
def generate_dfd0():
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Central Process 0.0
    circle = patches.Circle((50, 50), radius=15, facecolor='#E0F2FE', edgecolor='#0284C7', linewidth=2.2)
    ax.add_patch(circle)
    ax.text(50, 53, "0.0", fontsize=11, fontweight='bold', ha='center', color='#0369A1')
    ax.text(50, 48, "QKraft\nOptimizer System", fontsize=9, fontweight='bold', ha='center', va='center', color='#0C4A6E')

    # Entity: User / Developer (Left)
    rect_user = patches.FancyBboxPatch((5, 38), 18, 24, boxstyle="round,pad=0.5", facecolor='#F3F4F6', edgecolor='#4B5563', linewidth=1.8)
    ax.add_patch(rect_user)
    ax.text(14, 50, "Developer /\nDatabase Admin\n(User)", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#1F2937')

    # Entity: External AI (Top Right)
    rect_ai = patches.FancyBboxPatch((76, 65), 19, 20, boxstyle="round,pad=0.5", facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.8)
    ax.add_patch(rect_ai)
    ax.text(85.5, 75, "AI Engine\n(Google Gemini API)", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#92400E')

    # Entity: Sandbox Storage (Bottom Right)
    rect_db = patches.FancyBboxPatch((76, 15), 19, 20, boxstyle="round,pad=0.5", facecolor='#EEF2FF', edgecolor='#4F46E5', linewidth=1.8)
    ax.add_patch(rect_db)
    ax.text(85.5, 25, "Sandbox & Engine\nStorage\n(SQLite Files)", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#312E81')

    # Arrows User <-> Process
    ax.annotate("", xy=(35, 54), xytext=(23, 54), arrowprops=dict(arrowstyle="-|>", color="#0284C7", lw=1.6))
    ax.text(29, 56, "Raw DDL / Query Prompts", fontsize=7.5, ha='center', color='#0369A1', fontweight='bold')

    ax.annotate("", xy=(23, 46), xytext=(35, 46), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.6))
    ax.text(29, 41, "ER Diagram, Optimized DDL,\nBenchmark Latency & Stats", fontsize=7.5, ha='center', color='#065F46', fontweight='bold')

    # Arrows Process <-> AI
    ax.annotate("", xy=(76, 73), xytext=(63, 59), arrowprops=dict(arrowstyle="-|>", color="#D97706", lw=1.6))
    ax.text(67, 68, "Schema / Query Prompt", fontsize=7, rotation=35, color='#92400E', fontweight='bold')

    ax.annotate("", xy=(60, 56), xytext=(76, 68), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.6))
    ax.text(70, 58, "Recommendations & SQL", fontsize=7, rotation=35, color='#065F46', fontweight='bold')

    # Arrows Process <-> DB
    ax.annotate("", xy=(76, 27), xytext=(63, 41), arrowprops=dict(arrowstyle="-|>", color="#4F46E5", lw=1.6))
    ax.text(67, 36, "Translated DDL & Queries", fontsize=7, rotation=-35, color='#312E81', fontweight='bold')

    ax.annotate("", xy=(60, 44), xytext=(76, 31), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.6))
    ax.text(70, 42, "Execution Results & Timing", fontsize=7, rotation=-35, color='#065F46', fontweight='bold')

    plt.tight_layout()
    plt.savefig("diagrams/dfd_level_0.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("[OK] DFD Level 0 saved.")

# ==============================================================================
# 2. GENERATE DFD LEVEL 1
# ==============================================================================
def generate_dfd1():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Entity: User (Left)
    user_box = patches.FancyBboxPatch((3, 40), 14, 22, boxstyle="round,pad=0.4", facecolor='#F3F4F6', edgecolor='#374151', lw=1.8)
    ax.add_patch(user_box)
    ax.text(10, 51, "Developer /\nUser", fontsize=9, fontweight='bold', ha='center', va='center')

    # Process 1.0: DDL Ingestion & Parsing
    p1 = patches.Circle((32, 78), radius=8, facecolor='#E0F2FE', edgecolor='#0284C7', lw=1.8)
    ax.add_patch(p1)
    ax.text(32, 80, "1.0", fontsize=8.5, fontweight='bold', ha='center', color='#0369A1')
    ax.text(32, 76, "DDL Parsing &\nDiagramming", fontsize=7.5, fontweight='bold', ha='center', color='#0C4A6E')

    # Process 2.0: AI & Heuristic Optimization
    p2 = patches.Circle((62, 78), radius=8, facecolor='#FEF3C7', edgecolor='#D97706', lw=1.8)
    ax.add_patch(p2)
    ax.text(62, 80, "2.0", fontsize=8.5, fontweight='bold', ha='center', color='#B45309')
    ax.text(62, 76, "Schema\nOptimization", fontsize=7.5, fontweight='bold', ha='center', color='#78350F')

    # Process 3.0: Sandbox Population
    p3 = patches.Circle((92, 50), radius=8, facecolor='#EEF2FF', edgecolor='#4F46E5', lw=1.8)
    ax.add_patch(p3)
    ax.text(92, 52, "3.0", fontsize=8.5, fontweight='bold', ha='center', color='#4338CA')
    ax.text(92, 48, "Sandbox DB\n& Seeding", fontsize=7.5, fontweight='bold', ha='center', color='#312E81')

    # Process 4.0: Query Advisory & NL2SQL
    p4 = patches.Circle((32, 22), radius=8, facecolor='#FCE7F3', edgecolor='#DB2777', lw=1.8)
    ax.add_patch(p4)
    ax.text(32, 24, "4.0", fontsize=8.5, fontweight='bold', ha='center', color='#BE185D')
    ax.text(32, 20, "Query Advisory\n& Generation", fontsize=7.5, fontweight='bold', ha='center', color='#831843')

    # Process 5.0: Performance Benchmarking
    p5 = patches.Circle((62, 22), radius=8, facecolor='#DCFCE7', edgecolor='#16A34A', lw=1.8)
    ax.add_patch(p5)
    ax.text(62, 24, "5.0", fontsize=8.5, fontweight='bold', ha='center', color='#15803D')
    ax.text(62, 20, "Performance\nBenchmarker", fontsize=7.5, fontweight='bold', ha='center', color='#14532D')

    # Data Store D1: Schemas Table (Top Center)
    def draw_datastore(x, y, w, h, label):
        ax.plot([x, x+w], [y+h, y+h], color='#4B5563', lw=1.8)
        ax.plot([x, x+w], [y, y], color='#4B5563', lw=1.8)
        ax.fill_between([x, x+w], y, y+h, color='#F9FAFB')
        ax.text(x+w/2, y+h/2, label, fontsize=7.5, fontweight='bold', ha='center', va='center', color='#1F2937')

    draw_datastore(42, 50, 16, 7, "D1: Schemas DB")
    draw_datastore(70, 50, 16, 7, "D2: Sandbox DBs")
    draw_datastore(42, 3, 16, 7, "D3: Query History")

    # Connectors
    # User -> 1.0 (Raw DDL)
    ax.annotate("", xy=(24, 76), xytext=(17, 58), arrowprops=dict(arrowstyle="-|>", color="#0284C7", lw=1.5))
    ax.text(17, 70, "Raw DDL", fontsize=7, color="#0284C7", fontweight='bold')

    # 1.0 -> User (ER Diagram data)
    ax.annotate("", xy=(17, 54), xytext=(26, 72), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.5))
    ax.text(16, 62, "Diagram Nodes", fontsize=7, color="#059669", fontweight='bold')

    # 1.0 -> D1
    ax.annotate("", xy=(46, 57), xytext=(38, 72), arrowprops=dict(arrowstyle="-|>", color="#4B5563", lw=1.2))

    # 1.0 -> 2.0
    ax.annotate("", xy=(54, 78), xytext=(40, 78), arrowprops=dict(arrowstyle="-|>", color="#4B5563", lw=1.2))
    ax.text(47, 80, "Parsed Tables", fontsize=7, ha='center')

    # 2.0 -> D1 (Save optimized schema)
    ax.annotate("", xy=(54, 57), xytext=(58, 71), arrowprops=dict(arrowstyle="-|>", color="#4B5563", lw=1.2))

    # 2.0 -> 3.0 (Send schemas to sandbox)
    ax.annotate("", xy=(86, 56), xytext=(69, 74), arrowprops=dict(arrowstyle="-|>", color="#4F46E5", lw=1.4))
    ax.text(79, 68, "Schemas for Sandbox", fontsize=7, color="#4F46E5", fontweight='bold')

    # 3.0 -> D2 (Populate sqlite files)
    ax.annotate("", xy=(86, 53), xytext=(84, 53), arrowprops=dict(arrowstyle="<|-|>", color="#4B5563", lw=1.4))

    # User -> 4.0 (Natural Language Prompt / Query)
    ax.annotate("", xy=(25, 26), xytext=(17, 44), arrowprops=dict(arrowstyle="-|>", color="#DB2777", lw=1.5))
    ax.text(15, 34, "NL Prompt/SQL", fontsize=7, color="#DB2777", fontweight='bold')

    # 4.0 -> 5.0 (Generated SQL)
    ax.annotate("", xy=(54, 22), xytext=(40, 22), arrowprops=dict(arrowstyle="-|>", color="#16A34A", lw=1.4))
    ax.text(47, 24, "Candidate SQL", fontsize=7, color="#16A34A", fontweight='bold', ha='center')

    # 5.0 -> D2 (Execute against Sandbox)
    ax.annotate("", xy=(76, 50), xytext=(68, 28), arrowprops=dict(arrowstyle="<|-|>", color="#4F46E5", lw=1.4))
    ax.text(75, 37, "Test Executions", fontsize=7, color="#4F46E5", fontweight='bold')

    # 5.0 -> D3 (Log metrics)
    ax.annotate("", xy=(56, 10), xytext=(60, 15), arrowprops=dict(arrowstyle="-|>", color="#4B5563", lw=1.2))

    # 5.0 -> User (Performance modal & metrics)
    ax.annotate("", xy=(17, 48), xytext=(54, 25), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.5))
    ax.text(32, 40, "Execution Benchmark & % Saved", fontsize=7, color="#059669", fontweight='bold')

    plt.tight_layout()
    plt.savefig("diagrams/dfd_level_1.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("[OK] DFD Level 1 saved.")

# ==============================================================================
# 3. GENERATE DFD LEVEL 2 (Sandbox & Benchmarking Engine)
# ==============================================================================
def generate_dfd2():
    fig, ax = plt.subplots(figsize=(10.5, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Input on Left
    in_box = patches.FancyBboxPatch((3, 40), 16, 20, boxstyle="round,pad=0.4", facecolor='#F3F4F6', edgecolor='#4B5563', lw=1.6)
    ax.add_patch(in_box)
    ax.text(11, 50, "Original &\nOptimized DDL\n(from Process 2.0)", fontsize=8, fontweight='bold', ha='center', va='center')

    # Sub-process 3.1: Dialect Translator
    p31 = patches.Circle((32, 70), radius=7.5, facecolor='#EEF2FF', edgecolor='#4F46E5', lw=1.6)
    ax.add_patch(p31)
    ax.text(32, 72, "3.1", fontsize=8, fontweight='bold', ha='center', color='#4338CA')
    ax.text(32, 68, "Dialect\nTranslator", fontsize=7, fontweight='bold', ha='center', color='#312E81')

    # Sub-process 3.2: SQLite Sandbox Builder
    p32 = patches.Circle((57, 70), radius=7.5, facecolor='#EEF2FF', edgecolor='#4F46E5', lw=1.6)
    ax.add_patch(p32)
    ax.text(57, 72, "3.2", fontsize=8, fontweight='bold', ha='center', color='#4338CA')
    ax.text(57, 68, "Sandbox\nBuilder", fontsize=7, fontweight='bold', ha='center', color='#312E81')

    # Sub-process 3.3: Mock Data Synthesizer
    p33 = patches.Circle((82, 70), radius=7.5, facecolor='#EEF2FF', edgecolor='#4F46E5', lw=1.6)
    ax.add_patch(p33)
    ax.text(82, 72, "3.3", fontsize=8, fontweight='bold', ha='center', color='#4338CA')
    ax.text(82, 68, "Mock Data\nPopulator", fontsize=7, fontweight='bold', ha='center', color='#312E81')

    # Data Store: Sandbox File
    ax.plot([72, 92], [42, 42], color='#4B5563', lw=1.6)
    ax.plot([72, 92], [34, 34], color='#4B5563', lw=1.6)
    ax.fill_between([72, 92], 34, 42, color='#F9FAFB')
    ax.text(82, 38, "sandbox_{id}.db", fontsize=7.5, fontweight='bold', ha='center', va='center')

    # Sub-process 5.1: Query Execution Timer
    p51 = patches.Circle((57, 22), radius=7.5, facecolor='#DCFCE7', edgecolor='#16A34A', lw=1.6)
    ax.add_patch(p51)
    ax.text(57, 24, "5.1", fontsize=8, fontweight='bold', ha='center', color='#15803D')
    ax.text(57, 20, "Side-by-Side\nExecution", fontsize=7, fontweight='bold', ha='center', color='#14532D')

    # Sub-process 5.2: Metric Evaluator & Plan Diff
    p52 = patches.Circle((32, 22), radius=7.5, facecolor='#DCFCE7', edgecolor='#16A34A', lw=1.6)
    ax.add_patch(p52)
    ax.text(32, 24, "5.2", fontsize=8, fontweight='bold', ha='center', color='#15803D')
    ax.text(32, 20, "Speedup &\nPlan Diff", fontsize=7, fontweight='bold', ha='center', color='#14532D')

    # Flows
    ax.annotate("", xy=(25, 68), xytext=(19, 56), arrowprops=dict(arrowstyle="-|>", color="#4F46E5", lw=1.4))
    ax.text(17, 65, "Postgres DDL", fontsize=7, color="#4F46E5", fontweight='bold')

    ax.annotate("", xy=(50, 70), xytext=(40, 70), arrowprops=dict(arrowstyle="-|>", color="#4B5563", lw=1.3))
    ax.text(45, 72, "SQLite DDL", fontsize=6.5, ha='center')

    ax.annotate("", xy=(75, 70), xytext=(65, 70), arrowprops=dict(arrowstyle="-|>", color="#4B5563", lw=1.3))
    ax.text(70, 72, "Empty Tables", fontsize=6.5, ha='center')

    ax.annotate("", xy=(82, 43), xytext=(82, 62), arrowprops=dict(arrowstyle="-|>", color="#4B5563", lw=1.3))
    ax.text(85, 52, "Insert Sample Rows", fontsize=6.5, color="#1F2937")

    # Queries flow into 5.1
    ax.annotate("", xy=(75, 36), xytext=(64, 25), arrowprops=dict(arrowstyle="<|-|>", color="#16A34A", lw=1.4))
    ax.text(72, 28, "Run Original & Optimized", fontsize=6.5, color="#15803D", fontweight='bold')

    # 5.1 -> 5.2 (Raw times)
    ax.annotate("", xy=(40, 22), xytext=(50, 22), arrowprops=dict(arrowstyle="-|>", color="#16A34A", lw=1.4))
    ax.text(45, 24, "t_unopt, t_opt", fontsize=7, ha='center', color="#15803D")

    # 5.2 -> User Output
    ax.annotate("", xy=(15, 40), xytext=(26, 26), arrowprops=dict(arrowstyle="-|>", color="#059669", lw=1.4))
    ax.text(13, 30, "% Time Saved,\nPlan Comparison", fontsize=7, color="#059669", fontweight='bold')

    plt.tight_layout()
    plt.savefig("diagrams/dfd_level_2.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("[OK] DFD Level 2 saved.")

# ==============================================================================
# 4. WORD DOCUMENT CREATION WITH CUSTOM STYLES & EMBEDDED DIAGRAMS
# ==============================================================================
def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def style_table(table, header_bg="1E3A8A", alt_bg="F8FAFC"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
            if i == 0:
                set_cell_background(cell, header_bg)
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
            elif i % 2 == 1:
                set_cell_background(cell, alt_bg)
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
            else:
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)

def build_docx_report():
    doc = docx.Document()

    # Configure Margins (Normal 1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59) # Slate 800

    # Header / Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("PROJECT REVIEW 1 REPORT")
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(30, 58, 138) # Deep Blue

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(14)
    run_sub = sub_p.add_run("QKraft: AI-Driven Database Schema & Query Optimization Platform")
    run_sub.font.size = Pt(14)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Metadata Box (Table)
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Project Title", "QKraft – Automated Schema & Query Optimizer"),
        ("Student / Developer", "Romel"),
        ("Domain & Area", "Database Engineering, Artificial Intelligence & Cloud Developer Tools"),
        ("Review Milestone", "Project Review 1 (Phase 1 Progress & Architecture Defense)")
    ]
    for idx, (label, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(4.3)
        p1 = cell_lbl.paragraphs[0]
        r1 = p1.add_run(label)
        r1.bold = True
        r1.font.color.rgb = RGBColor(30, 58, 138)
        p2 = cell_val.paragraphs[0]
        p2.add_run(val)
    style_table(meta_table, header_bg="E2E8F0", alt_bg="F1F5F9")
    # fix text color in header row since we used light bg
    for cell in meta_table.rows[0].cells:
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Helper function for adding styled headings
    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(14, 116, 144) # Teal / Cyan 700
        return h

    # Section 1: Executive Summary
    add_h1("1. Executive Summary")
    p = doc.add_paragraph(
        "In modern web applications, the performance and scalability of backend services are critically dependent on relational database design. "
        "However, application developers frequently deploy schemas containing structural design flaws—such as unindexed foreign keys, absent primary keys, "
        "and sub-optimal data types. These errors lead to high disk I/O, sequential table scans, slow query executions, and unnecessary cloud database bills.\n\n"
        "QKraft is an intelligent developer workbench created to solve these challenges proactively. It ingests standard SQL Data Definition Language (DDL) scripts, "
        "analyzes them using rule-based heuristics and generative AI, renders interactive Entity-Relationship (ER) diagrams, and spins up an isolated sandbox database "
        "populated with synthetic data. QKraft then executes candidate queries against both the unoptimized and optimized schemas side-by-side, measuring exact "
        "latency in milliseconds and proving performance gains with measurable data."
    )
    p.paragraph_format.line_spacing = 1.15

    # Section 2: Problem Statement & Motivation
    add_h1("2. Problem Statement & Motivation")
    p = doc.add_paragraph(
        "Relational database optimization has traditionally suffered from three fundamental bottlenecks:"
    )
    p.paragraph_format.line_spacing = 1.15
    doc.add_paragraph("• Reactive Rather Than Proactive: Query performance is usually examined only after an application goes live and users report slow response times or query logs show timeouts.", style='List Bullet')
    doc.add_paragraph("• High Barrier to DBA Expertise: Identifying missing compound indexes, table joins, and execution plan anomalies requires specialized database administration skills that many full-stack developers lack.", style='List Bullet')
    doc.add_paragraph("• Friction in Testing Alternatives: Developers hesitate to modify table schemas or add B-Tree indexes in live or staging environments because creating safe sandboxes with realistic test rows is tedious and time-consuming.", style='List Bullet')

    # Section 3: Project Objectives
    add_h1("3. Project Objectives")
    doc.add_paragraph("1. Automated DDL Parsing & Visualization: Ingest raw SQL DDL and render a clean, interactive entity-relationship diagram with foreign key associations.", style='List Number')
    doc.add_paragraph("2. Dual-Layer Schema Optimization: Combine deterministic pattern-matching rules (for primary/foreign keys and index placement) with Google Gemini AI for contextual schema refactoring.", style='List Number')
    doc.add_paragraph("3. Isolated SQLite Sandbox Engine: Automatically translate standard/Postgres DDL into a functioning SQLite sandbox environment with automated realistic mock data generation.", style='List Number')
    doc.add_paragraph("4. Query Advisor & Natural Language Prompting: Provide an intelligent SQL assistant that converts user intent into optimized SQL statements.", style='List Number')
    doc.add_paragraph("5. Side-by-Side Performance Benchmarking: Execute queries against both unoptimized and optimized schemas, measuring runtime in milliseconds, row counts, and percentage time saved.", style='List Number')

    # Section 4: Existing System vs. Proposed System
    add_h1("4. Existing System vs. Proposed System")
    comp_table = doc.add_table(rows=6, cols=3)
    headers = ["Evaluation Metric", "Traditional Existing Approach", "Proposed System (QKraft)"]
    for j, h_text in enumerate(headers):
        comp_table.rows[0].cells[j].paragraphs[0].text = h_text
    
    comparisons = [
        ("Analysis Stage", "Post-production (slow query logs, APM tools)", "Pre-production (during schema design & development)"),
        ("Schema Recommendations", "Manual DBA code review & trial-and-error", "Instant automated rule engine + Gemini AI advisor"),
        ("ER Diagramming", "Separate static tools (draw.io, dbdiagram.io)", "Built-in dynamic SVG/Canvas entity relationship graph"),
        ("Safe Sandbox Validation", "Requires manual Docker setup & custom SQL seed scripts", "One-click automated SQLite sandbox with synthetic mock records"),
        ("Performance Proof", "Theoretical EXPLAIN plan interpretations", "Empirical side-by-side timing in milliseconds & % speedup")
    ]
    for i, row_data in enumerate(comparisons, start=1):
        row = comp_table.rows[i]
        for j, val in enumerate(row_data):
            row.cells[j].paragraphs[0].text = val
    style_table(comp_table, header_bg="1E3A8A", alt_bg="F8FAFC")

    # Section 5: Data Flow Diagrams (DFD)
    add_h1("5. Data Flow Diagrams (DFD)")
    p = doc.add_paragraph(
        "Data Flow Diagrams (DFDs) visually map how information enters, traverses, transforms, and is persisted across the QKraft platform. "
        "The following hierarchical diagrams describe the system from high-level context down to the inner mechanics of the sandbox execution engine."
    )
    p.paragraph_format.line_spacing = 1.15

    # 5.1 Level 0
    add_h2("5.1 DFD Level 0: Context Diagram")
    p0 = doc.add_paragraph(
        "The Context Diagram (Level 0) treats the entire QKraft platform as a single process (Process 0.0), showing interactions with three key external entities: "
        "the Developer/User, the external Google Gemini AI engine, and the underlying Sandbox Database storage."
    )
    p0.paragraph_format.line_spacing = 1.15

    # Insert Image 0
    doc.add_picture("diagrams/dfd_level_0.png", width=Inches(6.2))
    cap0 = doc.add_paragraph("Figure 1: DFD Level 0 – Context Diagram for QKraft Platform")
    cap0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap0.runs[0].font.size = Pt(9.5)
    cap0.runs[0].font.italic = True
    cap0.paragraph_format.space_after = Pt(12)

    # 5.2 Level 1
    add_h2("5.2 DFD Level 1: Functional Decomposition")
    p1_desc = doc.add_paragraph(
        "The Level 1 DFD decomposes the system into five core functional processes and three dedicated data stores:\n"
        "• Process 1.0 (DDL Parsing & Diagramming): Ingests DDL, extracts relational entities, and normalizes table structures.\n"
        "• Process 2.0 (Schema Optimization Engine): Employs heuristic rules and Gemini AI to suggest missing primary keys, foreign keys, and indexes.\n"
        "• Process 3.0 (Sandbox DB & Mock Seeding): Translates SQL dialect into SQLite, initializes sandbox files, and generates realistic records.\n"
        "• Process 4.0 (Query Advisory & Generation): Converts natural language prompts into optimized SQL statements.\n"
        "• Process 5.0 (Performance Benchmarker): Executes queries concurrently on original and optimized sandboxes to compute latency and speedup.\n"
        "• Data Stores: D1 (Schemas Store), D2 (Isolated Sandbox Databases), and D3 (Query History & Metrics)."
    )
    p1_desc.paragraph_format.line_spacing = 1.15

    # Insert Image 1
    doc.add_picture("diagrams/dfd_level_1.png", width=Inches(6.3))
    cap1 = doc.add_paragraph("Figure 2: DFD Level 1 – Decomposed Functional Process Flow")
    cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap1.runs[0].font.size = Pt(9.5)
    cap1.runs[0].font.italic = True
    cap1.paragraph_format.space_after = Pt(12)

    # 5.3 Level 2
    add_h2("5.3 DFD Level 2: Sandbox Creation & Performance Benchmarking")
    p2_desc = doc.add_paragraph(
        "The Level 2 DFD provides an in-depth view of the Sandbox Creation (Process 3.0) and Benchmarking (Process 5.0) pipeline. "
        "It details the dialect translation from PostgreSQL constructs (e.g. SERIAL, TIMESTAMPTZ) to SQLite, dynamic schema generation, "
        "table introspection via PRAGMA, realistic mock data synthesis, and side-by-side millisecond timing calculations."
    )
    p2_desc.paragraph_format.line_spacing = 1.15

    # Insert Image 2
    doc.add_picture("diagrams/dfd_level_2.png", width=Inches(6.2))
    cap2 = doc.add_paragraph("Figure 3: DFD Level 2 – Detailed Sub-Process Flow of Sandbox & Benchmark Engine")
    cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap2.runs[0].font.size = Pt(9.5)
    cap2.runs[0].font.italic = True
    cap2.paragraph_format.space_after = Pt(14)

    # Section 6: System Architecture & Technologies
    add_h1("6. System Architecture & Technologies")
    tech_table = doc.add_table(rows=6, cols=3)
    tech_headers = ["Layer", "Technology / Framework", "Specific Role in QKraft"]
    for j, h_text in enumerate(tech_headers):
        tech_table.rows[0].cells[j].paragraphs[0].text = h_text
    
    tech_rows = [
        ("Frontend Dashboard", "JavaScript (React 19 / Next.js)", "Dynamic client application, schema visualizer, and benchmarking modals"),
        ("Frontend Styling", "Vanilla CSS Modules", "Zero-runtime bespoke design system with dark mode and smooth animations"),
        ("Backend Web API", "Spring Boot 3 (Java 23, Spring Web)", "Enterprise-grade RESTful API endpoints for parsing, optimization, and testing"),
        ("ORM & Storage", "Spring Data JPA / Hibernate + SQLite", "Metadata database tracking saved schemas, query histories, and metrics"),
        ("AI Intelligence", "Google Gemini API (Generative AI)", "Context-aware schema auditing, query generation, and refactoring tips")
    ]
    for i, row_data in enumerate(tech_rows, start=1):
        row = tech_table.rows[i]
        for j, val in enumerate(row_data):
            row.cells[j].paragraphs[0].text = val
    style_table(tech_table, header_bg="1E3A8A", alt_bg="F8FAFC")

    # Section 7: Current Progress (Review 1 Status)
    add_h1("7. Current Progress & Completed Deliverables")
    p_status = doc.add_paragraph(
        "For Phase 1 (Project Review 1), all core foundational modules have been fully implemented and verified:"
    )
    p_status.paragraph_format.line_spacing = 1.15
    doc.add_paragraph("[COMPLETED] Full-Stack Scaffold: Spring Boot (Java 23) REST API backend paired with JavaScript React frontend with hot-reloading and robust CORS configuration.", style='List Bullet')
    doc.add_paragraph("[COMPLETED] SQL DDL Parser: Extracts table names, columns, data types, primary keys, and foreign keys even with syntax variations.", style='List Bullet')
    doc.add_paragraph("[COMPLETED] Interactive Schema Visualizer: Canvas/SVG representation of relational tables with foreign key link highlights.", style='List Bullet')
    doc.add_paragraph("[COMPLETED] Deterministic & AI Optimization: Detects missing B-Tree indexes on join and filter columns (e.g. status, created_at) and recommends corrected DDL.", style='List Bullet')
    doc.add_paragraph("[COMPLETED] Isolated Sandbox Generation: Automated creation of standalone sandbox_{id}.db instances with Postgres-to-SQLite type conversion.", style='List Bullet')
    doc.add_paragraph("[COMPLETED] Side-by-Side Benchmarking Modal: Executes queries concurrently on original and optimized sandboxes, displaying time in milliseconds, row counts, and speedup %.", style='List Bullet')
    doc.add_paragraph("[COMPLETED] Metrics & History Engine: Aggregates total time saved (ms), average percentage improvement, and session query histories.", style='List Bullet')

    # Section 8: Challenges Faced & Solutions
    add_h1("8. Challenges Encountered & Engineering Solutions")
    doc.add_paragraph("• SQL Dialect Differences: PostgreSQL features types like SERIAL, UUID, TIMESTAMPTZ, and JSONB that are unsupported in embedded SQLite sandboxes. Solution: Built an automated regex dialect translator in db_sandbox.py to seamlessly normalize and convert these constructs.", style='List Bullet')
    doc.add_paragraph("• Millisecond Timing Precision on Empty Tables: Running queries on empty tables yields near-zero execution times (0.01ms), hiding index benefits. Solution: Built an intelligent synthetic mock data generator that seeds realistic rows for users, orders, products, and generic tables automatically.", style='List Bullet')

    # Section 9: Phase 2 Plan (Target for Review 2)
    add_h1("9. Plan for Phase 2 (Review 2 & Final Review)")
    doc.add_paragraph("1. Visual Query Execution Plan (EXPLAIN): Render a graphical tree showing exact table scans vs. index lookups.", style='List Bullet')
    doc.add_paragraph("2. Multi-Engine Docker Runners: Add optional Docker containers for PostgreSQL and MySQL sandbox execution.", style='List Bullet')
    doc.add_paragraph("3. Migration Script Export: One-click export of Flyway/Liquibase-compatible SQL migration files containing only the delta changes.", style='List Bullet')
    doc.add_paragraph("4. Benchmarking on Standard Datasets: Test and document performance gains across standard enterprise schemas (TPC-H, Northwind).", style='List Bullet')

    # Save with fallback in case one file is currently open in Word
    out_path = "QKraft_Project_Review_1_Report.docx"
    try:
        doc.save(out_path)
        print(f"[OK] Successfully generated report: {out_path}")
    except PermissionError:
        out_path = "QKraft_Project_Review_1_Report_v2.docx"
        doc.save(out_path)
        print(f"[OK] Successfully generated report: {out_path}")

if __name__ == "__main__":
    import render_pro_dfds
    render_pro_dfds.gen0()
    render_pro_dfds.gen1()
    render_pro_dfds.gen2()
    build_docx_report()
