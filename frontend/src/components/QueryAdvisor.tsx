'use client';

import { useState } from 'react';
import styles from './QueryAdvisor.module.css';

export default function QueryAdvisor({ schemaContent }: { schemaContent: string }) {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<{role: 'user' | 'assistant', text: string}[]>([]);
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!query.trim()) return;
        
        const userMsg = query;
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setQuery('');
        setLoading(true);

        try {
            const res = await fetch('http://localhost:8000/api/advisor/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMsg, schema_content: schemaContent })
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || 'Error connecting to advisor.');
            }
            setMessages(prev => [...prev, { role: 'assistant', text: data.optimized_sql }]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', text: 'Error connecting to advisor.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <h2>Query Advisor Chat</h2>
            <div className={styles.chatWindow}>
                {messages.length === 0 && <p className={styles.placeholder}>Ask for an optimized query based on your schema...</p>}
                {messages.map((m, i) => (
                    <div key={i} className={m.role === 'user' ? styles.userMsg : styles.assistantMsg}>
                        {m.role === 'assistant' ? <pre><code>{m.text}</code></pre> : <p>{m.text}</p>}
                    </div>
                ))}
                {loading && <div className={styles.assistantMsg}><p>Thinking...</p></div>}
            </div>
            <div className={styles.inputArea}>
                <input 
                    type="text" 
                    className={styles.input}
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSend()}
                    placeholder="e.g. Write a query to fetch top 10 users..."
                    disabled={!schemaContent}
                />
                <button className={styles.button} onClick={handleSend} disabled={!schemaContent || loading}>Send</button>
            </div>
        </div>
    );
}
