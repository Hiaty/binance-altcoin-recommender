/**
 * 主应用逻辑
 */

// 开始分析
async function startAnalysis() {
    const btn = document.querySelector('.btn-primary');
    const loading = document.getElementById('loading');
    const btnText = document.getElementById('btnText');
    
    // 显示加载状态
    loading.style.display = 'inline';
    btnText.textContent = '分析中...';
    btn.disabled = true;
    
    try {
        // 获取参数
        const params = {
            count: parseInt(document.getElementById('count').value),
            minCap: parseInt(document.getElementById('minCap').value),
            sortBy: document.getElementById('sortBy').value
        };
        
        // 调用API
        const result = await api.analyze(params);
        
        if (result.success) {
            // 更新统计
            updateStats(result.stats);
            
            // 更新表格
            updateTable(result.data);
            
            // 更新时间
            document.getElementById('updateTime').textContent = new Date().toLocaleString();
            
            alert('分析完成！');
        } else {
            alert('分析失败: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败，请检查后端服务是否启动');
    } finally {
        // 恢复按钮状态
        loading.style.display = 'none';
        btnText.textContent = '🔄 开始分析';
        btn.disabled = false;
    }
}

// 更新统计卡片
function updateStats(stats) {
    document.getElementById('statRecommend').textContent = stats.recommend;
    document.getElementById('statWatch').textContent = stats.watch;
    document.getElementById('statAvoid').textContent = stats.avoid;
    document.getElementById('statWhale').textContent = stats.whale;
}

// 更新表格
function updateTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        // 根据推荐等级设置徽章样式
        const badgeClass = item.recommendation === '推荐' ? 'badge-recommend' :
                          item.recommendation === '观望' ? 'badge-watch' : 'badge-avoid';
        
        row.innerHTML = `
            <td>${item.rank}</td>
            <td><strong>${item.symbol}</strong><br><small>${item.name}</small></td>
            <td>${(item.market_cap / 10000).toFixed(0)}</td>
            <td class="${item.max_drawdown > 50 ? 'positive' : ''}">${item.max_drawdown.toFixed(1)}%</td>
            <td class="positive">${item.max_rebound.toFixed(0)}%</td>
            <td>${item.turnover_rate.toFixed(1)}%</td>
            <td class="${item.week_change > 0 ? 'positive' : 'negative'}">${item.week_change > 0 ? '+' : ''}${item.week_change.toFixed(1)}%</td>
            <td class="${item.month_change > 0 ? 'positive' : 'negative'}">${item.month_change > 0 ? '+' : ''}${item.month_change.toFixed(0)}%</td>
            <td class="${item.concentration > 80 ? 'negative' : ''}">${item.concentration.toFixed(1)}%</td>
            <td>${item.daily_pattern}</td>
            <td class="analysis-text">${item.analysis}</td>
            <td>${item.is_whale ? '是' : '否'}</td>
            <td><span class="badge ${badgeClass}">${item.recommendation}</span></td>
        `;
        
        tbody.appendChild(row);
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('币安山寨币智能推荐系统已加载');
    
    // 检查后端服务状态
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            console.log('后端服务状态:', data);
        })
        .catch(error => {
            console.warn('后端服务未启动，请先运行后端服务');
        });
});
