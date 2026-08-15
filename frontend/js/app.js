// State Management
let currentMode = 'search'; // 'search' atau 'recommend'

const API_BASE = "http://127.0.0.1:8000";

function switchTab(mode) {
    currentMode = mode;
    const tabSearch = document.getElementById('tabSearch');
    const tabRecommend = document.getElementById('tabRecommend');
    const formLabel = document.getElementById('formLabel');
    const submitBtn = document.getElementById('submitBtn');
    const aiBox = document.getElementById('aiBox');

    // Clear previous results
    document.getElementById('resultsGrid').innerHTML = '';
    document.getElementById('resultCount').textContent = '';
    aiBox.classList.add('hidden');

    if (mode === 'search') {
        // Gaya Segmented Control Luxury Editorial
        tabSearch.className = "px-5 py-2 rounded-lg font-medium text-xs transition-all bg-[#1A1A1A] text-white shadow-sm";
        tabRecommend.className = "px-5 py-2 rounded-lg font-medium text-xs transition-all text-[#666666] hover:text-[#1A1A1A]";
        formLabel.textContent = "Ketik kueri pencarian parfum impianmu:";
        submitBtn.innerHTML = "<span>Cari Parfum</span><span>✦</span>";
    } else {
        tabRecommend.className = "px-5 py-2 rounded-lg font-medium text-xs transition-all bg-[#1A1A1A] text-white shadow-sm";
        tabSearch.className = "px-5 py-2 rounded-lg font-medium text-xs transition-all text-[#666666] hover:text-[#1A1A1A]";
        formLabel.textContent = "Ceritakan kebutuhan & vibe parfum yang kamu cari ke AI Consultant:";
        submitBtn.innerHTML = "<span>Minta Rekomendasi AI</span><span>✦</span>";
    }
}

async function handleSubmit(event) {
    event.preventDefault();
    const query = document.getElementById('queryInput').value.trim();
    const limit = parseInt(document.getElementById('limitSelect').value);
    
    if (!query) return;

    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorBanner = document.getElementById('errorBanner');
    const resultsGrid = document.getElementById('resultsGrid');
    const resultCount = document.getElementById('resultCount');
    const aiBox = document.getElementById('aiBox');
    const aiTextContent = document.getElementById('aiTextContent');

    // Reset UI state
    loadingIndicator.classList.remove('hidden');
    errorBanner.classList.add('hidden');
    errorBanner.textContent = '';
    resultsGrid.innerHTML = '';
    resultCount.textContent = '';
    aiBox.classList.add('hidden');

    try {
        let endpoint = currentMode === 'search' ? `${API_BASE}/search` : `${API_BASE}/recommend`;
        
        let response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ query, limit })
        });

        if (!response.ok) {
            throw new Error(`Gagal menghubungi server API (HTTP ${response.status})`);
        }

        let data = await response.json();
        loadingIndicator.classList.add('hidden');

        if (currentMode === 'search') {
            renderSearchResults(data);
        } else {
            renderRecommendResults(data);
        }

    } catch (err) {
        loadingIndicator.classList.add('hidden');
        errorBanner.textContent = `Error: ${err.message}. Pastikan server FastAPI di terminal sudah menyala!`;
        errorBanner.classList.remove('hidden');
    }
}

function renderSearchResults(data) {
    const resultsGrid = document.getElementById('resultsGrid');
    const resultCount = document.getElementById('resultCount');
    
    resultCount.textContent = `Ditemukan ${data.total_results} produk`;

    if (!data.results || data.results.length === 0) {
        resultsGrid.innerHTML = `<p class="text-[#777777] text-xs col-span-2 text-center py-12 font-light">Tidak ada produk yang cocok dengan kueri tersebut.</p>`;
        return;
    }

    data.results.forEach(product => {
        resultsGrid.appendChild(createProductCard(product));
    });
}

function renderRecommendResults(data) {
    const resultsGrid = document.getElementById('resultsGrid');
    const resultCount = document.getElementById('resultCount');
    const aiBox = document.getElementById('aiBox');
    const aiTextContent = document.getElementById('aiTextContent');

    // Tampilkan ulasan AI
    aiTextContent.textContent = data.ai_recommendation;
    aiBox.classList.remove('hidden');

    const products = data.retrieved_products || [];
    resultCount.textContent = `Analisis berdasarkan ${products.length} produk teratas`;

    if (products.length === 0) {
        resultsGrid.innerHTML = `<p class="text-[#777777] text-xs col-span-2 text-center py-12 font-light">Tidak ada produk referensi.</p>`;
        return;
    }

    products.forEach(product => {
        resultsGrid.appendChild(createProductCard(product));
    });
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = "bg-white border border-[#EAE6DF] rounded-2xl p-6 flex flex-col justify-between hover:border-[#D4AF37] transition-all shadow-xs";

    const similarityPercent = (product.similarity * 100).toFixed(1);
    const formattedPrice = product.price ? `IDR ${product.price.toLocaleString('id-ID')}` : 'Harga tidak tersedia';

    card.innerHTML = `
        <div>
            <div class="flex items-start justify-between gap-3 mb-3">
                <h3 class="font-editorial font-medium text-[#1A1A1A] text-lg leading-snug">${product.product_name}</h3>
                <span class="text-[11px] font-medium px-2.5 py-1 rounded-full bg-[#EBF4EC] text-[#2D6A4F] border border-[#D8EAD9] whitespace-nowrap">
                    ${similarityPercent}% Match
                </span>
            </div>
            <p class="text-[#1A1A1A] font-semibold text-sm tracking-wide mb-4">${formattedPrice}</p>
        </div>
        
        <div class="pt-4 border-t border-[#F0ECE4] flex items-center justify-between text-xs">
            <span class="text-[10px] text-[#888888] uppercase tracking-widest font-medium">Official Product</span>
            <a href="${product.source_url}" target="_blank" class="font-medium text-[#1A1A1A] hover:text-[#D4AF37] flex items-center space-x-1 transition-colors underline underline-offset-4">
                <span>Kunjungi Toko</span>
                <span>↗</span>
            </a>
        </div>
    `;

    return card;
}