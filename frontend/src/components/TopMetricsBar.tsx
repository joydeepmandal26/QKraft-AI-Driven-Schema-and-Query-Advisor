import styles from './TopMetricsBar.module.css';
import { SchemaBenchmark } from './PerformanceComparisonModal';

interface TopMetricsBarProps {
    avgTimeSavedPct: number;
    totalTimeSavedMs: number;
    queryCount: number;
    schemaName: string;
    schemaExecuted: boolean;
    tableCount: number;
    schemaId?: number | null;
    isMeasuring?: boolean;
    benchmark?: SchemaBenchmark | null;
    testScore?: number;
    isAlreadyOptimized?: boolean;
}

export default function TopMetricsBar({
    avgTimeSavedPct,
    totalTimeSavedMs,
    queryCount,
    schemaName,
    schemaExecuted,
    tableCount,
    schemaId = null,
    isMeasuring = false,
    benchmark = null,
    testScore = 100,
    isAlreadyOptimized = false
}: TopMetricsBarProps) {
    return (
        <div className={styles.metricsContainer}>
                {/* 1. SCHEMA TEST SCORE - Evaluated on basis of input schema */}
                <div className={`${styles.metricCard} ${styles.cardGlowCyan}`}>
                    <div className={styles.metricHeader}>
                        <span className={styles.metricLabel}>Schema Test Score</span>
                        <span className={styles.metricIcon}>🎯</span>
                    </div>
                    {isMeasuring ? (
                        <div className={styles.metricValue}>
                            <span className={styles.measuringValue}>
                                <span className={styles.measuringSpinner}></span>
                                Scoring...
                            </span>
                        </div>
                    ) : (
                        <div className={styles.metricValue}>
                            {testScore}
                            <span className={styles.metricUnit}>/ 100</span>
                        </div>
                    )}
                    <div className={styles.metricSubtext}>
                        {testScore === 100 ? (
                            <span style={{ color: '#34d399', fontWeight: 600 }}>🏆 100% Production-Ready</span>
                        ) : testScore >= 80 ? (
                            <span style={{ color: '#60a5fa', fontWeight: 600 }}>⚡ Minor Tweaks Needed</span>
                        ) : (
                            <span style={{ color: '#f59e0b', fontWeight: 600 }}>⚠️ Needs Optimization</span>
                        )}
                    </div>
                </div>

                {/* 2. AVG. PERFORMANCE GAIN */}
                <div className={`${styles.metricCard} ${styles.cardGlowGreen}`}>
                    <div className={styles.metricHeader}>
                        <span className={styles.metricLabel}>Avg. Performance Gain</span>
                        <span className={styles.metricIcon}>⚡</span>
                    </div>
                    {isMeasuring ? (
                        <div className={styles.metricValue}>
                            <span className={styles.measuringValue}>
                                <span className={styles.measuringSpinner}></span>
                                Measuring...
                            </span>
                        </div>
                    ) : isAlreadyOptimized && queryCount === 0 ? (
                        <div className={styles.metricValue}>
                            Peak
                            <span className={styles.metricUnit}>optimal</span>
                        </div>
                    ) : avgTimeSavedPct > 0 ? (
                        <div className={styles.metricValue}>
                            +{avgTimeSavedPct.toFixed(1)}%
                            <span className={styles.metricUnit}>faster</span>
                        </div>
                    ) : (
                        <div className={`${styles.metricValue} ${styles.emptyValue}`}>
                            --%
                            <span className={styles.metricUnit}>gain</span>
                        </div>
                    )}
                    <div className={styles.metricSubtext}>
                        {isMeasuring 
                            ? 'Benchmarking schema...' 
                            : isAlreadyOptimized && queryCount === 0 
                            ? 'Input schema already optimal' 
                            : avgTimeSavedPct > 0 
                            ? 'Optimized vs Non-Optimized' 
                            : 'Awaiting execution'}
                    </div>
                </div>

                {/* 3. TOTAL EXECUTION TIME SAVED */}
                <div className={`${styles.metricCard} ${styles.cardGlowBlue}`}>
                    <div className={styles.metricHeader}>
                        <span className={styles.metricLabel}>Total Execution Time Saved</span>
                        <span className={styles.metricIcon}>⏱️</span>
                    </div>
                    {isMeasuring ? (
                        <div className={styles.metricValue}>
                            <span className={styles.measuringValue}>
                                <span className={styles.measuringSpinner}></span>
                                Measuring...
                            </span>
                        </div>
                    ) : totalTimeSavedMs > 0 ? (
                        <div className={styles.metricValue}>
                            {totalTimeSavedMs.toFixed(1)}
                            <span className={styles.metricUnit}>ms saved</span>
                        </div>
                    ) : isAlreadyOptimized ? (
                        <div className={styles.metricValue}>
                            0.0
                            <span className={styles.metricUnit}>ms saved</span>
                        </div>
                    ) : (
                        <div className={`${styles.metricValue} ${styles.emptyValue}`}>
                            -- ms
                            <span className={styles.metricUnit}>saved</span>
                        </div>
                    )}
                    <div className={styles.metricSubtext}>
                        {isMeasuring 
                            ? 'Analyzing query latency...' 
                            : totalTimeSavedMs > 0 
                            ? 'Cumulative DB latency reduction' 
                            : isAlreadyOptimized 
                            ? 'Zero schema latency overhead' 
                            : 'Awaiting execution'}
                    </div>
                </div>

                {/* 3. ACTIVE SCHEMA */}
                <div className={`${styles.metricCard} ${styles.cardGlowPurple}`}>
                    <div className={styles.metricHeader}>
                        <span className={styles.metricLabel}>Active Schema</span>
                        <span className={styles.metricIcon}>📂</span>
                    </div>
                    <div className={styles.metricValue} style={{ fontSize: '1.25rem', wordBreak: 'break-word' }}>
                        {schemaName || 'Active Workspace'}
                    </div>
                    <div className={styles.metricSubtext}>
                        <span className={styles.badgeLive}>
                            <span className={styles.liveDot}></span>
                            {schemaExecuted ? `${tableCount} Tables in DB` : 'In Memory'}
                        </span>
                    </div>
                </div>

                {/* 4. QUERIES EXECUTED */}
                <div className={`${styles.metricCard} ${styles.cardGlowAmber}`}>
                    <div className={styles.metricHeader}>
                        <span className={styles.metricLabel}>Queries Executed</span>
                        <span className={styles.metricIcon}>🚀</span>
                    </div>
                    <div className={styles.metricValue}>
                        {queryCount}
                        <span className={styles.metricUnit}>runs</span>
                    </div>
                    <div className={styles.metricSubtext}>
                        Scoped to current schema
                    </div>
                </div>
            </div>
    );
}
