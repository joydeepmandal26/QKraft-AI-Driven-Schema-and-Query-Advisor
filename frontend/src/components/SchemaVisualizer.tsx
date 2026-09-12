'use client';

import { useState } from 'react';
import styles from './SchemaVisualizer.module.css';

export default function SchemaVisualizer({ onSchemaSubmit }: { onSchemaSubmit: (schema: string) => void }) {
    const [schema, setSchema] = useState('');

    const handleSubmit = () => {
        onSchemaSubmit(schema);
    };

    return (
        <div className={styles.container}>
            <h2>Schema Visualizer</h2>
            <textarea 
                className={styles.textarea}
                value={schema}
                onChange={(e) => setSchema(e.target.value)}
                placeholder="Paste your PostgreSQL DDL schema here..."
                rows={10}
            />
            <button className={styles.button} onClick={handleSubmit}>Parse & Analyze</button>
        </div>
    );
}
