/**
 * API调用模块
 */

const API_BASE = '';

const api = {
    /**
     * 执行分析
     */
    async analyze(params) {
        // 添加时间戳防止缓存
        const timestamp = new Date().getTime();
        const response = await fetch(`${API_BASE}/api/analyze?t=${timestamp}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            },
            body: JSON.stringify(params)
        });
        return response.json();
    },

    /**
     * 获取结果
     */
    async getResults() {
        const response = await fetch(`${API_BASE}/api/results`);
        return response.json();
    },

    /**
     * 获取币种列表
     */
    async getCoins() {
        const response = await fetch(`${API_BASE}/api/coins`);
        return response.json();
    },

    /**
     * 生成图表
     */
    async generateChart() {
        const response = await fetch(`${API_BASE}/api/chart`);
        return response.json();
    }
};
