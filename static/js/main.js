// 主要JavaScript功能

// 全局变量
let currentUser = null;
let spacesData = [];
let filteredSpaces = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 添加页面加载动画
    addFadeInAnimation();
    
    // 初始化工具提示
    initializeTooltips();
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 如果在地图页面，初始化地图
    if (document.getElementById('campusMap')) {
        initializeCampusMap();
    }
}

// 添加淡入动画
function addFadeInAnimation() {
    const elements = document.querySelectorAll('.card, .btn, .form-control');
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// 初始化工具提示
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 绑定事件监听器
function bindEventListeners() {
    // 表单验证
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // 筛选器变化
    const filters = document.querySelectorAll('#spaceTypeFilter, #crowdingFilter, input[type="checkbox"]');
    filters.forEach(filter => {
        filter.addEventListener('change', applyFilters);
    });
}

// 处理表单提交
function handleFormSubmit(event) {
    const form = event.target;
    
    // 添加加载状态
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="loading-spinner"></span> 处理中...';
        submitBtn.disabled = true;
        
        // 模拟处理时间
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 2000);
    }
}

// 初始化校园地图
function initializeCampusMap() {
    // 模拟从服务器获取空间数据
    fetchSpacesData().then(data => {
        spacesData = data;
        filteredSpaces = [...spacesData];
        renderSpaceMarkers();
    });
}

// 刷新地图数据
function refreshMap() {
    console.log('刷新地图数据...');

    // 显示加载提示
    const btn = event.target.closest('button');
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>刷新中...';
    btn.disabled = true;

    // 重新获取数据
    fetchSpacesData().then(data => {
        spacesData = data;
        filteredSpaces = [...spacesData];
        renderSpaceMarkers();

        // 恢复按钮状态
        btn.innerHTML = originalHTML;
        btn.disabled = false;

        // 显示成功提示
        showToast('地图数据已更新', 'success');
    }).catch(() => {
        btn.innerHTML = originalHTML;
        btn.disabled = false;
        showToast('刷新失败，请重试', 'error');
    });
}

// 显示提示消息
function showToast(message, type = 'info') {
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} position-fixed top-0 start-50 translate-middle-x mt-3`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
        ${message}
    `;

    document.body.appendChild(toast);

    // 3秒后自动移除
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.5s';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

// 获取空间数据（从API获取）
async function fetchSpacesData() {
    try {
        const response = await fetch('/api/spaces');
        if (!response.ok) {
            throw new Error('Failed to fetch spaces data');
        }
        const data = await response.json();

        // 转换数据格式以匹配前端需求
        return data.map(space => ({
            ...space,
            lastUpdate: space.lastUpdate ? new Date(space.lastUpdate) : new Date(),
            tags: space.tags || []
        }));
    } catch (error) {
        console.error('Error fetching spaces data:', error);
        // 返回默认数据作为后备
        return [
            {
                id: 1,
                name: '图书馆阅览室',
                building: '图书馆',
                floor: '2F',
                x: 15.6,
                y: 16.7,
                crowding: 3,
                noise: 2,
                wifi: 4,
                power: true,
                capacity: 200,
                type: '图书馆',
                lastUpdate: new Date(Date.now() - 5 * 60 * 1000),
                tags: ['安静', '有电源', '网速快']
            },
            {
                id: 2,
                name: 'A301自习室',
                building: 'A座教学楼',
                floor: '3F',
                x: 38.8,
                y: 15.0,
                crowding: 2,
                noise: 1,
                wifi: 5,
                power: true,
                capacity: 50,
                type: '自习室',
                lastUpdate: new Date(Date.now() - 10 * 60 * 1000),
                tags: ['很安静', '有电源', '网速极快']
            },
            {
                id: 3,
                name: 'B201讨论室',
                building: 'B座教学楼',
                floor: '2F',
                x: 57.5,
                y: 15.0,
                crowding: 4,
                noise: 3,
                wifi: 4,
                power: true,
                capacity: 20,
                type: '讨论室',
                lastUpdate: new Date(Date.now() - 3 * 60 * 1000),
                tags: ['适合讨论', '有电源', '投影设备']
            },
            {
                id: 4,
                name: '星巴克咖啡厅',
                building: '学生中心',
                floor: '1F',
                x: 12.5,
                y: 40.0,
                crowding: 3,
                noise: 4,
                wifi: 3,
                power: false,
                capacity: 30,
                type: '咖啡厅',
                lastUpdate: new Date(Date.now() - 15 * 60 * 1000),
                tags: ['休闲', '有饮品', '氛围好']
            },
            {
                id: 5,
                name: '活动中心自习区',
                building: '学生活动中心',
                floor: '2F',
                x: 34.4,
                y: 41.7,
                crowding: 1,
                noise: 2,
                wifi: 4,
                power: true,
                capacity: 80,
                type: '自习室',
                lastUpdate: new Date(Date.now() - 8 * 60 * 1000),
                tags: ['宽敞', '有电源', '光线好']
            }
        ];
    }
}

