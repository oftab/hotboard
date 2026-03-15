const DATA_URL = './hotboard.json';
const HISTORY_URL = './history/';
const DEFAULT_VISIBLE_COUNT = 10;

let hotData = {
    version: '',
    generatedAt: '',
    items: [],
    sources: []
};

let platformGroups = {};
let expandedPlatforms = new Set();
let currentDate = 'today';
let currentCategory = 'all';

async function loadData() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const container = document.getElementById('platform-container');

    loading.classList.remove('hidden');
    error.classList.add('hidden');
    container.innerHTML = '';

    try {
        let url = DATA_URL;
        if (currentDate !== 'today') {
            url = `${HISTORY_URL}${currentDate}.json`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }
        hotData = await response.json();
        
        groupByPlatform();
        updateMeta();
        populateFilters();
        renderPlatforms();
    } catch (err) {
        console.error('Error loading data:', err);
        error.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
    }
}

function groupByPlatform() {
    platformGroups = {};
    
    hotData.items.forEach(item => {
        if (currentCategory !== 'all' && item.category !== currentCategory) {
            return;
        }
        
        const source = item.source;
        if (!platformGroups[source]) {
            platformGroups[source] = {
                items: [],
                category: item.category
            };
        }
        platformGroups[source].items.push(item);
    });
    
    Object.keys(platformGroups).forEach(source => {
        platformGroups[source].items.sort((a, b) => b.hot_score - a.hot_score);
    });
}

function updateMeta() {
    const lastUpdated = document.getElementById('last-updated');
    const itemCount = document.getElementById('item-count');
    const platformCount = document.getElementById('platform-count');

    const date = new Date(hotData.generatedAt);
    const formatted = date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
    lastUpdated.textContent = formatted;
    itemCount.textContent = hotData.items.length;
    platformCount.textContent = Object.keys(platformGroups).length;
}

function populateFilters() {
    const dateFilter = document.getElementById('date-filter');
    const today = new Date();
    
    dateFilter.innerHTML = '<option value="today">今天</option>';
    
    for (let i = 1; i <= 7; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        const displayStr = date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
        
        const option = document.createElement('option');
        option.value = dateStr;
        option.textContent = displayStr;
        dateFilter.appendChild(option);
    }
}

function getSourceName(source) {
    const names = {
        'hackernews': 'Hacker News',
        'github_trending': 'GitHub Trending',
        'reddit': 'Reddit',
        'weibo': '微博',
        'weibo_hot': '微博热搜',
        'zhihu': '知乎',
        'zhihu_daily': '知乎日报',
        'bilibili': '哔哩哔哩',
        'douyin': '抖音',
        'kuaishou': '快手',
        'xiaohongshu': '小红书',
        'douban': '豆瓣电影',
        'tieba': '百度贴吧',
        'toutiao': '今日头条',
        'baidu': '百度热搜',
        'thepaper': '澎湃新闻',
        'netease': '网易新闻',
        'sina': '新浪新闻',
        'sohu': '搜狐新闻',
        'ifeng': '凤凰网',
        'producthunt': 'Product Hunt',
        'devto': 'Dev.to',
        'digg': 'Digg',
        'weixin': '微信公众号',
        'v2ex': 'V2EX',
        'juejin': '掘金',
        'kr36': '36氪',
        'huxiu': '虎嗅',
        'ithome': 'IT之家',
        'sspai': '少数派',
        'coolapk': '酷安',
        'zol': '中关村在线',
        'lanjinger': '蓝鲸财经',
        'tmtpost': '钛媒体',
        'wallstreetcn': '华尔街见闻',
        'caixin': '财新网',
        'dingxiang': '丁香医生',
        'infoq': 'InfoQ',
        'segmentfault': '思否',
        'csdn': 'CSDN',
        'oschina': '开源中国',
        'rss': 'RSS订阅'
    };
    return names[source] || source;
}

function getSourceIcon(source) {
    const icons = {
        'hackernews': 'https://news.ycombinator.com/favicon.ico',
        'github_trending': 'https://github.com/favicon.ico',
        'reddit': 'https://www.reddit.com/favicon.ico',
        'weibo': 'https://weibo.com/favicon.ico',
        'weibo_hot': 'https://weibo.com/favicon.ico',
        'zhihu': 'https://www.zhihu.com/favicon.ico',
        'zhihu_daily': 'https://www.zhihu.com/favicon.ico',
        'bilibili': 'https://www.bilibili.com/favicon.ico',
        'douyin': 'https://www.douyin.com/favicon.ico',
        'kuaishou': 'https://www.kuaishou.com/favicon.ico',
        'xiaohongshu': 'https://www.xiaohongshu.com/favicon.ico',
        'douban': 'https://www.douban.com/favicon.ico',
        'tieba': 'https://tieba.baidu.com/favicon.ico',
        'toutiao': 'https://www.toutiao.com/favicon.ico',
        'baidu': 'https://www.baidu.com/favicon.ico',
        'thepaper': 'https://www.thepaper.cn/favicon.ico',
        'netease': 'https://news.163.com/favicon.ico',
        'sina': 'https://www.sina.com.cn/favicon.ico',
        'sohu': 'https://www.sohu.com/favicon.ico',
        'ifeng': 'https://www.ifeng.com/favicon.ico',
        'producthunt': 'https://www.producthunt.com/favicon.ico',
        'devto': 'https://dev.to/favicon.ico',
        'digg': 'https://digg.com/favicon.ico',
        'weixin': 'https://weixin.sogou.com/favicon.ico',
        'v2ex': 'https://www.v2ex.com/favicon.ico',
        'juejin': 'https://juejin.cn/favicon.ico',
        'kr36': 'https://36kr.com/favicon.ico',
        'huxiu': 'https://www.huxiu.com/favicon.ico',
        'ithome': 'https://www.ithome.com/favicon.ico',
        'sspai': 'https://sspai.com/favicon.ico',
        'coolapk': 'https://www.coolapk.com/favicon.ico',
        'zol': 'https://www.zol.com.cn/favicon.ico',
        'lanjinger': 'https://www.lanjinger.com/favicon.ico',
        'tmtpost': 'https://www.tmtpost.com/favicon.ico',
        'wallstreetcn': 'https://wallstreetcn.com/favicon.ico',
        'caixin': 'https://www.caixin.com/favicon.ico',
        'dingxiang': 'https://dxy.com/favicon.ico',
        'infoq': 'https://www.infoq.cn/favicon.ico',
        'segmentfault': 'https://segmentfault.com/favicon.ico',
        'csdn': 'https://www.csdn.net/favicon.ico',
        'oschina': 'https://www.oschina.net/favicon.ico',
        'rss': 'https://www.bbc.com/favicon.ico'
    };
    return icons[source] || '';
}

