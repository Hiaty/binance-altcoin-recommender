/**
 * 主应用逻辑 - 带分页功能
 */

// 全局变量
let currentData = [];
let currentPage = 1;
const itemsPerPage = 5;

// 开始分析
async function startAnalysis() {
    const btn = document.querySelector('.btn-primary');
    const loading = document.getElementById('loading');
    const btnText = document.getElementById('btnText');
    const statusDiv = document.getElementById('statusMessage');
    
    // 显示加载状态
    loading.style.display = 'inline';
    btnText.textContent = '分析中...';
    btn.disabled = true;
    if (statusDiv) {
        statusDiv.textContent = '正在分析，请稍候...';
        statusDiv.style.color = '#d29922';
    }
    
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
            // 保存数据
            currentData = result.data;
            currentPage = 1;
            
            // 更新统计
            updateStats(result.stats);
            
            // 更新表格（带分页）
            updateTableWithPagination(currentData);
            
            // 更新时间
            document.getElementById('updateTime').textContent = new Date().toLocaleString();
            
            // 显示成功状态（不弹窗）
            if (statusDiv) {
                statusDiv.textContent = `分析完成！共 ${currentData.length} 个币种`;
                statusDiv.style.color = '#238636';
            }
        } else {
            if (statusDiv) {
                statusDiv.textContent = '分析失败: ' + result.error;
                statusDiv.style.color = '#da3633';
            }
        }
    } catch (error) {
        console.error('Error:', error);
        if (statusDiv) {
            statusDiv.textContent = '请求失败，请检查后端服务是否启动';
            statusDiv.style.color = '#da3633';
        }
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

// 更新表格（带分页）
function updateTableWithPagination(data) {
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageData = data.slice(start, end);
    
    updateTable(pageData);
    updatePagination(data.length);
}

// 更新表格
function updateTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="13" class="empty">暂无数据</td></tr>';
        return;
    }
    
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

// 更新分页
function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const paginationDiv = document.getElementById('pagination');
    
    if (!paginationDiv) return;
    
    let html = `
        <div class="pagination-info">
            第 ${currentPage} / ${totalPages} 页，共 ${totalItems} 条
        </div>
        <div class="pagination-buttons">
    `;
    
    if (currentPage > 1) {
        html += `<button onclick="window.goToPage(${currentPage - 1})" class="btn-page">上一页</button>`;
    }
    
    // 显示页码（简化：只显示所有页码，避免...导致的混乱）
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            html += `<button class="btn-page active">${i}</button>`;
        } else {
            html += `<button onclick="window.goToPage(${i})" class="btn-page">${i}</button>`;
        }
    }
    
    if (currentPage < totalPages) {
        html += `<button onclick="window.goToPage(${currentPage + 1})" class="btn-page">下一页</button>`;
    }
    
    html += '</div>';
    paginationDiv.innerHTML = html;
}

// 跳转到指定页（绑定到window对象确保全局可用）
window.goToPage = function(page) {
    currentPage = page;
    updateTableWithPagination(currentData);
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('币安山寨币智能推荐系统已加载');
    
    // 添加状态消息区域
    const controls = document.querySelector('.controls');
    if (controls) {
        const statusDiv = document.createElement('div');
        statusDiv.id = 'statusMessage';
        statusDiv.style.marginTop = '10px';
        statusDiv.style.textAlign = 'center';
        statusDiv.style.fontWeight = 'bold';
        controls.appendChild(statusDiv);
    }
    
    // 添加分页区域
    const tableContainer = document.querySelector('.table-container');
    if (tableContainer) {
        const paginationDiv = document.createElement('div');
        paginationDiv.id = 'pagination';
        paginationDiv.className = 'pagination';
        tableContainer.after(paginationDiv);
    }
    
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