// 渲染空间标记
function renderSpaceMarkers() {
    const mapElement = document.getElementById('campusMap');
    if (!mapElement) return;
    
    // 清除现有标记
    const existingMarkers = mapElement.querySelectorAll('.space-marker');
    existingMarkers.forEach(marker => marker.remove());
    
    // 添加新标记
    filteredSpaces.forEach(space => {
        const marker = createSpaceMarker(space);
        mapElement.appendChild(marker);
    });
}

// 创建空间标记
function createSpaceMarker(space) {
    const marker = document.createElement('div');
    marker.className = `space-marker crowding-${space.crowding}`;
    marker.style.left = `${space.x}%`;
    marker.style.top = `${space.y}%`;
    marker.title = `${space.name} - ${getCrowdingText(space.crowding)}`;
    marker.dataset.spaceId = space.id;
    
    // 添加点击事件
    marker.addEventListener('click', () => showSpaceInfo(space));
    
    // 添加悬停效果
    marker.addEventListener('mouseenter', () => {
        marker.style.transform = 'scale(1.3)';
        showQuickInfo(space, marker);
    });
    
    marker.addEventListener('mouseleave', () => {
        marker.style.transform = 'scale(1)';
        hideQuickInfo();
    });
    
    return marker;
}

// 显示空间详细信息
function showSpaceInfo(space) {
    const panel = document.getElementById('spaceInfoPanel');
    if (!panel) return;
    
    const crowdingText = getCrowdingText(space.crowding);
    const noiseText = getNoiseText(space.noise);
    const wifiText = getWifiText(space.wifi);
    const timeAgo = getTimeAgo(space.lastUpdate);
    
    panel.innerHTML = `
        <div class="space-info-content">
            <h5 class="mb-3 text-primary">
                <i class="fas fa-map-marker-alt me-2"></i>
                ${space.name}
            </h5>
            <p class="text-muted mb-3">
                <i class="fas fa-building me-2"></i>
                ${space.building} ${space.floor}
            </p>
            
            <div class="space-stats mb-4">
                <div class="row g-2">
                    <div class="col-6">
                        <div class="stat-item p-2 bg-light rounded">
                            <small class="text-muted">拥挤程度</small>
                            <div class="fw-bold text-${getCrowdingColor(space.crowding)}">
                                ${crowdingText}
                            </div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="stat-item p-2 bg-light rounded">
                            <small class="text-muted">噪音水平</small>
                            <div class="fw-bold">${noiseText}</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="stat-item p-2 bg-light rounded">
                            <small class="text-muted">网速质量</small>
                            <div class="fw-bold">${wifiText}</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="stat-item p-2 bg-light rounded">
                            <small class="text-muted">电源插座</small>
                            <div class="fw-bold text-${space.power ? 'success' : 'danger'}">
                                ${space.power ? '可用' : '不可用'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="space-tags mb-3">
                ${space.tags.map(tag => `
                    <span class="badge bg-secondary me-1 mb-1">${tag}</span>
                `).join('')}
            </div>
            
            <div class="space-meta text-muted small mb-3">
                <i class="fas fa-clock me-1"></i>
                最后更新: ${timeAgo}
            </div>
            
            <div class="space-actions">
                <button class="btn btn-outline-primary btn-sm w-100 mb-2" onclick="getDirections(${space.id})">
                    <i class="fas fa-route me-2"></i>获取路线
                </button>
                <button class="btn btn-outline-success btn-sm w-100" onclick="reportSpace(${space.id})">
                    <i class="fas fa-edit me-2"></i>更新状态
                </button>
            </div>
        </div>
    `;
    
    // 添加动画效果
    panel.style.opacity = '0';
    panel.style.transform = 'translateY(20px)';
    setTimeout(() => {
        panel.style.transition = 'all 0.3s ease';
        panel.style.opacity = '1';
        panel.style.transform = 'translateY(0)';
    }, 50);
}