function getCategoryName(category) {
    const names = {
        'tech': '技术',
        'social': '社交',
        'news': '新闻',
        'entertainment': '娱乐',
        'finance': '财经',
        'health': '健康',
        'general': '综合'
    };
    return names[category] || '其他';
}

function getCategoryColor(category) {
    const colors = {
        'tech': { bg: '#3b82f615', text: '#60a5fa' },
        'social': { bg: '#ec489915', text: '#f472b6' },
        'news': { bg: '#ef444415', text: '#f87171' },
        'entertainment': { bg: '#f59e0b15', text: '#fbbf24' },
        'finance': { bg: '#10b98115', text: '#34d399' },
        'health': { bg: '#06b6d415', text: '#22d3ee' },
        'general': { bg: '#6b728015', text: '#9ca3af' }
    };
    return colors[category] || colors['general'];
}

function formatScore(score) {
    if (score >= 100000000) {
        return (score / 100000000).toFixed(1) + '亿';
    }
    if (score >= 10000) {
        return (score / 10000).toFixed(1) + '万';
    }
    return Math.round(score).toLocaleString();
}

function formatTime(dateStr) {
    if (!dateStr) return '';
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

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function togglePlatform(source) {
    const card = document.querySelector(`[data-card="${source}"]`);
    const list = document.querySelector(`[data-list="${source}"]`);
    
    if (expandedPlatforms.has(source)) {
        expandedPlatforms.delete(source);
        card.classList.remove('expanded');
        list.classList.remove('expanded');
        list.style.maxHeight = '0';
    } else {
        expandedPlatforms.add(source);
        card.classList.add('expanded');
        list.classList.add('expanded');
        list.style.maxHeight = list.scrollHeight + 'px';
    }
}

function renderPlatforms() {
    const container = document.getElementById('platform-container');
    container.innerHTML = '';

    const sortedPlatforms = Object.keys(platformGroups).sort((a, b) => {
        const categoryOrder = ['tech', 'social', 'news', 'entertainment', 'finance', 'health'];
        const catA = platformGroups[a].category;
        const catB = platformGroups[b].category;
        const orderA = categoryOrder.indexOf(catA);
        const orderB = categoryOrder.indexOf(catB);
        if (orderA !== orderB) return orderA - orderB;
        return getSourceName(a).localeCompare(getSourceName(b), 'zh-CN');
    });

    sortedPlatforms.forEach((source, idx) => {
        const group = platformGroups[source];
        const isExpanded = expandedPlatforms.has(source);
        const visibleItems = isExpanded ? group.items : group.items.slice(0, DEFAULT_VISIBLE_COUNT);
        const categoryColor = getCategoryColor(group.category);

        const card = document.createElement('div');
        card.className = `platform-card ${isExpanded ? 'expanded' : ''}`;
        card.setAttribute('data-card', source);
        card.style.animationDelay = `${idx * 0.04}s`;

        card.innerHTML = `
            <div class="platform-header" onclick="togglePlatform('${source}')">
                <div class="platform-left">
                    <img src="${getSourceIcon(source)}" alt="" class="platform-icon" onerror="this.style.display='none'">
                    <span class="platform-name">${getSourceName(source)}</span>
                    <span class="platform-count">${group.items.length}条</span>
                </div>
                <div class="platform-meta">
                    <span class="platform-category" style="background: ${categoryColor.bg}; color: ${categoryColor.text}">${getCategoryName(group.category)}</span>
                    <span class="platform-toggle">
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                            <path d="M3 5L7 9L11 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </span>
                </div>
            </div>
            <div class="platform-list ${isExpanded ? 'expanded' : ''}" data-list="${source}" style="${isExpanded ? 'max-height: ' + (group.items.length * 70) + 'px' : 'max-height: 0'}">
                <div class="platform-list-inner">
                    ${visibleItems.map((item, index) => `
                        <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="hot-item">
                            <span class="item-rank">${index + 1}</span>
                            <div class="item-content">
                                <h3 class="item-title">${escapeHtml(item.title)}</h3>
                                <p class="item-summary">${escapeHtml(item.summary)}</p>
                            </div>
                            <div class="item-meta">
                                <span class="item-score">${formatScore(item.hot_score)}</span>
                                <span class="item-time">${formatTime(item.published_at)}</span>
                            </div>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

document.getElementById('date-filter').addEventListener('change', (e) => {
    currentDate = e.target.value;
    loadData();
});

document.getElementById('category-filter').addEventListener('change', (e) => {
    currentCategory = e.target.value;
    groupByPlatform();
    renderPlatforms();
});

document.getElementById('refresh-btn').addEventListener('click', () => {
    currentDate = 'today';
    document.getElementById('date-filter').value = 'today';
    loadData();
});

loadData();
