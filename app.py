import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import urllib.parse
import textwrap

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Agora Esportes",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS DEFINITIVO ---
st.markdown("""
<style>
    .block-container { padding-top: 3rem !important; padding-bottom: 5rem; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; }
    a { text-decoration: none !important; color: inherit !important; }
    .header-container { border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 15px; margin-bottom: 30px; display: flex; align-items: center; }
    .brand-icon { font-size: 2.2rem; margin-right: 15px; }
    
    .brand-name { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; }

    @media (prefers-color-scheme: light) {
        .brand-name { background: linear-gradient(90deg, #1976D2, #64B5F6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .news-card, .loto-row { background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important; }
        .news-title, .loto-name { color: #212529 !important;
        }
    }
    @media (prefers-color-scheme: dark) {
        .brand-name { background: none;
        -webkit-text-fill-color: #ffffff; color: #ffffff; }
        .news-card, .loto-row { background-color: #262730 !important;
        border: 1px solid #444 !important; }
        .news-title, .loto-name { color: #ffffff !important;
        }
    }

    /* ESTILIZAÇÃO DAS ABAS (TABS) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px;
        border-bottom: 1px solid rgba(128,128,128,0.1); 
        margin-bottom: 25px;
    }
    
    .stTabs [data-baseweb="tab"] { 
        height: 40px;
        border-radius: 20px; 
        font-weight: 600; 
        font-size: 13px; 
        padding: 0 20px;
        transition: all 0.3s ease; 
        opacity: 0.7;
    }
    
    .stTabs [aria-selected="true"] { 
        background-color: #1976D2 !important;
        color: white !important;
        opacity: 1; 
        box-shadow: 0 4px 6px rgba(25, 118, 210, 0.3);
    }

    /* --- REMOÇÃO DA BARRA VERMELHA (Highlight) --- */
    div[data-baseweb="tab-highlight"] {
        display: none !important;
    }
    /* --------------------------------------------- */

    .news-card { 
        border-radius: 10px;
        padding: 18px;
        height: 210px; 
        border-left: 4px solid #1976D2 !important; 
        transition: transform 0.2s; 
        display: flex; 
        flex-direction: column; 
        justify-content: space-between; 
        margin-bottom: 24px;
    }
    .news-card:hover { transform: translateY(-2px); border-color: #42A5F5 !important; }
    .news-source { font-size: 10px;
    font-weight: 800; color: #1976D2; text-transform: uppercase; margin-bottom: 8px; }
    .news-title { font-size: 15px; font-weight: 700; line-height: 1.35;
    display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
    .news-footer { font-size: 11px; opacity: 0.6; display: flex;
    align-items: center; justify-content: space-between; border-top: 1px solid rgba(128,128,128,0.1); padding-top: 10px; }

    .loto-row { border-radius: 10px; padding: 15px;
    margin-bottom: 15px; position: relative; transition: transform 0.2s; }
    .loto-row:hover { transform: scale(1.02);
    }
    .loto-name { font-weight: 800; font-size: 12px; text-transform: uppercase; }
    .loto-acumulou { position: absolute;
    top: 12px; right: 12px; background: #FBC02D; color: #000; font-size: 9px; font-weight: 800; padding: 3px 8px; border-radius: 4px;
    }
    .ball { width: 28px; height: 28px; background: #37474F; color: #fff; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 11px; font-weight: bold; }
    .loto-val { font-size: 16px; font-weight: 800; color: #388E3C;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="header-container">
    <div class="brand-icon">🏆</div>
    <div class="brand-name">Agora Esportes</div>
</div>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
@st.cache_data(ttl=300)
def get_news_sorted(query_terms):
    query_str = " OR ".join([f'"{q}"' for q in query_terms])
    encoded_query = urllib.parse.quote(query_str)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    try:
        response = requests.get(rss_url, timeout=10)
        feed = feedparser.parse(response.content)
        news_list = []
        for entry in feed.entries[:60]:
            title_clean = entry.title.split(" - ")[0]
            source = entry.source.title if hasattr(entry, 'source') else "Notícia"
            pub_dt_utc = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.utcnow()
            now_utc = datetime.utcnow()
            pub_br = pub_dt_utc - timedelta(hours=3)
            delta = now_utc - pub_dt_utc
            diff_days = (datetime.now().date() - pub_br.date()).days
            
            display_time = pub_br.strftime("%d/%m")
            if diff_days == 0:
                if delta.total_seconds() < 3600: display_time = f"Há {int(delta.total_seconds()/60)} min"
                else: display_time = pub_br.strftime("%H:%M")
            
            news_list.append({"title": title_clean, "link": entry.link, "source": source, "display_time": display_time, "date_sort": pub_dt_utc})
        news_list.sort(key=lambda x: x['date_sort'], reverse=True)
        return news_list
    except: return []

@st.cache_data(ttl=1800)
def get_loterias():
    # Mapeamento exato dos slugs da API para as URLs da Caixa
    games = [
        ("megasena", "Mega-Sena", "mega-sena"), 
        ("lotofacil", "Lotofácil", "lotofacil"), 
        ("quina", "Quina", "quina"),
        ("lotomania", "Lotomania", "lotomania"), 
        ("timemania", "Timemania", "timemania"), 
        ("duplasena", "Dupla Sena", "dupla-sena"),
        ("maismilionaria", "+Milionária", "mais-milionaria"), 
        ("diadesorte", "Dia de Sorte", "dia-de-sorte"), 
        ("supersete", "Super Sete", "super-sete")
    ]
    results = []
    for slug_api, name_display, slug_url in games:
        try:
            r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{slug_api}/latest", timeout=3)
            if r.status_code == 200:
                d = r.json()
                results.append({
                    "name": name_display, 
                    "concurso": d.get('concurso', 'N/A'),
                    "data_prox": d.get('dataProximoConcurso', 'A definir'),
                    "dezenas": d.get('dezenas', []), 
                    "acumulou": d.get('acumulou', False), 
                    "premio": d.get('valorEstimadoProximoConcurso', 0), 
                    "url": f"https://loterias.caixa.gov.br/Paginas/{slug_url}.aspx"
                })
        except: continue
    return results

def format_money(v): return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if v else "Aguardando"

# --- LAYOUT PRINCIPAL ---
col_main, col_side = st.columns([0.75, 0.25], gap="medium")

with col_main:
    tab1, tab2, tab3 = st.tabs(["Rio Grande do Sul", "Brasil", "Mundo"])

    def render_grid(query_list, msg):
        data = get_news_sorted(query_list)
        if not data: 
            st.info(msg)
            return
        cols = st.columns(3, gap="medium")
        for idx, item in enumerate(data[:18]):
            with cols[idx % 3]:
                st.markdown(f"""
                <a href="{item['link']}" target="_blank">
                    <div class="news-card">
                        <div>
                            <div class="news-source">{item['source']}</div>
                            <div class="news-title">{item['title']}</div>
                        </div>
                        <div class="news-footer">
                            <span>🕒 {item['display_time']}</span>
                            <span style="font-weight:bold; font-size:18px; color:#1976D2;">›</span>
                        </div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

    with tab1:
        # RS: Filtros específicos "EC Juventude" e "SER Caxias" para evitar notícias de saúde/obituários
        render_grid(["Esportes RS", "Grêmio", "Internacional RS", "EC Juventude", "SER Caxias", "Gauchão", "Futsal RS", "Basquete RS"], "Buscando esportes no RS...")
    with tab2:
        # BRASIL: Adicionados Libertadores, Sul-Americana, F1, Vôlei
        render_grid(["Brasileirão", "Copa do Brasil", "Libertadores", "Sul-Americana", "Seleção Brasileira", "Vôlei Brasil", "F1 Brasil", "UFC Brasil"], "Buscando esportes no Brasil...")
    with tab3:
        # MUNDO: Adicionados Europa League, Conference, Ligue 1, Camp. Português
        render_grid([
            "Champions League", "Europa League", "Conference League", 
            "Premier League", "La Liga", "Serie A Italiana", 
            "Ligue 1", "Campeonato Português", 
            "NBA", "NFL, Budesliga"
        ], "Buscando esportes no Mundo...")

with col_side:
    st.markdown("##### 🎱 Loterias Caixa")
    lotos = get_loterias()
    if not lotos: st.caption("Carregando resultados...")
    for loto in lotos:
        badge = '<div class="loto-acumulou">ACUMULOU</div>' if loto['acumulou'] else ''
        display_balls = loto['dezenas'][:20]
        balls_html = "".join([f'<div class="ball">{n}</div>' for n in display_balls])
        
        # USO DE TEXTWRAP PARA CORRIGIR RENDERIZAÇÃO E EVITAR BLOCO DE CÓDIGO
        html_loto = textwrap.dedent(f"""
            <a href="{loto['url']}" target="_blank">
            <div class="loto-row">
            {badge}
            <div class="loto-name">{loto['name']} <span style="font-weight:400; opacity:0.6; margin-left:4px; text-transform: none;">Conc. {loto['concurso']}</span></div>
            <div style="display:flex; flex-wrap:wrap; gap:4px; margin:8px 0;">{balls_html}</div>
            <div style="font-size:10px; opacity:0.7; margin-top:5px">Próximo: <b>{loto['data_prox']}</b></div>
            <div class="loto-val">{format_money(loto['premio'])}</div>
            </div>
            </a>
        """).strip()
        
        st.markdown(html_loto, unsafe_allow_html=True)