// 应用筛选条件
function applyFilters() {
    const typeFilter = document.getElementById('spaceTypeFilter')?.value;
    const crowdingFilter = document.getElementById('crowdingFilter')?.value;
    const powerRequired = document.getElementById('powerAvailable')?.checked;
    const quietRequired = document.getElementById('quietSpace')?.checked;
    const goodWifiRequired = document.getElementById('goodWifi')?.checked;
    
    filteredSpaces = spacesData.filter(space => {
        // 类型筛选
        if (typeFilter && space.type !== typeFilter) return false;
        
        // 拥挤程度筛选
        if (crowdingFilter && space.crowding != crowdingFilter) return false;
        
        // 电源需求
        if (powerRequired && !space.power) return false;
        
        // 安静需求
        if (quietRequired && space.noise > 2) return false;
        
        // 网速需求
        if (goodWifiRequired && space.wifi < 4) return false;
        
        return true;
    });
    
    renderSpaceMarkers();
    
    // 显示筛选结果
    showFilterResults();
}

// 显示筛选结果
function showFilterResults() {
    const resultCount = filteredSpaces.length;
    const totalCount = spacesData.length;
    
    // 可以在这里添加结果提示
    console.log(`筛选结果: ${resultCount}/${totalCount} 个空间`);
}

// 工具函数
function getCrowdingText(level) {
    const texts = ['', '很空闲', '较空闲', '一般', '较拥挤', '很拥挤'];
    return texts[level] || '未知';
}

function getNoiseText(level) {
    const texts = ['', '很安静', '较安静', '一般', '较嘈杂', '很嘈杂'];
    return texts[level] || '未知';
}

function getWifiText(level) {
    const texts = ['', '很差', '较差', '一般', '较好', '很好'];
    return texts[level] || '未知';
}

function getCrowdingColor(level) {
    const colors = ['', 'success', 'warning', 'info', 'warning', 'danger'];
    return colors[level] || 'secondary';
}

function getTimeAgo(date) {
    const now = new Date();
    const diff = Math.floor((now - date) / 1000 / 60); // 分钟差
    
    if (diff < 1) return '刚刚';
    if (diff < 60) return `${diff}分钟前`;
    if (diff < 1440) return `${Math.floor(diff / 60)}小时前`;
    return `${Math.floor(diff / 1440)}天前`;
}

// 获取路线
function getDirections(spaceId) {
    const space = spacesData.find(s => s.id === spaceId);
    if (space) {
        alert(`正在为您规划到"${space.name}"的路线...`);
        // 这里可以集成地图导航API
    }
}

// 上报空间状态
function reportSpace(spaceId) {
    const modal = new bootstrap.Modal(document.getElementById('reportModal'));
    const spaceSelect = document.getElementById('spaceSelect');
    
    if (spaceSelect) {
        spaceSelect.value = spaceId;
    }
    
    modal.show();
}

// 提交上报
async function submitReport() {
    const form = document.getElementById('reportForm');
    const submitBtn = document.querySelector('#reportModal .btn-success');
    const originalText = submitBtn.innerHTML;

    // 获取表单数据
    const spaceId = document.getElementById('spaceSelect').value;
    const crowdingLevel = document.getElementById('crowdingLevel').value;
    const noiseLevel = document.getElementById('noiseLevel').value;
    const wifiQuality = document.getElementById('wifiQuality').value;
    const powerAvailable = document.getElementById('powerAvailableReport').checked;
    const comment = document.getElementById('comment').value;

    // 验证必填字段
    if (!spaceId || !crowdingLevel || !noiseLevel || !wifiQuality) {
        alert('请填写所有必填字段');
        return;
    }

    // 显示加载状态
    submitBtn.innerHTML = '<span class="loading-spinner"></span> 提交中...';
    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                space_id: parseInt(spaceId),
                crowding_level: parseInt(crowdingLevel),
                noise_level: parseInt(noiseLevel),
                wifi_quality: parseInt(wifiQuality),
                power_available: powerAvailable,
                comment: comment
            })
        });

        const result = await response.json();

        if (result.success) {
            showSuccessMessage(result.message);

            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
            modal.hide();

            // 重置表单
            form.reset();

            // 更新用户积分
            updateUserPoints(10);

            // 刷新地图数据
            initializeCampusMap();
        } else {
            alert('上报失败: ' + result.message);
        }
    } catch (error) {
        console.error('Error submitting report:', error);
        alert('上报失败，请检查网络连接后重试');
    } finally {
        // 恢复按钮
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// 显示成功消息
function showSuccessMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 自动移除
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// 更新用户积分
function updateUserPoints(points) {
    const pointsBadge = document.querySelector('.badge.bg-warning');
    if (pointsBadge) {
        const currentPoints = parseInt(pointsBadge.textContent);
        pointsBadge.textContent = `${currentPoints + points}分`;
        
        // 添加动画效果
        pointsBadge.style.transform = 'scale(1.2)';
        setTimeout(() => {
            pointsBadge.style.transform = 'scale(1)';
        }, 300);
    }
}
