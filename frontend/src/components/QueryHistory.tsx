'use client';

import { useEffect, useState } from 'react';
import styles from './QueryHistory.module.css';

export interface QueryHistoryItem {
    id: number;
    schema_id: number;
    user_prompt: string;
    optimized_sql: string;
    unoptimized_sql?: string;
    optimized_time_ms: number;
    unoptimized_time_ms: number;
    time_saved_ms: number;
    time_saved_pct: number;
    status: string;
    created_at: string;
}

interface QueryHistoryProps {
    schemaId: number | null;
    refreshTrigger: number;
}

export default function QueryHistory({ schemaId, refreshTrigger }: QueryHistoryProps) {
    const [history, setHistory] = useState<QueryHistoryItem[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!schemaId) {
            setHistory([]);
            return;
        }

        const fetchHistory = async () => {
            setLoading(true);
            try {
                const res = await fetch(`/api/schema/${schemaId}/history`);
                if (res.ok) {
                    const data = await res.json();
                    setHistory(data);
                }
            } catch (err) {
                console.error('Failed to load schema query history', err);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [schemaId, refreshTrigger]);

    if (!schemaId) return null;

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.titleGroup}>
                    <span>📜</span>
                    <h2>Schema Query History</h2>
                    <span className={styles.badge}>Schema #{schemaId}</span>
                </div>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                    {history.length} {history.length === 1 ? 'record' : 'records'}
                </span>
            </div>

            {loading && <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Refreshing history...</p>}

            {!loading && history.length === 0 && (
                <div className={styles.emptyState}>
                    <p>No queries executed on this schema yet.</p>
                    <p style={{ marginTop: '0.35rem', color: '#64748b' }}>
                        Run an optimized query in Query Advisor to see execution statistics recorded here.
                    </p>
                </div>
            )}

            {!loading && history.length > 0 && (
                <div className={styles.historyList}>
                    {history.map(item => {
                        const dateFormatted = new Date(item.created_at).toLocaleTimeString(undefined, {
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        });

                        return (
                            <div key={item.id} className={styles.historyItem}>
                                <div className={styles.itemTop}>
                                    <span className={styles.userPrompt}>{item.user_prompt}</span>
                                    <span className={styles.timestamp}>{dateFormatted}</span>
                                </div>
                                <div className={styles.sqlSnippet}>
                                    {item.optimized_sql}
                                </div>
                                <div className={styles.itemBottom}>
                                    <div className={styles.metricPills}>
                                        <span className={styles.timePill}>
                                            ⚡ {item.time_saved_ms} ms Saved (+{item.time_saved_pct}%)
                                        </span>
                                        <span style={{ fontSize: '0.72rem', color: '#94a3b8', alignSelf: 'center' }}>
                                            Opt: {item.optimized_time_ms} ms vs Unopt: {item.unoptimized_time_ms} ms
                                        </span>
                                    </div>
                                    <span style={{ fontSize: '0.75rem', color: item.status === 'SUCCESS' ? '#34d399' : '#ef4444' }}>
                                        {item.status === 'SUCCESS' ? '✓ Passed' : '✗ Failed'}
                                    </span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
