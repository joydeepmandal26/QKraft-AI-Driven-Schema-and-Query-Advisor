'use client';

import { useState } from 'react';
import styles from './RecommendedSchema.module.css';
import SqlDiagram, { DiagramData } from './SqlDiagram';
import { safeFetchJson } from '@/lib/api';

interface RecommendedSchemaProps {
    schemaContent: string;
    recommendedSchema: string;
    schemaName?: string;
    schemaId: number | null;
    isOptimizing: boolean;
    diagramData: DiagramData | null;
    isExecuted: boolean;
    isAlreadyOptimized?: boolean;
    testScore?: number;
    onSchemaExecuted: (schemaId: number, diagram: DiagramData, message: string) => void;
}

export default function RecommendedSchema({
    schemaContent,
    recommendedSchema,
    schemaName,
    schemaId,
    isOptimizing,
    diagramData,
    isExecuted,
    isAlreadyOptimized = false,
    testScore = 100,
    onSchemaExecuted
}: RecommendedSchemaProps) {
    const [executing, setExecuting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [copied, setCopied] = useState(false);
    const [executionMsg, setExecutionMsg] = useState<string | null>(null);

    const handleExecuteSchema = async () => {
        if (!recommendedSchema && !schemaContent) return;
        setExecuting(true);
        setError(null);
        setExecutionMsg(null);

        try {
            const ddlToExecute = recommendedSchema || schemaContent;
            const data = await safeFetchJson('/api/schema/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    schema_id: schemaId,
                    schema_content: ddlToExecute,
                    schema_name: schemaName || 'Custom Schema'
                })
            });

            setExecutionMsg(data.message || 'Schema successfully executed into DB sandbox.');
            onSchemaExecuted(data.schema_id, data.diagram, data.message);
        } catch (err: any) {
            console.error(err);
            setError(err.message || 'Error executing schema.');
        } finally {
            setExecuting(false);
        }
    };

    const handleCopy = () => {
        if (!recommendedSchema) return;
        navigator.clipboard.writeText(recommendedSchema);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const scrollToQueryAdvisor = () => {
        const el = document.getElementById('query-advisor-section');
        if (el) {
            el.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.titleGroup}>
                    <h2>Recommended Schema</h2>
                    {isAlreadyOptimized ? (
                        <span className={styles.badge} style={{ background: 'rgba(16, 185, 129, 0.18)', borderColor: 'rgba(16, 185, 129, 0.4)', color: '#34d399' }}>
                            100/100 Optimal
                        </span>
                    ) : (
                        <span className={styles.badge}>
                            Score: {testScore}/100 • Auto-Optimized
                        </span>
                    )}
                </div>
                <div className={styles.actions}>
                    {recommendedSchema && (
                        <button 
                            type="button" 
                            className={styles.copyBtn} 
                            onClick={handleCopy}
                            title="Copy SQL to clipboard"
                        >
                            {copied ? 'Copied!' : 'Copy SQL'}
                        </button>
                    )}
                    <button 
                        type="button" 
                        className={styles.executeBtn} 
                        onClick={handleExecuteSchema} 
                        disabled={(!recommendedSchema && !schemaContent) || executing || isOptimizing}
                    >
                        {executing ? 'Executing on DB...' : (isExecuted ? 'Re-Execute Schema' : 'Execute Schema')}
                    </button>
                </div>
            </div>

            {isAlreadyOptimized && (
                <div className={styles.optimalBanner}>
                    <div className={styles.optimalBannerHeader}>
                        <span>Schema is Already Fully Optimized (Score: 100/100)</span>
                    </div>
                    <p>
                        Your input schema already has all necessary Primary Keys, Foreign Key relationships, and B-Tree Indexes in place. No structural schema rewrites are needed.
                    </p>
                    <div style={{ marginTop: '0.65rem', display: 'flex', gap: '0.6rem', alignItems: 'center', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 600 }}>
                            Production-Ready: Tables and mock data are active in the database sandbox.
                        </span>
                        <button
                            type="button"
                            onClick={scrollToQueryAdvisor}
                            style={{
                                background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
                                border: 'none',
                                color: '#ffffff',
                                borderRadius: '4px',
                                padding: '0.3rem 0.75rem',
                                fontSize: '0.78rem',
                                fontWeight: 600,
                                cursor: 'pointer',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.3rem'
                            }}
                        >
                            Test Live Queries in Query Optimizer &darr;
                        </button>
                    </div>
                </div>
            )}

            {recommendedSchema && (
                <div className={styles.featurePills}>
                    <span className={styles.pill}>Primary Keys</span>
                    <span className={styles.pill}>Foreign Keys</span>
                    <span className={styles.pill}>Performance Indexes</span>
                    <span className={styles.pill}>Integrity Constraints</span>
                </div>
            )}

            {isOptimizing && (
                <div className={styles.placeholder}>
                    <div className={styles.spinner}></div>
                    <p>Directly generating optimized schema with performance indexes, primary keys, and constraints...</p>
                </div>
            )}

            {!isOptimizing && !recommendedSchema && (
                <div className={styles.placeholder}>
                    <p>
                        {schemaContent 
                            ? 'Ready! Submitting schema will directly generate the optimized schema.'
                            : 'Enter your schema name and paste your SQL DDL in the Schema Input, then click "Parse & Auto-Optimize".'}
                    </p>
                </div>
            )}

            {error && (
                <div className={styles.errorBanner}>
                    <span>{error}</span>
                </div>
            )}

            {executionMsg && (
                <div className={styles.executionBanner}>
                    <div className={styles.bannerLeft}>
                        <span>{executionMsg}</span>
                    </div>
                    <span style={{ fontSize: '0.75rem', opacity: 0.85 }}>Mock data generated</span>
                </div>
            )}

            {!isOptimizing && recommendedSchema && (
                <>
                    <div className={styles.codeContainer}>
                        <div className={styles.codeHeader}>
                            <span>PostgreSQL / ANSI DDL (Auto-Optimized)</span>
                            <span>{recommendedSchema.split('\n').length} lines</span>
                        </div>
                        <pre className={styles.codeBlock}>
                            <code>{recommendedSchema}</code>
                        </pre>
                    </div>

                    {/* Visual SQL Relational Diagram */}
                    {diagramData && <SqlDiagram diagram={diagramData} />}
                </>
            )}
        </div>
    );
}
