'use client';

import { useState, useEffect } from 'react';
import styles from './OldSchemaModal.module.css';

interface SchemaRecord {
    id: number;
    name: string;
    content: string;
    optimized_content?: string;
    diagram_data?: string;
    executed?: boolean;
    created_at: string;
}

interface OldSchemaModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSelectSchema: (schema: SchemaRecord) => void;
}

export default function OldSchemaModal({ isOpen, onClose, onSelectSchema }: OldSchemaModalProps) {
    const [schemas, setSchemas] = useState<SchemaRecord[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isOpen) {
            fetchSchemas();
        }
    }, [isOpen]);

    const fetchSchemas = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('/api/schemas');
            if (!res.ok) throw new Error('Failed to load schemas from database');
            const data = await res.json();
            setSchemas(data);
        } catch (err: any) {
            console.error(err);
            setError(err.message || 'Error loading saved schemas');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.modal} onClick={e => e.stopPropagation()}>
                <div className={styles.header}>
                    <h2>
                        Saved Database Schemas
                    </h2>
                    <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
                        &times;
                    </button>
                </div>

                <div className={styles.body}>
                    {loading && <p style={{ textAlign: 'center', color: '#94a3b8' }}>Loading schemas...</p>}
                    {error && <p style={{ color: '#ef4444' }}>{error}</p>}
                    
                    {!loading && schemas.length === 0 && (
                        <div className={styles.emptyState}>
                            <p>No previously saved schemas found in database.</p>
                            <p style={{ fontSize: '0.85rem', marginTop: '0.5rem', color: '#64748b' }}>
                                Use &ldquo;Create New Schema&rdquo; to define and execute your first schema!
                            </p>
                        </div>
                    )}

                    {!loading && schemas.length > 0 && (
                        <div className={styles.schemaList}>
                            {schemas.map(s => {
                                const dateFormatted = new Date(s.created_at).toLocaleDateString(undefined, {
                                    month: 'short',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                });
                                const previewSnippet = (s.optimized_content || s.content || '')
                                    .split('\n')
                                    .filter(l => l.trim().length > 0)
                                    .slice(0, 2)
                                    .join(' ');

                                return (
                                    <div key={s.id} className={styles.schemaItem}>
                                        <div className={styles.schemaInfo}>
                                            <div className={styles.schemaName}>
                                                {s.name || `Schema #${s.id}`}
                                            </div>
                                            <div className={styles.schemaMeta}>
                                                <span>ID: #{s.id}</span>
                                                <span>•</span>
                                                <span>Saved {dateFormatted}</span>
                                                {s.executed && (
                                                    <>
                                                        <span>•</span>
                                                        <span style={{ color: '#34d399' }}>DB Sandbox Ready</span>
                                                    </>
                                                )}
                                            </div>
                                            {previewSnippet && (
                                                <div className={styles.snippet}>
                                                    {previewSnippet}
                                                </div>
                                            )}
                                        </div>
                                        <button
                                            className={styles.selectBtn}
                                            onClick={() => {
                                                onSelectSchema(s);
                                                onClose();
                                            }}
                                        >
                                            Load Schema
                                        </button>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
