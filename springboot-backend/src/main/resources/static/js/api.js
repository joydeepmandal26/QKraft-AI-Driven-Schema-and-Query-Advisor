/**
 * QKraft API Client (Vanilla JavaScript)
 * Communicates with the Spring Boot PostgreSQL Backend REST endpoints.
 */

const API = {
    baseUrl: '', // relative to current origin

    async checkHealth() {
        try {
            const res = await fetch(`${this.baseUrl}/api/health`);
            if (!res.ok) throw new Error('Health check failed');
            return await res.json();
        } catch (e) {
            console.warn('API Health Check failed:', e);
            return null;
        }
    },

    async getAllSchemas() {
        const res = await fetch(`${this.baseUrl}/api/schemas`);
        if (!res.ok) throw new Error('Failed to fetch schemas');
        return await res.json();
    },

    async getSchemaById(id) {
        const res = await fetch(`${this.baseUrl}/api/schema/${id}`);
        if (!res.ok) throw new Error(`Schema ${id} not found`);
        return await res.json();
    },

    async saveSchema(name, content, optimizedContent, diagramData) {
        const res = await fetch(`${this.baseUrl}/api/schema`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name || 'Untitled Schema',
                content: content,
                optimized_content: optimizedContent,
                diagram_data: typeof diagramData === 'object' ? JSON.stringify(diagramData) : diagramData
            })
        });
        if (!res.ok) throw new Error('Failed to save schema');
        return await res.json();
    },

    async analyzeSchema(ddl) {
        const res = await fetch(`${this.baseUrl}/api/schema/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ schema_content: ddl })
        });
        if (!res.ok) throw new Error('Failed to analyze schema');
        return await res.json();
    },

    async recommendSchema(ddl) {
        const res = await fetch(`${this.baseUrl}/api/schema/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ schema_content: ddl })
        });
        if (!res.ok) throw new Error('Failed to get schema recommendations');
        return await res.json();
    },

    async executeSandbox(schemaId, schemaName, ddl) {
        const res = await fetch(`${this.baseUrl}/api/schema/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                schema_id: schemaId,
                schema_name: schemaName,
                ddl: ddl
            })
        });
        if (!res.ok) throw new Error('Failed to execute sandbox in PostgreSQL');
        return await res.json();
    },

    async runQuery(schemaId, sqlQuery, unoptimizedSql, userPrompt) {
        const res = await fetch(`${this.baseUrl}/api/query/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                schema_id: schemaId,
                sql_query: sqlQuery,
                unoptimized_sql: unoptimizedSql,
                user_prompt: userPrompt
            })
        });
        if (!res.ok) throw new Error('Failed to run query in PostgreSQL');
        return await res.json();
    },

    async askAdvisor(query, schemaContent) {
        const res = await fetch(`${this.baseUrl}/api/advisor/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                schema_content: schemaContent
            })
        });
        if (!res.ok) throw new Error('Failed to get advisor feedback');
        return await res.json();
    },

    async deleteSchema(id) {
        const res = await fetch(`${this.baseUrl}/api/schema/${id}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error(`Failed to delete schema ${id}`);
        return await res.json();
    }
};
