/* ==========================================
   ScoutIQ — App Logic (app.js)
   Fully API-driven: all data fetched from Flask backend
   ========================================== */

// =========== API BASE ===========
const API = '';  // Same-origin; Flask serves both API and static files

// =========== STATE ===========
let watchlist = new Set();
let compareList = new Set();
let currentSection = 'dashboard';
let allProducts = [];
let filteredProducts = [];
let displayedCount = 12;
let charts = {};

// — Mutable copies of server data for local UI —
let alertsData = [];
let categoriesData = [];
let geoData = [];
let brandsData = [];
let insightsData = [];

// =========== API HELPERS ===========
async function api(path, options = {}) {
  try {
    const res = await fetch(`${API}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.error(`API Error [${path}]:`, err);
    throw err;
  }
}

const apiGet    = (path) => api(path);
const apiPost   = (path, body) => api(path, { method: 'POST', body: JSON.stringify(body) });
const apiPut    = (path, body) => api(path, { method: 'PUT', body: JSON.stringify(body) });
const apiPatch  = (path, body) => api(path, { method: 'PATCH', body: JSON.stringify(body) });
const apiDelete = (path) => api(path, { method: 'DELETE' });

// =========== INIT ===========
document.addEventListener('DOMContentLoaded', async () => {
  createToastContainer();

  // Show a loading indicator
  showToast('Loading data from server…', 'info', '⏳');

  try {
    // Fetch data sequentially to prevent CPU/memory spikes on Render Free Tier 
    // which cause intermittent 502 errors when hitting 7 endpoints simultaneously.
    // Fetch SMALL JSON packets first for immediate UI feedback (KPIs, navigation, sidebar)
    // Moving heavy '/api/products' fetch to the end to prevent blocking other UI updates.
    const [watchlistIds, alerts, categories, geo, brands, insights] = await Promise.all([
      apiGet('/api/watchlist'),
      apiGet('/api/alerts'),
      apiGet('/api/categories'),
      apiGet('/api/geo'),
      apiGet('/api/brands'),
      apiGet('/api/insights'),
    ]);

    watchlist = new Set(watchlistIds);
    alertsData = alerts;
    categoriesData = categories;
    geoData = geo;
    brandsData = brands;
    insightsData = insights;

    // Initialize UI structure immediately
    initNavigation();
    initSidebar();
    
    // Call render and animate counters right away with what we have
    renderDashboard(); 
    updateWatchlistBadge();
    
    // NOW fetch the heavy products list in the background
    const products = await apiGet('/api/products');
    allProducts = products;
    filteredProducts = [...allProducts];

    // Final rendering updates
    renderScoutProducts();
    renderWatchlist();
    renderTrends();
    renderAlerts();
    initSearch();
    initModals();
    initTicker();

    showToast('Data loaded successfully!', 'success', '✅');
  } catch (err) {
    showToast('Failed to load data from server. Using offline mode.', 'warning', '⚠️');
    console.error('Init error:', err);
    // Still init UI elements even if API fails
    initNavigation();
    initSidebar();
    initSearch();
    initModals();
  }
});

// =========== NAVIGATION ===========
function initNavigation() {
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const section = btn.dataset.section;
      if (!section) return;
      navigateTo(section);
    });
  });

  document.querySelectorAll('[data-section]').forEach(btn => {
    if (!btn.classList.contains('nav-item')) {
      btn.addEventListener('click', () => navigateTo(btn.dataset.section));
    }
  });
}

function navigateTo(section) {
  currentSection = section;
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));

  const navBtn = document.getElementById(`nav-${section}`);
  if (navBtn) navBtn.classList.add('active');

  const sectionEl = document.getElementById(`section-${section}`);
  if (sectionEl) sectionEl.classList.add('active');

  const titles = {
    dashboard: ['Dashboard', 'Your product intelligence overview'],
    scout: ['Scout Products', 'Discover and analyze winning products'],
    watchlist: ['My Watchlist', 'Products you are tracking'],
    compare: ['Compare Products', 'Side-by-side product analysis'],
    trends: ['Market Trends', 'Real-time market and trend intelligence'],
    alerts: ['Price Alerts', 'Manage your price and trend alerts'],
  };

  const [title, subtitle] = titles[section] || ['ScoutIQ', ''];
  document.getElementById('pageTitle').textContent = title;
  document.getElementById('pageSubtitle').textContent = subtitle;

  if (section === 'compare') {
    renderCompare();
    setTimeout(() => {
      const cb = document.getElementById('clearCompareBtn');
      if (cb) cb.onclick = () => { compareList.clear(); renderCompare(); };
    }, 0);
  }
  if (section === 'watchlist') renderWatchlist();
}

// =========== SIDEBAR ===========
function initSidebar() {
  const btn = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const main = document.getElementById('mainContent');
  btn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    main.classList.toggle('expanded');
  });
}

// =========== DASHBOARD ===========
async function renderDashboard() {
  const container = document.getElementById('dashboardProducts');
  const top = [...allProducts].sort((a, b) => b.score - a.score).slice(0, 4);
  container.innerHTML = top.map(p => productCardHTML(p)).join('');
  attachProductCardEvents(container);
  
  // Defer chart drawing slightly to ensure layout / offsetWidth is ready
  requestAnimationFrame(() => {
    setTimeout(initCharts, 50);
  });
  
  animateKPIs();
}

async function animateKPIs() {
  try {
    const dashData = await apiGet('/api/dashboard');
    
    const animate = (id, target, isCurrency = false, isDec = false) => {
      const el = document.getElementById(id);
      if (!el) return;
      let count = 0;
      if (target === 0) { el.textContent = isCurrency ? '$0' : '0'; return; }
      const duration = 1500; // ms
      const startTime = performance.now();
      
      const update = (now) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = target * easeOut;
        
        if (isCurrency) {
          el.textContent = '$' + (current >= 1000000 ? (current / 1000000).toFixed(1) + 'M' : current.toLocaleString());
        } else if (isDec) {
          el.textContent = current.toFixed(1);
        } else {
          el.textContent = Math.round(current).toLocaleString();
        }
        
        if (progress < 1) requestAnimationFrame(update);
      };
      requestAnimationFrame(update);
    };

    animate('kpiProducts', dashData.totalProducts || 0);
    animate('kpiWatchlist', dashData.watchlistCount || 0);
    animate('kpiMarket', (dashData.marketOpportunity || 0) * 1000000, true);
    animate('kpiTrending', dashData.trending || 0);
    
  } catch (err) {
    console.error('KPI fetch error:', err);
  }
}

// =========== CHARTS ===========
function initCharts() {
  drawActivityChart();
  drawCategoryChart();
}

function drawActivityChart() {
  const canvas = document.getElementById('activityChart');
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth || 600;
  canvas.height = 200;

  const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const data = [42, 78, 55, 91, 67, 83, 120];

  const w = canvas.width, h = canvas.height;
  const pad = { top: 20, right: 20, bottom: 30, left: 40 };
  const chartW = w - pad.left - pad.right;
  const chartH = h - pad.top - pad.bottom;
  const maxVal = Math.max(...data) * 1.15;

  ctx.clearRect(0, 0, w, h);

  // Grid lines
  ctx.strokeStyle = 'rgba(255,255,255,0.05)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + (chartH / 4) * i;
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(w - pad.right, y); ctx.stroke();
    ctx.fillStyle = 'rgba(139,155,200,0.5)';
    ctx.font = '10px Inter';
    ctx.textAlign = 'right';
    ctx.fillText(Math.round(maxVal - (maxVal / 4) * i), pad.left - 6, y + 4);
  }

  // Gradient fill
  const grad = ctx.createLinearGradient(0, pad.top, 0, h - pad.bottom);
  grad.addColorStop(0, 'rgba(139,92,246,0.4)');
  grad.addColorStop(1, 'rgba(139,92,246,0)');

  const pts = data.map((v, i) => ({
    x: pad.left + (chartW / (data.length - 1)) * i,
    y: pad.top + chartH * (1 - v / maxVal)
  }));

  // Smooth curve
  ctx.beginPath();
  ctx.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) {
    const cpX = (pts[i - 1].x + pts[i].x) / 2;
    ctx.bezierCurveTo(cpX, pts[i - 1].y, cpX, pts[i].y, pts[i].x, pts[i].y);
  }
  ctx.lineTo(pts[pts.length - 1].x, h - pad.bottom);
  ctx.lineTo(pts[0].x, h - pad.bottom);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Stroke
  ctx.beginPath();
  ctx.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) {
    const cpX = (pts[i - 1].x + pts[i].x) / 2;
    ctx.bezierCurveTo(cpX, pts[i - 1].y, cpX, pts[i].y, pts[i].x, pts[i].y);
  }
  ctx.strokeStyle = '#8b5cf6';
  ctx.lineWidth = 2.5;
  ctx.stroke();

  // Points
  pts.forEach((pt, i) => {
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#8b5cf6'; ctx.fill();
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, 2, 0, Math.PI * 2);
    ctx.fillStyle = '#fff'; ctx.fill();

    ctx.fillStyle = 'rgba(139,155,200,0.6)';
    ctx.font = '10px Inter'; ctx.textAlign = 'center';
    ctx.fillText(labels[i], pt.x, h - pad.bottom + 14);
  });
}

function drawCategoryChart() {
  const canvas = document.getElementById('categoryChart');
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth || 340;
  canvas.height = 200;

  const labels = categoriesData.map(c => c.name.substring(0, 8)) || ['Electronics', 'Health', 'Home', 'Sports', 'Toys', 'Auto'];
  const data = categoriesData.map(c => c.count) || [30, 25, 18, 12, 9, 6];
  const colors = ['#8b5cf6', '#06b6d4', '#f97316', '#10b981', '#f59e0b', '#ef4444', '#6366f1', '#ec4899'];
  const w = canvas.width, h = canvas.height;
  const cx = w / 2, cy = h / 2 - 10, r = Math.min(cx, cy) - 20;

  ctx.clearRect(0, 0, w, h);
  const total = data.reduce((a, b) => a + b, 0);
  let startAngle = -Math.PI / 2;

  data.forEach((val, i) => {
    const angle = (val / (total || 1)) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, r, startAngle, startAngle + angle);
    ctx.closePath();
    ctx.fillStyle = colors[i % colors.length]; ctx.fill();

    // Donut hole
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2);
    ctx.fillStyle = '#111928'; ctx.fill();

    startAngle += angle;
  });

  // Center text
  ctx.fillStyle = '#f0f4ff'; ctx.font = 'bold 18px Inter'; ctx.textAlign = 'center';
  ctx.fillText(data.length, cx, cy + 4);
  ctx.fillStyle = 'rgba(139,155,200,0.7)'; ctx.font = '10px Inter';
  ctx.fillText('Categories', cx, cy + 18);

  // Legend
  const legX = 10, legY = h - 34;
  labels.forEach((l, i) => {
    const x = legX + (i % 3) * 110;
    const y = legY + Math.floor(i / 3) * 16;
    ctx.fillStyle = colors[i];
    ctx.fillRect(x, y, 8, 8);
    ctx.fillStyle = 'rgba(139,155,200,0.7)'; ctx.font = '9px Inter';
    ctx.textAlign = 'left';
    ctx.fillText(l, x + 12, y + 8);
  });
}

function drawPriceChart() {
  const canvas = document.getElementById('priceChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth || 400;
  canvas.height = 250;

  const months = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'];
  const series = [
    { label: 'Electronics', color: '#8b5cf6', data: [120, 125, 118, 140, 155, 148, 160, 165] },
    { label: 'Sports', color: '#06b6d4', data: [45, 48, 44, 52, 55, 50, 58, 62] },
    { label: 'Health', color: '#10b981', data: [60, 58, 65, 72, 68, 75, 78, 82] },
  ];

  const w = canvas.width, h = canvas.height;
  const pad = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartW = w - pad.left - pad.right;
  const chartH = h - pad.top - pad.bottom;

  const allVals = series.flatMap(s => s.data);
  const minVal = Math.min(...allVals) * 0.9, maxVal = Math.max(...allVals) * 1.1;

  ctx.clearRect(0, 0, w, h);

  // Grid
  ctx.strokeStyle = 'rgba(255,255,255,0.05)'; ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + (chartH / 4) * i;
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(w - pad.right, y); ctx.stroke();
    ctx.fillStyle = 'rgba(139,155,200,0.5)'; ctx.font = '10px Inter'; ctx.textAlign = 'right';
    ctx.fillText('$' + Math.round(maxVal - (maxVal - minVal) / 4 * i), pad.left - 6, y + 4);
  }

  series.forEach(s => {
    const pts = s.data.map((v, i) => ({
      x: pad.left + (chartW / (s.data.length - 1)) * i,
      y: pad.top + chartH * (1 - (v - minVal) / (maxVal - minVal))
    }));
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < pts.length; i++) {
      const cpX = (pts[i - 1].x + pts[i].x) / 2;
      ctx.bezierCurveTo(cpX, pts[i - 1].y, cpX, pts[i].y, pts[i].x, pts[i].y);
    }
    ctx.strokeStyle = s.color; ctx.lineWidth = 2; ctx.stroke();
    pts.forEach(pt => {
      ctx.beginPath(); ctx.arc(pt.x, pt.y, 3, 0, Math.PI * 2);
      ctx.fillStyle = s.color; ctx.fill();
    });
  });

  // X labels
  months.forEach((m, i) => {
    const x = pad.left + (chartW / (months.length - 1)) * i;
    ctx.fillStyle = 'rgba(139,155,200,0.5)'; ctx.font = '10px Inter'; ctx.textAlign = 'center';
    ctx.fillText(m, x, h - pad.bottom + 14);
  });

  // Legend
  series.forEach((s, i) => {
    const x = pad.left + i * 100;
    ctx.fillStyle = s.color; ctx.fillRect(x, h - 8, 12, 3);
    ctx.fillStyle = 'rgba(139,155,200,0.7)'; ctx.font = '9px Inter'; ctx.textAlign = 'left';
    ctx.fillText(s.label, x + 16, h - 4);
  });
}

document.querySelectorAll('.chart-tab').forEach(tab => {
  tab.addEventListener('click', function () {
    document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
    this.classList.add('active');
    setTimeout(drawActivityChart, 0);
  });
});

// =========== PRODUCT CARDS ===========
function productCardHTML(p, compact = false) {
  const scoreClass = p.score >= 90 ? 'score-high' : p.score >= 80 ? 'score-mid' : 'score-low';
  const tags = Array.isArray(p.tags) ? p.tags : [];
  const badgesHTML = tags.map(t => `<span class="badge-tag badge-${t}">${t}</span>`).join('');
  const starsHTML = '★'.repeat(Math.floor(p.rating)) + (p.rating % 1 >= 0.5 ? '½' : '');
  const inWatch = watchlist.has(p.id);
  const origPrice = p.originalPrice || p.original_price;

  return `
    <div class="product-card" data-id="${p.id}" id="card-${p.id}">
      <div class="product-img-wrap">
        <span class="product-emoji">${p.emoji}</span>
        <div class="product-badges">${badgesHTML}</div>
        <span class="scout-score ${scoreClass}">⚡ ${p.score}</span>
        <button class="watchlist-btn ${inWatch ? 'active' : ''}" data-id="${p.id}" title="${inWatch ? 'Remove from watchlist' : 'Add to watchlist'}">
          ${inWatch ? '★' : '☆'}
        </button>
      </div>
      <div class="product-body">
        <div class="product-category">${p.category}</div>
        <div class="product-name">${p.name}</div>
        <div class="product-meta">
          <div class="product-price">
            $${p.price.toFixed(2)}
            ${origPrice ? `<span class="original">$${origPrice.toFixed(2)}</span>` : ''}
          </div>
          <div class="rating">
            <span class="stars">${starsHTML}</span>
            <span class="rating-val">${p.rating}</span>
          </div>
        </div>
        <div class="product-stats">
          <div class="stat"><span class="stat-val">${p.sales >= 1000 ? (p.sales / 1000).toFixed(1) + 'K' : p.sales}</span><span class="stat-key">Monthly Sales</span></div>
          <div class="stat"><span class="stat-val">${p.margin}%</span><span class="stat-key">Margin</span></div>
          <div class="stat"><span class="stat-val">${(p.demand || '').split(' ')[0]}</span><span class="stat-key">Demand</span></div>
        </div>
      </div>
    </div>`;
}

function attachProductCardEvents(container) {
  container.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('click', e => {
      if (e.target.closest('.watchlist-btn')) return;
      const id = parseInt(card.dataset.id);
      openProductModal(id);
    });
  });
  container.querySelectorAll('.watchlist-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      toggleWatchlist(parseInt(btn.dataset.id));
    });
  });
}

// =========== SCOUT PRODUCTS ===========
function renderScoutProducts() {
  filteredProducts = [...allProducts];
  displayedCount = 12;
  renderProductGrid();
}

function renderProductGrid() {
  const container = document.getElementById('scoutProducts');
  const slice = filteredProducts.slice(0, displayedCount);
  container.innerHTML = slice.map(p => productCardHTML(p)).join('');
  attachProductCardEvents(container);
  document.getElementById('resultsCount').innerHTML = `Showing <strong>${slice.length}</strong> of <strong>${filteredProducts.length}</strong> products`;
  document.getElementById('loadMoreBtn').style.display = filteredProducts.length > displayedCount ? 'block' : 'none';
}

document.getElementById('loadMoreBtn').addEventListener('click', () => {
  displayedCount += 8;
  renderProductGrid();
});

document.getElementById('applyFilters').addEventListener('click', applyFilters);
document.getElementById('scoutSearch').addEventListener('input', applyFilters);

function applyFilters() {
  const query = document.getElementById('scoutSearch').value.toLowerCase();
  const category = document.getElementById('filterCategory').value;
  const sortBy = document.getElementById('filterSort').value;
  const minScore = parseInt(document.getElementById('filterScore').value) || 0;

  filteredProducts = allProducts.filter(p => {
    const matchQ = !query || p.name.toLowerCase().includes(query) || p.category.toLowerCase().includes(query) || (p.brand || '').toLowerCase().includes(query);
    const matchCat = !category || p.category === category;
    const matchScore = p.score >= minScore;
    return matchQ && matchCat && matchScore;
  });

  filteredProducts.sort((a, b) => {
    switch (sortBy) {
      case 'price-low': return a.price - b.price;
      case 'price-high': return b.price - a.price;
      case 'rating': return b.rating - a.rating;
      case 'newest': return b.id - a.id;
      default: return b.score - a.score;
    }
  });

  displayedCount = 12;
  renderProductGrid();
}

// Grid / List view toggle
document.getElementById('gridViewBtn').addEventListener('click', () => {
  document.getElementById('scoutProducts').classList.remove('list-view');
  document.getElementById('gridViewBtn').classList.add('active');
  document.getElementById('listViewBtn').classList.remove('active');
});
document.getElementById('listViewBtn').addEventListener('click', () => {
  document.getElementById('scoutProducts').classList.add('list-view');
  document.getElementById('listViewBtn').classList.add('active');
  document.getElementById('gridViewBtn').classList.remove('active');
});

// =========== WATCHLIST (API-backed) ===========
async function toggleWatchlist(id) {
  if (watchlist.has(id)) {
    // Remove from watchlist via API
    try {
      await apiDelete(`/api/watchlist/${id}`);
      watchlist.delete(id);
      showToast('Removed from watchlist', 'info', '📌');
    } catch (err) {
      showToast('Failed to remove from watchlist', 'warning', '⚠️');
      return;
    }
  } else {
    // Add to watchlist via API
    try {
      await apiPost(`/api/watchlist/${id}`);
      watchlist.add(id);
      showToast('Added to watchlist!', 'success', '⭐');
    } catch (err) {
      showToast('Failed to add to watchlist', 'warning', '⚠️');
      return;
    }
  }
  updateWatchlistBadge();
  updateAllWatchlistBtns(id);
  if (currentSection === 'watchlist') renderWatchlist();
}

function updateAllWatchlistBtns(id) {
  document.querySelectorAll(`.watchlist-btn[data-id="${id}"]`).forEach(btn => {
    const inWatch = watchlist.has(id);
    btn.textContent = inWatch ? '★' : '☆';
    btn.classList.toggle('active', inWatch);
    btn.title = inWatch ? 'Remove from watchlist' : 'Add to watchlist';
  });
}

function updateWatchlistBadge() {
  document.getElementById('watchlistBadge').textContent = watchlist.size;
}

function renderWatchlist() {
  const container = document.getElementById('watchlistProducts');
  const empty = document.getElementById('watchlistEmpty');
  const items = allProducts.filter(p => watchlist.has(p.id));
  if (items.length === 0) {
    container.innerHTML = '';
    empty.style.display = 'flex';
  } else {
    empty.style.display = 'none';
    container.innerHTML = items.map(p => productCardHTML(p)).join('');
    attachProductCardEvents(container);
  }
}

// =========== COMPARE ===========
function renderCompare() {
  const watchItems = allProducts.filter(p => watchlist.has(p.id));
  const pool = document.getElementById('comparePool');
  const empty = document.getElementById('compareEmpty');
  const cardsWrap = document.getElementById('compareCardsWrap');
  const poolHeader = document.querySelector('.compare-pool-header');

  if (watchItems.length === 0) {
    pool.innerHTML = '';
    poolHeader.style.display = 'none';
    empty.style.display = 'flex';
    cardsWrap.style.display = 'none';
    return;
  }

  poolHeader.style.display = 'flex';
  empty.style.display = 'none';

  // Render pool chips
  pool.innerHTML = watchItems.map(p => {
    const sel = compareList.has(p.id);
    return `<div class="cpool-chip ${sel ? 'selected' : ''}" data-id="${p.id}">
      <span class="cpool-emoji">${p.emoji}</span>
      <span class="cpool-name">${p.name.substring(0, 30)}</span>
      <span class="cpool-check">${sel ? '✓' : '+'}</span>
    </div>`;
  }).join('');

  pool.querySelectorAll('.cpool-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const id = parseInt(chip.dataset.id);
      if (compareList.has(id)) {
        compareList.delete(id);
      } else if (compareList.size < 3) {
        compareList.add(id);
      } else {
        showToast('Max 3 products can be compared', 'warning', '⚠️');
        return;
      }
      renderCompare();
    });
  });

  buildVisualCompare();
}

function buildVisualCompare() {
  const selected = allProducts.filter(p => compareList.has(p.id));
  const cardsWrap = document.getElementById('compareCardsWrap');
  const header = document.getElementById('compareCardsHeader');
  const attrsEl = document.getElementById('compareAttrs');
  const recEl = document.getElementById('compareRecommendation');

  if (selected.length < 2) {
    cardsWrap.style.display = 'none';
    return;
  }
  cardsWrap.style.display = 'block';

  // --- Bests ---
  const bestScore = Math.max(...selected.map(p => p.score));
  const bestMargin = Math.max(...selected.map(p => p.margin));
  const bestSales = Math.max(...selected.map(p => p.sales));
  const bestRating = Math.max(...selected.map(p => p.rating));
  const bestReviews = Math.max(...selected.map(p => p.reviews));
  const minPrice = Math.min(...selected.map(p => p.price));

  // Accent colors per column
  const ACCENT = ['#8b5cf6', '#06b6d4', '#f97316'];

  // --- HEADER CARDS ---
  const discount = p => {
    const orig = p.originalPrice || p.original_price;
    return orig ? Math.round((1 - p.price / orig) * 100) : 0;
  };
  const scoreClass = s => s >= 90 ? 'compare-score-high' : s >= 80 ? 'compare-score-mid' : 'compare-score-low';

  header.innerHTML = `
    <div class="compare-attr-label-col"></div>
    ${selected.map((p, i) => {
      const orig = p.originalPrice || p.original_price;
      return `
      <div class="compare-product-col">
        <div class="compare-product-card" style="--col-accent:${ACCENT[i]}">
          ${p.score === bestScore ? '<div class="compare-crown" title="Top Score">👑</div>' : ''}
          <div class="compare-product-emoji">${p.emoji}</div>
          <div class="compare-product-meta">
            <div class="compare-product-cat">${p.category} · ${p.brand || ''}</div>
            <div class="compare-product-name">${p.name}</div>
            <div class="compare-product-price">
              $${p.price.toFixed(2)}
              ${orig ? `<span class="compare-product-orig">$${orig.toFixed(2)}</span>` : ''}
              ${discount(p) > 0 ? `<span class="compare-product-disc">-${discount(p)}%</span>` : ''}
            </div>
            <div class="compare-product-stars">${'★'.repeat(Math.floor(p.rating))}${p.rating % 1 >= 0.5 ? '½' : ''} <span>${p.rating}</span></div>
          </div>
          <div class="compare-score-pill ${scoreClass(p.score)}" style="border-color:${ACCENT[i]}20">
            ⚡ ${p.score} <small>Scout Score</small>
          </div>
          <button class="compare-remove-btn" data-id="${p.id}" title="Remove">✕</button>
        </div>
      </div>`;
    }).join('')}`;

  header.querySelectorAll('.compare-remove-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      compareList.delete(parseInt(btn.dataset.id));
      renderCompare();
    });
  });

  // --- ATTRIBUTE ROWS ---
  const attrs = [
    {
      label: 'Scout Score', icon: '⚡',
      getValue: p => p.score,
      format: p => `${p.score}`,
      getBar: p => (p.score / 100) * 100,
      isBest: p => p.score === bestScore,
    },
    {
      label: 'Price', icon: '💰',
      getValue: p => p.price,
      format: p => `$${p.price.toFixed(2)}`,
      getBar: p => ((Math.max(...selected.map(x => x.price)) - p.price) / Math.max(...selected.map(x => x.price))) * 100 + 20,
      isBest: p => p.price === minPrice,
    },
    {
      label: 'Monthly Sales', icon: '📦',
      getValue: p => p.sales,
      format: p => p.sales >= 1000 ? (p.sales / 1000).toFixed(1) + 'K' : p.sales,
      getBar: p => (p.sales / bestSales) * 100,
      isBest: p => p.sales === bestSales,
    },
    {
      label: 'Profit Margin', icon: '📈',
      getValue: p => p.margin,
      format: p => `${p.margin}%`,
      getBar: p => (p.margin / bestMargin) * 100,
      isBest: p => p.margin === bestMargin,
    },
    {
      label: 'Star Rating', icon: '⭐',
      getValue: p => p.rating,
      format: p => `${p.rating} / 5`,
      getBar: p => (p.rating / 5) * 100,
      isBest: p => p.rating === bestRating,
    },
    {
      label: 'Reviews', icon: '💬',
      getValue: p => p.reviews,
      format: p => p.reviews.toLocaleString(),
      getBar: p => (p.reviews / bestReviews) * 100,
      isBest: p => p.reviews === bestReviews,
    },
    {
      label: 'Demand Level', icon: '🔥',
      getValue: p => ['Low', 'Medium', 'High', 'Very High', 'Growing'].indexOf(p.demand),
      format: p => p.demand,
      getBar: p => {
        const map = { Low: 20, Medium: 40, High: 65, Growing: 55, 'Very High': 95 };
        return map[p.demand] || 50;
      },
      isBest: p => {
        const map = { Low: 0, Medium: 1, High: 2, Growing: 1.5, 'Very High': 3 };
        const maxD = Math.max(...selected.map(x => map[x.demand] || 0));
        return (map[p.demand] || 0) === maxD;
      },
    },
  ];

  attrsEl.innerHTML = `
    <div class="compare-attrs-grid" style="--col-count:${selected.length}">
      ${attrs.map(attr => `
        <div class="compare-attr-row">
          <div class="compare-attr-label">
            <span class="compare-attr-icon">${attr.icon}</span>
            <span>${attr.label}</span>
          </div>
          ${selected.map((p, i) => {
    const best = attr.isBest(p);
    const barPct = Math.min(100, Math.max(0, attr.getBar(p)));
    return `<div class="compare-attr-cell ${best ? 'best-cell' : ''}">
              <div class="compare-attr-value ${best ? 'best-value' : ''}">${attr.format(p)}${best ? ' <span class="best-badge">Best</span>' : ''}</div>
              <div class="compare-attr-bar-wrap">
                <div class="compare-attr-bar" style="width:${barPct}%; background:${ACCENT[i]}; animation-delay:${i * 0.1}s"></div>
              </div>
            </div>`;
  }).join('')}
        </div>`).join('')}
    </div>`;

  // --- RECOMMENDATION ---
  const maxScoreV = Math.max(...selected.map(p => p.score));
  const maxMarginV = Math.max(...selected.map(p => p.margin));
  const maxSalesV = Math.max(...selected.map(p => p.sales));
  const maxRatingV = Math.max(...selected.map(p => p.rating));

  const winScore = p =>
    (p.score / maxScoreV) * 40 +
    (p.margin / maxMarginV) * 25 +
    (p.sales / maxSalesV) * 20 +
    (p.rating / maxRatingV) * 15;

  const ranked = [...selected].sort((a, b) => winScore(b) - winScore(a));
  const winner = ranked[0];
  const ws = winScore(winner).toFixed(1);

  recEl.innerHTML = `
    <div class="compare-rec-card">
      <div class="compare-rec-badge">🏆 ScoutIQ Recommendation</div>
      <div class="compare-rec-body">
        <div class="compare-rec-winner">
          <span class="compare-rec-emoji">${winner.emoji}</span>
          <div>
            <div class="compare-rec-name">${winner.name}</div>
            <div class="compare-rec-reason">
              Highest composite score (<strong>${ws}/100</strong>) across scout score, margin, sales velocity, and rating metrics.
            </div>
          </div>
        </div>
        <div class="compare-rec-scores">
          ${ranked.map((p, i) => `
            <div class="compare-rec-score-row">
              <span class="compare-rec-rank">${['🥇', '🥈', '🥉'][i]}</span>
              <span class="compare-rec-rname">${p.name.substring(0, 30)}</span>
              <div class="compare-rec-bar-wrap">
                <div class="compare-rec-bar" style="width:${(winScore(p) / winScore(winner)) * 100}%"></div>
              </div>
              <span class="compare-rec-rval">${winScore(p).toFixed(1)}</span>
            </div>`).join('')}
        </div>
      </div>
    </div>`;
}

// =========== TRENDS (API-backed) ===========
function renderTrends() {
  // Categories
  const catContainer = document.getElementById('trendingCategories');
  catContainer.innerHTML = categoriesData.map((c, i) => `
    <div class="trend-item">
      <div class="trend-rank">${i + 1}</div>
      <div class="trend-info">
        <div class="trend-name">${c.icon} ${c.name}</div>
        <div class="trend-bar-wrap">
          <div class="trend-bar" style="width:${c.pct}%"></div>
        </div>
      </div>
      <span class="trend-pct">+${c.pct}%</span>
    </div>`).join('');

  // Geo
  const geoGrid = document.getElementById('geoGrid');
  geoGrid.innerHTML = geoData.map(g => `
    <div class="geo-card">
      <div class="geo-flag">${g.flag}</div>
      <div class="geo-name">${g.name}</div>
      <div class="geo-demand">${g.demand}</div>
      <div class="geo-bar"><div class="geo-fill" style="width:${g.pct}%"></div></div>
    </div>`).join('');

  // Brands
  const brandList = document.getElementById('brandList');
  brandList.innerHTML = brandsData.map(b => `
    <div class="brand-item">
      <div class="brand-logo">${b.logo}</div>
      <div>
        <div class="brand-name">${b.name}</div>
        <div class="brand-products">${b.products} products tracked</div>
      </div>
      <span class="brand-score">${b.score}</span>
    </div>`).join('');

  // Insights
  const insightsList = document.getElementById('insightsList');
  insightsList.innerHTML = insightsData.map(ins => `
    <div class="insight-item">
      <span class="insight-icon">${ins.icon}</span>
      <p class="insight-text">${ins.text}</p>
    </div>`).join('');

  setTimeout(drawPriceChart, 100);
}

// =========== ALERTS (API-backed) ===========
function renderAlerts() {
  const list = document.getElementById('alertsList');
  list.innerHTML = alertsData.map(a => {
    const desc = a.desc || a.description || '';
    const typeName = a.typeName || a.type_name || a.type;
    return `
    <div class="alert-item ${a.status === 'triggered' ? 'triggered' : 'active-alert'}">
      <div class="alert-icon ${a.type}">${a.icon}</div>
      <div class="alert-info">
        <div class="alert-product">${a.product}</div>
        <div class="alert-desc">${typeName} · ${desc}</div>
      </div>
      <span class="alert-status status-${a.status}">${a.status.charAt(0).toUpperCase() + a.status.slice(1)}</span>
      <div class="alert-actions">
        <button class="alert-action-btn" onclick="toggleAlertStatus(${a.id})">
          ${a.status === 'paused' ? 'Activate' : 'Pause'}
        </button>
        <button class="alert-action-btn btn-danger" onclick="deleteAlert(${a.id})">Delete</button>
      </div>
    </div>`;
  }).join('');
  updateAlertBadge();
}

function updateAlertBadge() {
  const badge = document.querySelector('.badge-alert');
  if (badge) {
    badge.textContent = alertsData.filter(a => a.status === 'active' || a.status === 'triggered').length;
  }
}

async function toggleAlertStatus(id) {
  try {
    await apiPatch(`/api/alerts/${id}`, {});
    // Refresh alerts from server
    alertsData = await apiGet('/api/alerts');
    renderAlerts();
    showToast('Alert status updated', 'info', '🔔');
  } catch (err) {
    // Fallback: toggle locally
    const alert = alertsData.find(a => a.id === id);
    if (!alert) return;
    alert.status = alert.status === 'paused' ? 'active' : 'paused';
    renderAlerts();
    showToast('Alert toggled (offline)', 'info', '🔔');
  }
}

async function deleteAlert(id) {
  try {
    await apiDelete(`/api/alerts/${id}`);
    alertsData = alertsData.filter(a => a.id !== id);
    renderAlerts();
    showToast('Alert deleted', 'info', '🗑️');
  } catch (err) {
    // Fallback: remove locally
    const idx = alertsData.findIndex(a => a.id === id);
    if (idx > -1) { alertsData.splice(idx, 1); renderAlerts(); }
    showToast('Alert deleted (offline)', 'info', '🗑️');
  }
}

document.getElementById('addAlertBtn').addEventListener('click', () => {
  document.getElementById('alertModal').classList.add('open');
});

document.getElementById('alertModalClose').addEventListener('click', () => {
  document.getElementById('alertModal').classList.remove('open');
});

document.getElementById('saveAlert').addEventListener('click', async () => {
  const product = document.getElementById('alertProduct').value.trim();
  const type = document.getElementById('alertType').value;
  const threshold = document.getElementById('alertThreshold').value;
  if (!product) { showToast('Please enter a product name', 'warning', '⚠️'); return; }

  const alertBody = {
    product,
    type,
    description: threshold ? `Threshold: $${threshold}` : 'Trend monitoring active',
  };

  try {
    const result = await apiPost('/api/alerts', alertBody);
    // Refresh alerts from server
    alertsData = await apiGet('/api/alerts');
    renderAlerts();
    showToast('Alert created!', 'success', '✅');
  } catch (err) {
    // Fallback: add locally
    const icons = { 'price-drop': '📉', 'price-rise': '📈', 'trend': '🔥', 'stock': '📦' };
    const names = { 'price-drop': 'Price Drop', 'price-rise': 'Price Rise', 'trend': 'Trend Alert', 'stock': 'Stock Alert' };
    alertsData.unshift({ id: Date.now(), product, type, typeName: names[type], desc: alertBody.description, status: 'active', icon: icons[type] });
    renderAlerts();
    showToast('Alert created (offline)', 'success', '✅');
  }

  document.getElementById('alertModal').classList.remove('open');
  document.getElementById('alertProduct').value = '';
  document.getElementById('alertThreshold').value = '';
});

// =========== MODAL ===========
function openProductModal(id) {
  const p = allProducts.find(p => p.id === id);
  if (!p) return;
  const inWatch = watchlist.has(id);
  const starsHTML = '★'.repeat(Math.floor(p.rating)) + (p.rating % 1 >= 0.5 ? '½' : '');
  const origPrice = p.originalPrice || p.original_price;
  const discount = origPrice ? Math.round((1 - p.price / origPrice) * 100) : 0;

  // Mock platform prices
  const platforms = [
    { name: 'Amazon', price: p.price, icon: '📦', link: '#' },
    { name: 'eBay', price: +(p.price * (1 + (Math.random() * 0.15 - 0.05))).toFixed(2), icon: '🏷️', link: '#' },
    { name: 'Walmart', price: +(p.price * (1 + (Math.random() * 0.1 - 0.05))).toFixed(2), icon: '🛒', link: '#' },
    { name: 'Target', price: +(p.price * (1 + (Math.random() * 0.12 - 0.04))).toFixed(2), icon: '🎯', link: '#' },
  ];

  platforms.sort((a, b) => a.price - b.price);

  document.getElementById('productModalContent').className = 'modal modal-lg detail-modal';
  document.getElementById('modalBody').innerHTML = `
    <div class="product-detail-layout">
      <!-- Left: Core Info -->
      <div class="detail-main">
        <div class="modal-product-header">
          <div class="modal-product-img">${p.emoji}</div>
          <div class="modal-product-info">
            <div class="modal-product-category">${p.category} · ${p.brand || ''}</div>
            <div class="modal-product-name">${p.name}</div>
            <div class="modal-product-price">
              $${p.price.toFixed(2)}
              ${origPrice ? `<span class="price-orig">$${origPrice.toFixed(2)}</span>` : ''}
              ${discount > 0 ? `<span class="badge-tag badge-deal" style="margin-left:8px;font-size:.75rem">-${discount}%</span>` : ''}
            </div>
            <div style="margin-top:8px">
              <span class="stars" style="font-size:1rem">${starsHTML}</span>
              <span style="color:var(--text-secondary);font-size:.85rem;margin-left:6px">${p.rating} · ${p.reviews.toLocaleString()} reviews</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h3>Description</h3>
          <div class="modal-product-desc">${p.description || 'No detailed description available for this product.'}</div>
        </div>

        <div class="detail-section">
          <h3>Market Stats</h3>
          <div class="modal-stats-grid">
            <div class="modal-stat"><div class="modal-stat-val">⚡ ${p.score}</div><div class="modal-stat-key">Scout Score</div></div>
            <div class="modal-stat"><div class="modal-stat-val">${p.sales >= 1000 ? (p.sales / 1000).toFixed(1) + 'K' : p.sales}</div><div class="modal-stat-key">Monthly Sales</div></div>
            <div class="modal-stat"><div class="modal-stat-val">${p.margin}%</div><div class="modal-stat-key">Profit Margin</div></div>
            <div class="modal-stat"><div class="modal-stat-val">${p.demand || 'High'}</div><div class="modal-stat-key">Demand level</div></div>
          </div>
        </div>

        <div class="detail-section">
          <h3>Price History (Last 30 Days)</h3>
          <div class="price-history-chart-wrap">
            <canvas id="modalPriceHistory" height="150"></canvas>
          </div>
        </div>
      </div>

      <!-- Right: Price Comparison & Actions -->
      <div class="detail-sidebar">
        <div class="sidebar-box">
          <h3>Price Comparison</h3>
          <div class="platform-list">
            ${platforms.map((plat, i) => `
              <div class="platform-item ${i === 0 ? 'platform-best' : ''}">
                <div class="plat-info">
                  <span class="plat-icon">${plat.icon}</span>
                  <span class="plat-name">${plat.name}</span>
                </div>
                <div class="plat-price">
                  $${plat.price.toFixed(2)}
                  ${i === 0 ? '<span class="best-plat-tag">LOWEST</span>' : ''}
                </div>
                <a href="${plat.link}" class="plat-link" onclick="event.stopPropagation()">View</a>
              </div>
            `).join('')}
          </div>
        </div>

        <div class="sidebar-box actions-box">
          <h3>Quick Actions</h3>
          <div class="modal-actions-vertical">
            <button class="btn btn-primary btn-full" id="modalWatchlistBtn" onclick="toggleWatchlist(${p.id}); updateModalWatchlistBtn(${p.id})">
              ${inWatch ? '★ Remove from Watchlist' : '☆ Add to Watchlist'}
            </button>
            <button class="btn btn-outline btn-full" onclick="navigateTo('compare'); compareList.add(${p.id}); hideModal();">⚖️ Add to Comparison</button>
            <button class="btn btn-outline btn-full" onclick="navigateTo('alerts'); hideModal();">🔔 Set Price Alert</button>
            <button class="btn btn-outline btn-full" onclick="hideModal()">Close Details</button>
          </div>
        </div>

        <div class="sidebar-box scout-insight">
          <div class="insight-header">
            <span class="insight-icon">💡</span>
            <h4>ScoutIQ Insight</h4>
          </div>
          <p>This product has <strong>${p.margin}% margin</strong> which is ${p.margin > 60 ? 'excellent' : 'above average'} for the <strong>${p.category}</strong> category. Recommended for immediate tracking.</p>
        </div>
      </div>
    </div>`;

  document.getElementById('productModal').classList.add('open');
  // Need to wait for DOM to render the canvas
  setTimeout(() => drawModalPriceHistory(p.price), 100);
}

function drawModalPriceHistory(basePrice) {
  const canvas = document.getElementById('modalPriceHistory');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.offsetWidth;
  const h = canvas.offsetHeight;
  canvas.width = w;
  canvas.height = h;

  const data = [];
  for (let i = 0; i < 30; i++) {
    const drift = (Math.random() - 0.51) * (basePrice * 0.08); // Slight downward trend for some excitement
    data.push(basePrice + drift);
  }
  data.push(basePrice); // Today

  const max = Math.max(...data) * 1.05;
  const min = Math.min(...data) * 0.95;
  const range = max - min;

  ctx.clearRect(0, 0, w, h);

  // Gradient
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, 'rgba(139, 92, 246, 0.4)');
  grad.addColorStop(1, 'rgba(139, 92, 246, 0)');

  ctx.beginPath();
  ctx.moveTo(0, h);
  data.forEach((val, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((val - min) / range) * h;
    ctx.lineTo(x, y);
  });
  ctx.lineTo(w, h);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Line
  ctx.beginPath();
  ctx.strokeStyle = '#8b5cf6';
  ctx.lineWidth = 3;
  ctx.lineJoin = 'round';
  data.forEach((val, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((val - min) / range) * h;
    if (i === 0) ctx.moveTo(x, y);
    else {
      const prevX = ((i - 1) / (data.length - 1)) * w;
      const prevY = h - ((data[i - 1] - min) / range) * h;
      const cpX = (prevX + x) / 2;
      ctx.bezierCurveTo(cpX, prevY, cpX, y, x, y);
    }
  });
  ctx.stroke();

  // Highlight points
  ctx.fillStyle = '#8b5cf6';
  [0, 15, 30].forEach(idx => {
    if (idx >= data.length) return;
    const val = data[idx];
    const x = (idx / (data.length - 1)) * w;
    const y = h - ((val - min) / range) * h;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.8)';
    ctx.lineWidth = 2;
    ctx.stroke();
  });
}

function hideModal() {
  const modal = document.getElementById('productModal');
  if (modal) modal.classList.remove('open');
}


function updateModalWatchlistBtn(id) {
  const btn = document.getElementById('modalWatchlistBtn');
  if (!btn) return;
  const inWatch = watchlist.has(id);
  btn.textContent = inWatch ? '★ Remove from Watchlist' : '☆ Add to Watchlist';
}

function initModals() {
  document.getElementById('modalClose').addEventListener('click', () => {
    document.getElementById('productModal').classList.remove('open');
  });
  document.getElementById('productModal').addEventListener('click', e => {
    if (e.target === document.getElementById('productModal')) {
      document.getElementById('productModal').classList.remove('open');
    }
  });
  document.getElementById('alertModal').addEventListener('click', e => {
    if (e.target === document.getElementById('alertModal')) {
      document.getElementById('alertModal').classList.remove('open');
    }
  });
}

// =========== SEARCH ===========
function initSearch() {
  document.getElementById('globalSearch').addEventListener('input', function () {
    const q = this.value.toLowerCase();
    if (!q) return;
    navigateTo('scout');
    document.getElementById('scoutSearch').value = this.value;
    applyFilters();
  });
}

// =========== TOAST ===========
function createToastContainer() {
  const div = document.createElement('div');
  div.className = 'toast-container';
  div.id = 'toastContainer';
  document.body.appendChild(div);
}

function showToast(msg, type = 'info', icon = 'ℹ️') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-msg">${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; toast.style.transition = 'all .3s ease'; setTimeout(() => toast.remove(), 300); }, 2500);
}

// =========== RESIZE ===========
window.addEventListener('resize', () => {
  if (currentSection === 'dashboard') { drawActivityChart(); drawCategoryChart(); }
  if (currentSection === 'trends') drawPriceChart();
});

// =========== LIVE TICKER ===========
function initTicker() {
  const track = document.getElementById('tickerTrack');
  if (!track) return;

  const topProducts = [...allProducts].sort((a, b) => b.score - a.score).slice(0, 10);
  if (topProducts.length === 0) return;

  function buildTickerHTML(products) {
    return products.map(p => {
      const change = ((Math.random() * 6) - 2).toFixed(1);
      const up = parseFloat(change) >= 0;
      return `<div class="ticker-item">
        <span>${p.emoji}</span>
        <span class="ticker-name">${p.name.substring(0, 28)}</span>
        <span class="ticker-price">$${p.price.toFixed(2)}</span>
        <span class="ticker-${up ? 'up' : 'down'}">${up ? '▲' : '▼'} ${Math.abs(change)}%</span>
        <span style="color:var(--purple-light);font-size:.7rem">⚡${p.score}</span>
      </div>`;
    }).join('');
  }

  // Duplicate for seamless loop
  const html = buildTickerHTML(topProducts);
  track.innerHTML = html + html;

  // Randomly flicker a price every 4s for "live" feel
  setInterval(() => {
    const items = track.querySelectorAll('.ticker-price');
    if (items.length === 0) return;
    const idx = Math.floor(Math.random() * Math.min(topProducts.length, items.length));
    const oldVal = parseFloat(items[idx].textContent.replace('$', ''));
    const delta = ((Math.random() * 2) - 1) * 0.5;
    const newVal = Math.max(0, oldVal + delta);
    items[idx].textContent = '$' + newVal.toFixed(2);
    items[idx].style.transition = 'color 0.3s';
    items[idx].style.color = delta >= 0 ? 'var(--green-light)' : '#f87171';
    setTimeout(() => { items[idx].style.color = 'var(--cyan-light)'; }, 800);
  }, 4000);
}
