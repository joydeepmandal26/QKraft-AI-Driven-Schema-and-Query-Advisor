'use client';

import { useState, useEffect } from 'react';
import styles from './SchemaVisualizer.module.css';

interface SchemaVisualizerProps {
    onSchemaSubmit: (schema: string, name: string) => void;
    currentSchema?: string;
    currentSchemaName?: string;
    loading?: boolean;
}

export default function SchemaVisualizer({
    onSchemaSubmit,
    currentSchema = '',
    currentSchemaName = '',
    loading
}: SchemaVisualizerProps) {
    const [schema, setSchema] = useState(currentSchema);
    const [name, setName] = useState(currentSchemaName);

    useEffect(() => {
        setSchema(currentSchema);
    }, [currentSchema]);

    useEffect(() => {
        setName(currentSchemaName);
    }, [currentSchemaName]);

    const handleSubmit = () => {
        if (!schema.trim()) {
            alert('Please paste or write your SQL DDL schema first.');
            return;
        }
        const trimmedName = name.trim() || 'Custom Schema';
        onSchemaSubmit(schema, trimmedName);
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.titleGroup}>
                    <h2>Schema Input</h2>
                    <span className={styles.badge}>DDL Parser</span>
                </div>
            </div>

            {/* User-defined Schema Name input */}
            <div className={styles.nameInputGroup}>
                <label className={styles.nameLabel}>
                    <span>🏷️</span> Schema Name:
                </label>
                <input
                    type="text"
                    className={styles.nameInput}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter a name for this schema (e.g. Billing Core, User Profiles, Analytics)..."
                />
            </div>

            <textarea 
                className={styles.textarea}
                value={schema}
                onChange={(e) => setSchema(e.target.value)}
                placeholder="Paste your PostgreSQL / ANSI DDL schema here...
Example:
CREATE TABLE users (
    id SERIAL,
    email VARCHAR(255),
    created_at TIMESTAMP
);"
                rows={11}
            />

            <div className={styles.actions}>
                <span className={styles.hint}>
                    ⚡ Submitting automatically generates the optimized schema directly.
                </span>
                <button 
                    className={styles.button} 
                    onClick={handleSubmit}
                    disabled={!schema.trim() || loading}
                >
                    {loading ? 'Optimizing...' : '🚀 Parse & Auto-Optimize'}
                </button>
            </div>
        </div>
    );
}
