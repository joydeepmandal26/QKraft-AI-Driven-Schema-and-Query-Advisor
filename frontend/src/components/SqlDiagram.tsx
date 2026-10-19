'use client';

import styles from './SqlDiagram.module.css';

export interface ColumnInfo {
    name: string;
    type: string;
    is_pk?: boolean;
    is_fk?: boolean;
    references?: string | null;
    is_indexed?: boolean;
}

export interface TableInfo {
    name: string;
    columns: ColumnInfo[];
    row_count?: number;
}

export interface RelationInfo {
    from_table: string;
    from_column: string;
    to_table: string;
    to_column: string;
}

export interface DiagramData {
    tables: TableInfo[];
    relations: RelationInfo[];
}

interface SqlDiagramProps {
    diagram: DiagramData;
}

export default function SqlDiagram({ diagram }: SqlDiagramProps) {
    if (!diagram || !diagram.tables || diagram.tables.length === 0) {
        return null;
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.titleGroup}>
                    <span>📊</span>
                    <h3>SQL Relational Diagram</h3>
                    <span className={styles.badge}>{diagram.tables.length} Tables</span>
                </div>
                <div className={styles.legend}>
                    <div className={styles.legendItem}>
                        <span className={styles.badgePk}>PK</span>
                        <span>Primary Key</span>
                    </div>
                    <div className={styles.legendItem}>
                        <span className={styles.badgeFk}>FK</span>
                        <span>Foreign Key</span>
                    </div>
                    <div className={styles.legendItem}>
                        <span className={styles.badgeIdx}>IDX</span>
                        <span>Indexed</span>
                    </div>
                </div>
            </div>

            <div className={styles.diagramCanvas}>
                {diagram.tables.map((table, tIdx) => (
                    <div key={`${table.name}-${tIdx}`} className={styles.tableCard}>
                        <div className={styles.tableHeader}>
                            <div className={styles.tableName}>
                                <span>📋</span> {table.name}
                            </div>
                            <span className={styles.rowCount}>
                                {table.row_count !== undefined ? `${table.row_count} rows` : 'DB ready'}
                            </span>
                        </div>
                        <div className={styles.columnList}>
                            {table.columns.map((col, cIdx) => (
                                <div key={`${table.name}-${col.name}-${cIdx}`} className={styles.columnRow}>
                                    <div className={styles.columnLeft}>
                                        {col.is_pk && <span className={styles.badgePk} title="Primary Key constraint">PK</span>}
                                        {col.is_fk && (
                                            <span 
                                                className={styles.badgeFk} 
                                                title={col.references ? `Foreign Key referencing ${col.references}` : 'Foreign Key constraint'}
                                            >
                                                FK
                                            </span>
                                        )}
                                        {col.is_indexed && (!col.is_pk || col.is_fk) && (
                                            <span 
                                                className={styles.badgeIdx} 
                                                title="B-Tree Index enabled for accelerated query joins & filters"
                                            >
                                                IDX
                                            </span>
                                        )}
                                        <span className={styles.columnName}>{col.name}</span>
                                    </div>
                                    <div className={styles.columnRight}>
                                        <span className={styles.columnType}>{col.type}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {diagram.relations && diagram.relations.length > 0 && (
                <div className={styles.relationsBox}>
                    <div className={styles.relationsTitle}>
                        🔗 Foreign Key Relationships & Join Paths
                    </div>
                    <div className={styles.relationPillList}>
                        {diagram.relations.map((rel, idx) => (
                            <div key={idx} className={styles.relationPill}>
                                <span>{rel.from_table}.{rel.from_column}</span>
                                <span className={styles.relationArrow}>&rarr;</span>
                                <span>{rel.to_table}.{rel.to_column}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
