'use client';

import { useState } from 'react';
import SchemaVisualizer from '@/components/SchemaVisualizer';
import QueryAdvisor from '@/components/QueryAdvisor';
import PerformanceRater from '@/components/PerformanceRater';
import styles from './page.module.css';

export default function Home() {
  const [schemaContent, setSchemaContent] = useState('');

  const handleSchemaSubmit = async (schema: string) => {
    setSchemaContent(schema);
    // In a full implementation, we could also send this to the backend right away to save it
    try {
      await fetch('http://localhost:8000/api/schema', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: schema })
      });
    } catch (error) {
      console.error("Failed to save schema to backend", error);
    }
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>QKraft</h1>
        <p>AI Driven Schema and Query Advisor</p>
      </header>

      <main className={styles.main}>
        <div className={styles.leftColumn}>
          <SchemaVisualizer onSchemaSubmit={handleSchemaSubmit} />
        </div>
        <div className={styles.rightColumn}>
          <PerformanceRater schemaContent={schemaContent} />
          <QueryAdvisor schemaContent={schemaContent} />
        </div>
      </main>
    </div>
  );
}
