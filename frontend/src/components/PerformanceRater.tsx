'use client';

import { useState } from 'react';
import styles from './PerformanceRater.module.css';

export default function PerformanceRater({ schemaContent }: { schemaContent: string }) {
    const [recommendations, setRecommendations] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [analyzed, setAnalyzed] = useState(false);

    const handleAnalyze = async () => {
        if (!schemaContent) return;
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/schema/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ schema_content: schemaContent })
            });
            const data = await res.json();
            setRecommendations(data.recommendations || []);
            setAnalyzed(true);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h2>Performance Rater</h2>
                <button className={styles.button} onClick={handleAnalyze} disabled={!schemaContent || loading}>
                    {loading ? 'Scanning...' : 'Scan Schema'}
                </button>
            </div>
            
            {analyzed && (
                <div className={styles.results}>
                    {recommendations.length > 0 ? (
                        <ul className={styles.list}>
                            {recommendations.map((rec, i) => (
                                <li key={i} className={styles.listItem}>⚠️ {rec}</li>
                            ))}
                        </ul>
                    ) : (
                        <p className={styles.perfect}>✅ No issues found! Your schema looks optimal.</p>
                    )}
                </div>
            )}
        </div>
    );
}
