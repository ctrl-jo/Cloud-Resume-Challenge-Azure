/**
 * Cloud Resume Challenge - Visitor Counter (Step 7: JavaScript)
 * 
 * Fetches the visitor count from the Azure Functions API (CosmosDB backend).
 * Temporarily mocked until Step 9/10 (API & Backend implementation).
 */

// Live Azure Function endpoint (deployed in Step 14)
const API_URL = 'https://func-cloud-resume-jdm.azurewebsites.net/api/GetResumeCounter';

/**
 * Retrieves the visitor count from the API.
 * In mock mode (empty API_URL), returns a static test number to prevent CORS / 404 errors.
 * @returns {Promise<number|null>} The visitor count, or null on failure.
 */
async function getVisitorCount() {
    // Mock mode: backend API is not yet deployed
    if (!API_URL) {
        console.info('[VisitorCounter] Backend API not yet configured. Returning mock count.');
        return 42;
    }

    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        // Expecting { count: number } from Azure Function
        return typeof data === 'object' && data !== null ? data.count : data;
    } catch (error) {
        console.error('[VisitorCounter] Error fetching visitor count:', error);
        return null;
    }
}

/**
 * Updates the DOM element #visitor-count with the retrieved count.
 */
async function updateVisitorCounter() {
    const counterElement = document.getElementById('visitor-count');
    if (!counterElement) {
        console.warn('[VisitorCounter] Element #visitor-count not found in DOM.');
        return;
    }

    const count = await getVisitorCount();
    if (count !== null && count !== undefined) {
        counterElement.textContent = count;
    } else {
        counterElement.textContent = '—';
    }
}

// Ensure the script executes only after the DOM is fully parsed and loaded
document.addEventListener('DOMContentLoaded', updateVisitorCounter);
