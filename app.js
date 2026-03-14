const DATA_URL = './hotboard.json';

let hotData = {
    version: '',
    generatedAt: '',
    items: [],
    sources: []
};

let filteredItems = [];

async function loadData() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const hotList = document.getElementById('hot-list');

    loading.classList.remove('hidden');
    error.classList.add('hidden');
    hotList.innerHTML = '';

    try {
        const response = await fetch(DATA_URL);
        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }
        hotData = await response.json();
        filteredItems = [...hotData.items];
        
        updateMeta();
        populateFilters();
        renderItems();
    } catch (err) {
        console.error('Error loading data:', err);
        error.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
    }
}

function updateMeta() {
    const lastUpdated = document.getElementById('last-updated');
    const itemCount = document.getElementById('item-count');

    const date = new Date(hotData.generatedAt);
    const formatted = date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    });
    lastUpdated.textContent = `更新于 ${formatted}`;
    itemCount.textContent = hotData.items.length;
}

function populateFilters() {
    const sourceFilter = document.getElementById('source-filter');
    const currentValue = sourceFilter.value;

    sourceFilter.innerHTML = '<option value="all">全部</option>';
    
    const sources = new Set(hotData.items.map(item => item.source));
    sources.forEach(source => {
        const option = document.createElement('option');
        option.value = source;
        option.textContent = getSourceName(source);
        sourceFilter.appendChild(option);
    });

    sourceFilter.value = currentValue || 'all';
}

function getSourceName(source) {
    const names = {
        'hackernews': 'Hacker News',
        'github_trending': 'GitHub Trending',
        'reddit': 'Reddit',
        'weibo': '微博',
        'rss': 'RSS'
    };
    return names[source] || source;
}

function getSourceIcon(source) {
    const icons = {
        'hackernews': 'https://news.ycombinator.com/favicon.ico',
        'github_trending': 'https://github.com/favicon.ico',
        'reddit': 'https://www.reddit.com/favicon.ico',
        'weibo': 'https://weibo.com/favicon.ico',
        'rss': 'https://www.bbc.com/favicon.ico'
    };
    return icons[source] || '';
}

function getCategoryName(category) {
    const names = {
        'tech': '技术',
        'social': '社交',
        'news': '新闻',
        'general': '综合'
    };
    return names[category] || category;
}

function formatTime(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;
    
    return date.toLocaleDateString('zh-CN');
}

function renderItems() {
    const hotList = document.getElementById('hot-list');
    hotList.innerHTML = '';

    if (filteredItems.length === 0) {
        hotList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">暂无数据</p>';
        return;
    }

    filteredItems.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'hot-item';
        
        const score = Math.round(item.hot_score);
        
        card.innerHTML = `
            <span class="hot-rank">#${index + 1}</span>
            <div class="hot-header">
                <span class="hot-source">
                    <img src="${getSourceIcon(item.source)}" alt="" onerror="this.style.display='none'">
                    ${getSourceName(item.source)}
                </span>
                <span class="hot-category">${getCategoryName(item.category)}</span>
            </div>
            <h3 class="hot-title">
                <a href="${item.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title)}</a>
            </h3>
            <p class="hot-summary">${escapeHtml(item.summary)}</p>
            <div class="hot-meta">
                <span class="hot-score">🔥 ${score}</span>
                <span>📅 ${formatTime(item.published_at)}</span>
            </div>
            ${item.tags && item.tags.length > 0 ? `
                <div class="hot-tags">
                    ${item.tags.slice(0, 3).map(tag => `<span class="hot-tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
        `;
        
        hotList.appendChild(card);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function applyFilters() {
    const source = document.getElementById('source-filter').value;
    const category = document.getElementById('category-filter').value;
    const sort = document.getElementById('sort-filter').value;

    filteredItems = hotData.items.filter(item => {
        if (source !== 'all' && item.source !== source) return false;
        if (category !== 'all' && item.category !== category) return false;
        return true;
    });

    if (sort === 'score') {
        filteredItems.sort((a, b) => b.hot_score - a.hot_score);
    } else {
        filteredItems.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
    }

    renderItems();
}

document.getElementById('source-filter').addEventListener('change', applyFilters);
document.getElementById('category-filter').addEventListener('change', applyFilters);
document.getElementById('sort-filter').addEventListener('change', applyFilters);

document.getElementById('refresh-btn').addEventListener('click', () => {
    loadData();
});

loadData();
