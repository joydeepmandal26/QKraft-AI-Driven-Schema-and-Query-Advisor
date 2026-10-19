/**
 * Safe fetch utility that gracefully handles non-JSON error responses (like 500 "Internal Server Error"
 * or network proxy failures) and produces user-friendly error messages.
 */
export async function safeFetchJson(input, init) {
    const res = await fetch(input, init);
    const text = await res.text();

    let data = null;
    if (text) {
        try {
            data = JSON.parse(text);
        } catch {
            // Non-JSON response (e.g. plain text "Internal Server Error" or HTML error page)
        }
    }

    if (!res.ok) {
        let msg = data?.detail || data?.message || data?.error;
        if (!msg) {
            if (res.status === 500) {
                msg = 'Backend server error (500). Please ensure the Spring Boot backend is running on port 8000.';
            } else if (res.status === 502 || res.status === 503 || res.status === 504) {
                msg = `Backend unreachable (${res.status}). Please check that the Spring Boot backend server is running on port 8000.`;
            } else {
                msg = text || `Request failed with status ${res.status}`;
            }
        }
        throw new Error(msg);
    }

    return data !== null ? data : {};
}
