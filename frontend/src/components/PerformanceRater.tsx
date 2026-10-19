'use client';

import { useState, useEffect, useCallback } from 'react';
import styles from './PerformanceRater.module.css';
import { safeFetchJson } from '@/lib/api';

export default function PerformanceRater({ schemaContent }: { schemaContent: string }) {
    const [recommendations, setRecommendations] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [analyzed, setAnalyzed] = useState(false);
    const [score, setScore] = useState<number>(100);
    const [isOptimal, setIsOptimal] = useState<boolean>(false);

    const handleAnalyze = useCallback(async () => {
        if (!schemaContent || !schemaContent.trim()) {
            setAnalyzed(false);
            setRecommendations([]);
            return;
        }
        setLoading(true);
        try {
            const data = await safeFetchJson('/api/schema/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ schema_content: schemaContent })
            });
            const recs = data.recommendations || [];
            setRecommendations(recs);
            setScore(data.score !== undefined ? data.score : (recs.length === 0 ? 100 : Math.max(100 - recs.length * 18, 20)));
            setIsOptimal(data.is_optimal !== undefined ? data.is_optimal : (recs.length === 0));
            setAnalyzed(true);
        } catch (error: any) {
            console.error('Analyze error:', error);
            setRecommendations([`Error: ${error.message}`]);
            setScore(50);
            setIsOptimal(false);
            setAnalyzed(true);
        } finally {
            setLoading(false);
        }
    }, [schemaContent]);

    // Automatically analyze whenever active schema changes
    useEffect(() => {
        if (schemaContent && schemaContent.trim()) {
            handleAnalyze();
        } else {
            setAnalyzed(false);
            setRecommendations([]);
            setIsOptimal(false);
        }
    }, [schemaContent, handleAnalyze]);

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.titleGroup}>
                    <h2>Performance Rater</h2>
                    {analyzed && (
                        isOptimal || recommendations.length === 0 ? (
                            <span className={styles.scoreBadgeOptimal}>
                                🏆 100/100 Optimal
                            </span>
                        ) : (
                            <span className={styles.scoreBadgeWarning}>
                                ⚠️ {score}/100 Bottlenecks
                            </span>
                        )
                    )}
                </div>
                <button 
                    type="button"
                    className={styles.button} 
                    onClick={handleAnalyze} 
                    disabled={!schemaContent || loading}
                >
                    {loading ? 'Scanning...' : 'Re-Scan'}
                </button>
            </div>
            
            {analyzed && (
                <div className={styles.results}>
                    {recommendations.length > 0 ? (
                        <ul className={styles.list}>
                            {recommendations.map((rec, i) => (
                                <li key={i} className={styles.listItem}>
                                    <span className={styles.itemIcon}>⚠️</span>
                                    <span className={styles.itemText}>{rec}</span>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <div className={styles.perfectCard}>
                            <div className={styles.perfectHeader}>
                                <span>✅</span>
                                <span>Schema is Fully Optimized!</span>
                            </div>
                            <p className={styles.perfectDesc}>
                                Zero query bottlenecks detected. All tables have explicit primary keys, foreign keys for join ordering, and strategic B-Tree performance indexes.
                            </p>
                            <div className={styles.featureChecks}>
                                <span className={styles.checkBadge}>✓ Clustered Primary Keys</span>
                                <span className={styles.checkBadge}>✓ B-Tree Filter Indexes</span>
                                <span className={styles.checkBadge}>✓ Foreign Key Joins</span>
                                <span className={styles.checkBadge}>✓ Zero Full Table Scans</span>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
