/**
 * QKraft Interactive SVG Entity-Relationship Diagram Renderer
 * Pure Vanilla JavaScript & SVG (Zero external library dependencies)
 */

class ERDiagramRenderer {
    constructor(svgElementId, emptyStateId) {
        this.svg = document.getElementById(svgElementId);
        this.emptyState = document.getElementById(emptyStateId);
        this.zoom = 1.0;
        this.panX = 40;
        this.panY = 40;
        this.isPanning = false;
        this.startX = 0;
        this.startY = 0;
        this.tables = [];
        this.relationships = [];
        this.tablePositions = new Map(); // tableName -> { x, y, width, height }

        this.initEvents();
    }

    initEvents() {
        if (!this.svg) return;

        this.svg.addEventListener('mousedown', (e) => {
            if (e.target === this.svg || e.target.tagName === 'svg' || e.target.id === 'erViewport') {
                this.isPanning = true;
                this.startX = e.clientX - this.panX;
                this.startY = e.clientY - this.panY;
            }
        });

        window.addEventListener('mousemove', (e) => {
            if (this.isPanning) {
                this.panX = e.clientX - this.startX;
                this.panY = e.clientY - this.startY;
                this.applyTransform();
            }
        });

        window.addEventListener('mouseup', () => {
            this.isPanning = false;
        });

        this.svg.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            this.zoom = Math.min(Math.max(0.4, this.zoom + delta), 2.5);
            this.applyTransform();
        });

        const btnZoomIn = document.getElementById('btnZoomIn');
        const btnZoomOut = document.getElementById('btnZoomOut');
        const btnResetZoom = document.getElementById('btnResetZoom');

        if (btnZoomIn) btnZoomIn.addEventListener('click', () => { this.zoom = Math.min(2.5, this.zoom + 0.15); this.applyTransform(); });
        if (btnZoomOut) btnZoomOut.addEventListener('click', () => { this.zoom = Math.max(0.4, this.zoom - 0.15); this.applyTransform(); });
        if (btnResetZoom) btnResetZoom.addEventListener('click', () => { this.zoom = 1.0; this.panX = 40; this.panY = 40; this.applyTransform(); });
    }

    applyTransform() {
        const viewport = document.getElementById('erViewport');
        if (viewport) {
            viewport.setAttribute('transform', `translate(${this.panX}, ${this.panY}) scale(${this.zoom})`);
        }
    }

    render(diagramData) {
        if (!diagramData || !diagramData.tables || diagramData.tables.length === 0) {
            this.svg.innerHTML = '';
            if (this.emptyState) this.emptyState.style.display = 'flex';
            const countInfo = document.getElementById('diagramTableCountInfo');
            if (countInfo) countInfo.textContent = '0 Tables | 0 Relationships';
            return;
        }

        if (this.emptyState) this.emptyState.style.display = 'none';

        this.tables = diagramData.tables;
        this.relationships = diagramData.relationships || [];
        this.tablePositions.clear();

        const countInfo = document.getElementById('diagramTableCountInfo');
        if (countInfo) {
            countInfo.textContent = `${this.tables.length} Tables | ${this.relationships.length} Relationships`;
        }

        // Layout algorithm: Calculate (x, y) coordinates for each table
        const tableWidth = 240;
        const colGap = 80;
        const rowGap = 60;
        const maxCols = Math.min(Math.max(2, Math.ceil(Math.sqrt(this.tables.length))), 4);

        let col = 0;
        let row = 0;
        const colHeights = new Array(maxCols).fill(0);

        this.tables.forEach((tbl) => {
            const rowCount = tbl.columns ? tbl.columns.length : 0;
            const tableHeight = 44 + (rowCount * 28) + 12;

            // Pick column with smallest height
            let bestCol = 0;
            for (let c = 1; c < maxCols; c++) {
                if (colHeights[c] < colHeights[bestCol]) bestCol = c;
            }

            const x = bestCol * (tableWidth + colGap);
            const y = colHeights[bestCol];
            colHeights[bestCol] += tableHeight + rowGap;

            this.tablePositions.set(tbl.name.toLowerCase(), {
                x, y, width: tableWidth, height: tableHeight, data: tbl
            });
        });

        // Generate SVG markup
        let svgContent = `<g id="erViewport" transform="translate(${this.panX}, ${this.panY}) scale(${this.zoom})">`;

        // SVG Defs (glow filters, arrowheads)
        svgContent += `
        <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#06B6D4" />
            </marker>
            <filter id="boxShadow" x="-10%" y="-10%" width="130%" height="130%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.5"/>
            </filter>
        </defs>`;

        // Render Relationships (curved connectors with glow)
        this.relationships.forEach((rel) => {
            const src = this.tablePositions.get((rel.sourceTable || '').toLowerCase());
            const tgt = this.tablePositions.get((rel.targetTable || '').toLowerCase());
            if (src && tgt) {
                const x1 = src.x + src.width;
                const y1 = src.y + 50;
                const x2 = tgt.x;
                const y2 = tgt.y + 50;
                const cx1 = x1 + 40;
                const cy1 = y1;
                const cx2 = x2 - 40;
                const cy2 = y2;

                svgContent += `
                <g class="er-relation-group">
                    <path d="M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}" 
                          fill="none" stroke="#06B6D4" stroke-width="2" stroke-dasharray="4 2" marker-end="url(#arrow)" opacity="0.85"/>
                    <circle cx="${x1}" cy="${y1}" r="4" fill="#06B6D4"/>
                </g>`;
            }
        });

        // Render Table Cards
        this.tablePositions.forEach((pos, tblName) => {
            const tbl = pos.data;
            const columns = tbl.columns || [];

            svgContent += `
            <g class="er-table-node" transform="translate(${pos.x}, ${pos.y})" filter="url(#boxShadow)">
                <!-- Table Background Card -->
                <rect width="${pos.width}" height="${pos.height}" rx="10" ry="10" 
                      fill="#182234" stroke="rgba(255, 255, 255, 0.12)" stroke-width="1.5"/>

                <!-- Header Bar -->
                <path d="M 0 10 Q 0 0 10 0 L ${pos.width - 10} 0 Q ${pos.width} 0 ${pos.width} 10 L ${pos.width} 40 L 0 40 Z" 
                      fill="#1E293B" stroke="none"/>
                <line x1="0" y1="40" x2="${pos.width}" y2="40" stroke="rgba(255, 255, 255, 0.1)" stroke-width="1"/>

                <!-- Table Header Icon & Title -->
                <rect x="12" y="12" width="16" height="16" rx="3" fill="#3B82F6" opacity="0.25"/>
                <text x="36" y="26" font-family="'Inter', sans-serif" font-size="13" font-weight="700" fill="#F8FAFC">
                    ${tbl.name}
                </text>
                <text x="${pos.width - 12}" y="25" text-anchor="end" font-family="'JetBrains Mono', monospace" font-size="10" fill="#64748B">
                    ${columns.length} cols
                </text>`;

            // Columns
            let rowY = 58;
            columns.forEach((col, idx) => {
                const isPk = col.isPk || col.pk;
                const isFk = col.isFk || col.fk;

                svgContent += `
                <g class="er-col-row" transform="translate(0, ${rowY - 14})">
                    <!-- Column Pill Indicator -->
                    ${isPk ? `<rect x="10" y="2" width="22" height="15" rx="3" fill="#F59E0B"/><text x="21" y="13" text-anchor="middle" font-family="'Inter', sans-serif" font-size="9" font-weight="800" fill="#000">PK</text>` : ''}
                    ${isFk ? `<rect x="10" y="2" width="22" height="15" rx="3" fill="#06B6D4"/><text x="21" y="13" text-anchor="middle" font-family="'Inter', sans-serif" font-size="9" font-weight="800" fill="#000">FK</text>` : ''}
                    ${!isPk && !isFk ? `<circle cx="18" cy="10" r="3" fill="#475569"/>` : ''}

                    <!-- Column Name -->
                    <text x="38" y="14" font-family="'JetBrains Mono', monospace" font-size="11.5" font-weight="${isPk ? '600' : '400'}" fill="${isPk ? '#FCD34D' : (isFk ? '#67E8F9' : '#CBD5E1')}">
                        ${col.name}
                    </text>

                    <!-- Column Data Type -->
                    <text x="${pos.width - 12}" y="14" text-anchor="end" font-family="'JetBrains Mono', monospace" font-size="10" fill="#64748B">
                        ${(col.type || 'text').toLowerCase()}
                    </text>
                </g>`;
                rowY += 28;
            });

            svgContent += `</g>`;
        });

        svgContent += `</g>`;
        this.svg.innerHTML = svgContent;
    }
}
