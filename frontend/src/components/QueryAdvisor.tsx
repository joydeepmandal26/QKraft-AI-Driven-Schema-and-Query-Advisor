'use client';

import { useState, useMemo, useRef } from 'react';
import styles from './QueryAdvisor.module.css';
import { safeFetchJson } from '@/lib/api';

interface ExecutionStep {
    step_number: number;
    name: string;
    node_type: string;
    duration_ms: number;
    description: string;
    status: string;
}

interface QueryExecutionResult {
    columns: string[];
    rows: any[][];
    row_count: number;
    optimized_time_ms: number;
    unoptimized_time_ms: number;
    time_saved_ms: number;
    time_saved_pct: number;
    scan_type: string;
    execution_pipeline: ExecutionStep[];
    explain_plan: string[];
}

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    text?: string;
    optimized_sql?: string;
    unoptimized_sql?: string;
    explanation?: string;
    details?: {
        techniques_used: string[];
        index_utilization: string[];
        estimated_speedup: string;
        rationale: string;
    };
    executionResult?: QueryExecutionResult;
    isExecuting?: boolean;
    error?: string;
    executionError?: string;
}

interface QueryAdvisorProps {
    schemaContent: string;
    optimizedSchema: string;
    schemaId: number | null;
    onQueryExecuted: (res: QueryExecutionResult) => void;
}

interface ParsedTable {
    name: string;
    columns: string[];
}

function extractSchemaTables(ddl: string): ParsedTable[] {
    if (!ddl) return [];
    const tables: ParsedTable[] = [];
    const tableRegex = /CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)\s*\(([\s\S]*?)\)(?:;|$)/gi;
    let match;
    while ((match = tableRegex.exec(ddl)) !== null) {
        const tblName = match[1].trim();
        const body = match[2];
        const cols: string[] = [];
        body.split(',').forEach(part => {
            const trimmed = part.trim();
            if (trimmed &&
                !trimmed.toUpperCase().startsWith('PRIMARY') &&
                !trimmed.toUpperCase().startsWith('FOREIGN') &&
                !trimmed.toUpperCase().startsWith('CONSTRAINT') &&
                !trimmed.toUpperCase().startsWith('KEY') &&
                !trimmed.toUpperCase().startsWith('CHECK')) {
                const colName = trimmed.split(/\s+/)[0]?.trim();
                if (colName && !colName.includes('(') && !colName.includes(')')) {
                    cols.push(colName);
                }
            }
        });
        tables.push({ name: tblName, columns: cols });
    }
    return tables;
}

