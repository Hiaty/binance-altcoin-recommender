/**
 * API 调用模块 v2
 */

const api = {
    async analyze(params) {
        const ts = Date.now();
        const resp = await fetch(`/api/analyze?t=${ts}`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Cache-Control": "no-cache" },
            body: JSON.stringify(params),
        });
        return resp.json();
    },

    async getSentiment() {
        const resp = await fetch("/api/sentiment");
        return resp.json();
    },

    async getBacktest() {
        const resp = await fetch("/api/backtest");
        return resp.json();
    },

    async getResults() {
        const resp = await fetch("/api/results");
        return resp.json();
    },
};