export default function QueryAdvisor({
    schemaContent,
    optimizedSchema,
    schemaId,
    onQueryExecuted
}: QueryAdvisorProps) {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [loading, setLoading] = useState(false);
    const [copiedId, setCopiedId] = useState<string | null>(null);
    const chatWindowRef = useRef<HTMLDivElement>(null);

    const activeTables = useMemo(() => {
        return extractSchemaTables(optimizedSchema || schemaContent);
    }, [optimizedSchema, schemaContent]);

    const primaryTable = activeTables.length > 0 ? activeTables[0].name : '';
    const primaryCols = activeTables.length > 0 ? activeTables[0].columns : [];

    const dynamicQuickPrompts = useMemo(() => {
        if (activeTables.length === 0) {
            return [
                'Enter schema DDL above first',
                'SELECT * FROM your_table LIMIT 10',
                'Filter records by index condition'
            ];
        }
        const t0 = activeTables[0];
        const searchCol = t0.columns.find(c => /address|city|location/i.test(c)) ||
                          t0.columns.find(c => /name|title|emp|student/i.test(c)) ||
                          (t0.columns.length > 1 ? t0.columns[1] : t0.columns[0]);
        const pkCol = t0.columns[0] || 'id';

        const prompts = [
            `SELECT * FROM ${t0.name} LIMIT 10`
        ];

        if (searchCol && searchCol !== pkCol) {
            prompts.push(`Filter ${t0.name} WHERE ${searchCol} ILIKE '%Mumbai%'`);
        } else {
            prompts.push(`SELECT ${t0.columns.slice(0, 3).join(', ')} FROM ${t0.name}`);
        }

        if (activeTables.length > 1) {
            prompts.push(`Join ${activeTables[0].name} with ${activeTables[1].name}`);
        } else {
            prompts.push(`Sort ${t0.name} by ${pkCol} DESC`);
        }

        return prompts;
    }, [activeTables]);

    const handleSend = async (promptToSend?: string) => {
        const textQuery = promptToSend || query;
        if (!textQuery.trim()) return;

        const userMsgId = 'user_' + Date.now();
        const assistantMsgId = 'asst_' + Date.now();

        setMessages(prev => [...prev, { id: userMsgId, role: 'user', text: textQuery }]);
        if (!promptToSend) setQuery('');
        setLoading(true);

        try {
            const data = await safeFetchJson('/api/advisor/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: textQuery,
                    schema_content: schemaContent,
                    optimized_schema: optimizedSchema || schemaContent,
                    schema_id: schemaId
                })
            });

            setMessages(prev => [
                ...prev,
                {
                    id: assistantMsgId,
                    role: 'assistant',
                    optimized_sql: data.optimized_sql,
                    unoptimized_sql: data.unoptimized_sql,
                    explanation: data.explanation,
                    details: data.details
                }
            ]);

            setTimeout(() => {
                if (chatWindowRef.current) {
                    chatWindowRef.current.scrollTo({
                        top: chatWindowRef.current.scrollHeight,
                        behavior: 'smooth'
                    });
                }
            }, 100);
        } catch (error: any) {
            console.error(error);
            setMessages(prev => [
                ...prev,
                {
                    id: assistantMsgId,
                    role: 'assistant',
                    error: error.message || 'Failed to optimize query.'
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleExecuteQuery = async (msgIndex: number, sql: string, unoptSql?: string) => {
        setMessages(prev => prev.map((m, idx) => idx === msgIndex ? { ...m, isExecuting: true, executionError: undefined } : m));

        try {
            const data = await safeFetchJson('/api/query/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    schema_id: schemaId || 1,
                    sql_query: sql,
                    unoptimized_sql: unoptSql,
                    user_prompt: query || 'Optimized Schema Query',
                    schema_content: schemaContent,
                    optimized_schema: optimizedSchema || schemaContent
                })
            });

            if (data.status === 'error') {
                throw new Error(data.error || data.detail || 'Execution failed in DB sandbox');
            }

            const execResult: QueryExecutionResult = {
                columns: data.columns || [],
                rows: data.rows || [],
                row_count: data.row_count || 0,
                optimized_time_ms: data.optimized_time_ms,
                unoptimized_time_ms: data.unoptimized_time_ms,
                time_saved_ms: data.time_saved_ms,
                time_saved_pct: data.time_saved_pct,
                scan_type: data.scan_type,
                execution_pipeline: data.execution_pipeline || [],
                explain_plan: data.explain_plan || []
            };

            setMessages(prev => prev.map((m, idx) => idx === msgIndex ? { ...m, executionResult: execResult, isExecuting: false, executionError: undefined } : m));
            onQueryExecuted(execResult);

            setTimeout(() => {
                if (chatWindowRef.current) {
                    chatWindowRef.current.scrollTo({
                        top: chatWindowRef.current.scrollHeight,
                        behavior: 'smooth'
                    });
                }
            }, 150);
        } catch (err: any) {
            console.error(err);
            setMessages(prev => prev.map((m, idx) => idx === msgIndex ? { ...m, isExecuting: false, executionError: err.message } : m));
        }
    };

    const handleCopy = (id: string, text: string) => {
        navigator.clipboard.writeText(text);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    return (
        <div className={styles.container} id="query-advisor-section">
            <div className={styles.header}>
                <div className={styles.titleGroup}>
                    <h2>Query Optimizer &amp; Execution</h2>
                    <span className={styles.badge}>Schema-Aware</span>
                </div>
                {messages.length > 0 && (
                    <button
                        type="button"
                        className={styles.clearHeaderBtn}
                        onClick={() => {
                            setMessages([]);
                            setQuery('');
                        }}
                        title="Clear conversation history"
                    >
                        Clear Chat
                    </button>
                )}
            </div>

            <div className={styles.quickPrompts}>
                {dynamicQuickPrompts.map((p, i) => (
                    <button
                        key={i}
                        type="button"
                        className={styles.chip}
                        onClick={() => handleSend(p)}
                        disabled={loading || (!schemaContent && !optimizedSchema)}
                    >
                        {p}
                    </button>
                ))}
            </div>

            <div className={styles.chatWindow} ref={chatWindowRef}>
                {messages.length === 0 && (
                    <div className={styles.placeholder}>
                        <p>Ask for any query or analysis. Every query is directly optimized against the active schema&apos;s indexes, constraints, and joins.</p>
                    </div>
                )}

                {messages.map((m, i) => {
                    if (m.role === 'user') {
                        return (
                            <div key={m.id} className={styles.userMsg}>
                                <p>{m.text}</p>
                            </div>
                        );
                    }

                    if (m.error) {
                        return (
                            <div key={m.id} className={styles.assistantCard} style={{ borderColor: '#ef4444' }}>
                                <p style={{ color: '#fca5a5' }}>{m.error}</p>
                            </div>
                        );
                    }

                    const exec = m.executionResult;

                    return (
                        <div key={m.id} className={styles.assistantCard}>
                            <div className={styles.cardHeader}>
                                <span style={{ fontWeight: 600, color: '#38bdf8', fontSize: '0.9rem' }}>
                                    Schema-Optimized Query
                                </span>
                                {m.details?.estimated_speedup && (
                                    <span style={{ fontSize: '0.75rem', color: '#34d399', fontWeight: 700 }}>
                                        Est. {m.details.estimated_speedup}
                                    </span>
                                )}
                            </div>

                            {m.explanation && <p className={styles.explanation}>{m.explanation}</p>}

                            {m.details?.techniques_used && (
                                <div className={styles.techPills}>
                                    {m.details.techniques_used.map((tech, idx) => (
                                        <span key={idx} className={styles.techPill}>{tech}</span>
                                    ))}
                                </div>
                            )}

                            {m.optimized_sql && (
                                <div className={styles.sqlBox}>
                                    <div className={styles.sqlHeader}>
                                        <span>SQL Query (Index-Aware)</span>
                                        <span>Target Schema</span>
                                    </div>
                                    <pre className={styles.sqlCode}>
                                        <code>{m.optimized_sql}</code>
                                    </pre>
                                </div>
                            )}

                            <div className={styles.cardActions}>
                                <button
                                    type="button"
                                    className={styles.executeBtn}
                                    onClick={() => handleExecuteQuery(i, m.optimized_sql || '', m.unoptimized_sql)}
                                    disabled={m.isExecuting}
                                >
                                    {m.isExecuting ? 'Running on DB...' : 'Execute Query'}
                                </button>
                                {m.optimized_sql && (
                                    <button
                                        type="button"
                                        className={styles.copyBtn}
                                        onClick={() => handleCopy(m.id, m.optimized_sql || '')}
                                    >
                                        {copiedId === m.id ? 'Copied' : 'Copy SQL'}
                                    </button>
                                )}
                            </div>

                            {m.executionError && (
                                <div style={{
                                    padding: '0.65rem 0.95rem',
                                    backgroundColor: 'rgba(239, 68, 68, 0.12)',
                                    border: '1px solid rgba(239, 68, 68, 0.35)',
                                    borderRadius: '6px',
                                    color: '#fca5a5',
                                    fontSize: '0.82rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                    marginTop: '0.4rem'
                                }}>
                                    <span>{m.executionError}</span>
                                </div>
                            )}

                            {/* Visually Represent Query Execution */}
                            {exec && (
                                <>
                                    <div className={styles.executionPipeline}>
                                        <div className={styles.pipelineTitle}>
                                            <span>Visual Query Execution Pipeline</span>
                                            <span style={{ color: '#34d399', fontSize: '0.75rem' }}>
                                                {exec.scan_type}
                                            </span>
                                        </div>
                                        <div className={styles.pipelineNodes}>
                                            {exec.execution_pipeline.map((step, sIdx) => (
                                                <div key={sIdx} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                    <div className={styles.nodeCard}>
                                                        <span className={styles.nodeType}>{step.node_type}</span>
                                                        <span className={styles.nodeName}>{step.name}</span>
                                                        <span className={styles.nodeDuration}>{step.duration_ms} ms</span>
                                                    </div>
                                                    {sIdx < exec.execution_pipeline.length - 1 && (
                                                        <span className={styles.nodeArrow}>&rarr;</span>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Performance Increase Metric (Time Saved) */}
                                    <div className={styles.perfComparisonCard}>
                                        <div className={styles.perfHeader}>
                                            <div className={styles.perfTitle}>
                                                Performance Comparison
                                            </div>
                                            <div className={styles.timeSavedHighlight}>
                                                {exec.time_saved_ms} ms Saved (+{exec.time_saved_pct}% Faster)
                                            </div>
                                        </div>

                                        <div className={styles.barRow}>
                                            <div className={styles.barMeta}>
                                                <span>Unoptimized Schema (Full Table Scan)</span>
                                                <span style={{ color: '#ef4444' }}>{exec.unoptimized_time_ms} ms</span>
                                            </div>
                                            <div className={styles.barTrack}>
                                                <div className={styles.barFillUnopt} style={{ width: '100%' }}></div>
                                            </div>
                                        </div>

                                        <div className={styles.barRow}>
                                            <div className={styles.barMeta}>
                                                <span>Optimized Schema ({exec.scan_type})</span>
                                                <span style={{ color: '#34d399', fontWeight: 700 }}>{exec.optimized_time_ms} ms</span>
                                            </div>
                                            <div className={styles.barTrack}>
                                                <div
                                                    className={styles.barFillOpt}
                                                    style={{
                                                        width: `${Math.max(Math.min((exec.optimized_time_ms / exec.unoptimized_time_ms) * 100, 100), 5)}%`
                                                    }}
                                                ></div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* DB Result Set Table with Indian Dummy Records */}
                                    <div className={styles.resultsTableBox}>
                                        <div className={styles.tableHeaderBar}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                                                <span style={{ fontWeight: 600, color: '#e2e8f0' }}>Live Database Records</span>
                                                <span style={{
                                                    fontSize: '0.7rem',
                                                    padding: '0.15rem 0.5rem',
                                                    borderRadius: '4px',
                                                    background: 'rgba(16, 185, 129, 0.15)',
                                                    color: '#34d399',
                                                    border: '1px solid rgba(16, 185, 129, 0.3)',
                                                    fontWeight: 600
                                                }}>
                                                    Indian Dummy Dataset Loaded
                                                </span>
                                            </div>
                                            <span style={{ color: '#94a3b8', fontSize: '0.75rem', fontFamily: 'monospace' }}>
                                                {exec.row_count} records returned
                                            </span>
                                        </div>
                                        <div className={styles.tableWrapper}>
                                            {exec.rows.length === 0 ? (
                                                <p style={{ padding: '0.85rem 1rem', color: '#94a3b8', margin: 0, fontSize: '0.82rem' }}>
                                                    Query executed successfully. 0 rows returned.
                                                </p>
                                            ) : (
                                                <table className={styles.dataTable}>
                                                    <thead>
                                                        <tr>
                                                            {exec.columns.map((col, cIdx) => (
                                                                <th key={cIdx}>{col}</th>
                                                            ))}
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {exec.rows.map((row, rIdx) => (
                                                            <tr key={rIdx}>
                                                                {row.map((val, cellIdx) => (
                                                                    <td key={cellIdx} style={cellIdx === 0 ? { color: '#38bdf8', fontWeight: 600 } : {}}>
                                                                        {val === null || val === undefined ? 'NULL' : String(val)}
                                                                    </td>
                                                                ))}
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                            )}
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                    );
                })}

                {loading && (
                    <div className={styles.assistantCard}>
                        <p style={{ color: '#a78bfa', margin: 0 }}>Optimizing query based on active schema indexes...</p>
                    </div>
                )}
            </div>

            <div className={styles.inputArea}>
                <input 
                    type="text" 
                    className={styles.input}
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSend()}
                    placeholder={primaryTable ? `eg: SELECT * FROM ${primaryTable};` : "eg: SELECT * FROM your_schema_table;"}
                    disabled={(!schemaContent && !optimizedSchema) || loading}
                />
                {(messages.length > 0 || query.trim().length > 0) && (
                    <button 
                        type="button"
                        className={styles.clearActionBtn}
                        onClick={() => {
                            setMessages([]);
                            setQuery('');
                        }}
                        title="Clear conversation and input"
                    >
                        Clear
                    </button>
                )}
                <button 
                    className={styles.sendBtn} 
                    onClick={() => handleSend()} 
                    disabled={(!schemaContent && !optimizedSchema) || loading || !query.trim()}
                >
                    Optimize &amp; Suggest
                </button>
            </div>
        </div>
    );
}
