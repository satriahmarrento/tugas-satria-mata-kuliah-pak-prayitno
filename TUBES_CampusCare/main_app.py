from datetime import datetime
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

from konfigurasi import (
    PERAN_MAHASISWA,
    PERAN_PETUGAS,
    STATUS_BARU,
    STATUS_DIPROSES,
    STATUS_SELESAI,
)
from database import Database
from manajer_laporan import ManajerLaporan
from model import Mahasiswa, Petugas, NotifikasiToast


UPLOAD_DIR = Path(__file__).parent / "uploads"
DAFTAR_STATUS = [STATUS_BARU, STATUS_DIPROSES, STATUS_SELESAI]

# ─── Lumina Nexus Design System (Light Mode) ─────────────
COLORS = {
    STATUS_BARU: {"bg": "#4f46e5", "light": "#e0e7ff", "icon": "📋"},
    STATUS_DIPROSES: {"bg": "#f59e0b", "light": "#fef3c7", "icon": "🔧"},
    STATUS_SELESAI: {"bg": "#10b981", "light": "#d1fae5", "icon": "✅"},
}
ACCENT = "#4f46e5"
ACCENT_SECONDARY = "#9333ea"
ACCENT_TERTIARY = "#0ea5e9"
BG_LIGHT = "#f8fafc"
SURFACE = "#ffffff"
ON_SURFACE = "#1e293b"
ON_SURFACE_VARIANT = "#475569"
OUTLINE = "#cbd5e1"
CARD_BG = "rgba(255, 255, 255, 0.7)"
CARD_BORDER = "rgba(0, 0, 0, 0.05)"


def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ─────────────────────────────── */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
    }

    /* ── Ambient Glow Background ────────────── */
    .stApp::before {
        content: '';
        position: fixed;
        top: -100px; left: -100px;
        width: 600px; height: 600px;
        background: radial-gradient(circle, rgba(79, 70, 229, 0.1) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
        filter: blur(80px);
        z-index: 0;
        animation: pulse 15s infinite alternate;
        pointer-events: none;
    }
    .stApp::after {
        content: '';
        position: fixed;
        bottom: -200px; right: -100px;
        width: 600px; height: 600px;
        background: radial-gradient(circle, rgba(147, 51, 234, 0.08) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
        filter: blur(80px);
        z-index: 0;
        animation: pulse 15s infinite alternate-reverse;
        pointer-events: none;
    }
    @keyframes pulse {
        0% { transform: translate(-10%, -10%) scale(1); }
        100% { transform: translate(10%, 10%) scale(1.1); }
    }

    /* ── Sidebar ────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%) !important;
        border-right: 1px solid rgba(0, 0, 0, 0.05);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #1e293b !important;
    }

    /* ── Tabs ───────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding: 4px;
        background: rgba(241, 245, 249, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        color: #64748b !important;
        transition: all 0.3s cubic-bezier(.4,0,.2,1);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5, #9333ea) !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.25);
    }

    /* ── Buttons ────────────────────────────── */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
        background: linear-gradient(45deg, #4f46e5, #9333ea) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2) !important;
    }
    .stButton > button:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.3) !important;
    }

    /* ── Forms ──────────────────────────────── */
    .stForm {
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.05),
                    inset 0 1px 1px rgba(255,255,255,0.5) !important;
    }

    /* ── Inputs ─────────────────────────────── */
    .stTextInput input, .stTextArea textarea, .stSelectbox > div {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        color: #1e293b !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox > div:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
    }

    /* ── Metric Card ───────────────────────── */
    .metric-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-radius: 16px;
        padding: 20px 18px;
        text-align: center;
        transition: all 0.3s cubic-bezier(.4,0,.2,1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03),
                    inset 0 1px 1px rgba(255,255,255,0.8);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-color), transparent);
        border-radius: 16px 16px 0 0;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(79, 70, 229, 0.1),
                    inset 0 1px 1px rgba(255,255,255,0.9);
        border-color: rgba(79, 70, 229, 0.2);
    }
    .metric-icon { font-size: 28px; margin-bottom: 6px; }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 12px;
        color: #64748b;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* ── Report Card ───────────────────────── */
    .report-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: all 0.3s cubic-bezier(.4,0,.2,1);
        box-shadow: 0 2px 8px rgba(0,0,0,0.02), inset 0 1px 1px rgba(255,255,255,0.8);
    }
    .report-card:hover {
        border-color: rgba(79, 70, 229, 0.2);
        box-shadow: 0 8px 24px rgba(0,0,0,0.06),
                    inset 0 0 15px rgba(79, 70, 229, 0.02);
        transform: translateX(4px);
    }
    .report-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .report-id {
        font-size: 12px;
        color: #4f46e5;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .report-date {
        font-size: 12px;
        color: #94a3b8;
    }
    .report-location {
        font-size: 16px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 4px;
    }
    .report-desc {
        font-size: 14px;
        color: #475569;
        line-height: 1.5;
    }
    .report-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
    }
    .report-user {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
    }

    /* ── Status Badge ──────────────────────── */
    .status-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.03em;
    }

    /* ── Rating Stars ──────────────────────── */
    .star-rating { font-size: 16px; letter-spacing: 2px; }

    /* ── Login Page ─────────────────────────── */
    .login-header {
        text-align: center;
        padding: 30px 0 10px 0;
    }
    .login-header h1 {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .login-header p {
        color: #64748b;
        font-size: 16px;
        font-weight: 500;
    }

    /* ── Section Title ─────────────────────── */
    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: #1e293b;
        margin: 20px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.01em;
    }
    .section-title .icon {
        font-size: 22px;
    }

    /* ── Sidebar Avatar ────────────────────── */
    .sidebar-avatar {
        width: 48px; height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, #4f46e5, #9333ea);
        display: flex; align-items: center; justify-content: center;
        font-size: 22px; font-weight: 700; color: white;
        margin-right: 12px;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.25);
    }
    .sidebar-user-info {
        display: flex;
        align-items: center;
        padding: 12px 0;
        margin-bottom: 8px;
    }
    .sidebar-user-name {
        font-size: 15px;
        font-weight: 600;
        color: #1e293b;
    }
    .sidebar-user-role {
        font-size: 12px;
        color: #4f46e5;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ── Notification ──────────────────────── */
    .notif-item {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 8px;
        font-size: 13px;
        color: #475569;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .notif-item:hover {
        border-color: rgba(79, 70, 229, 0.2);
        box-shadow: 0 4px 8px rgba(79, 70, 229, 0.05);
    }
    .notif-time {
        font-size: 11px;
        color: #94a3b8;
        margin-bottom: 2px;
    }

    /* ── Empty State ───────────────────────── */
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #94a3b8;
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 12px; color: #cbd5e1; }
    .empty-state p { font-size: 15px; color: #64748b; }
    
    /* Override Streamlit elements to match light theme */
    div[data-testid="stMarkdownContainer"] p,
    .stCheckbox label, .stRadio label, .stSelectbox label, .stSlider label {
        color: #334155 !important;
    }
    h1, h2, h3 {
        color: #1e293b !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)


def setup_aplikasi():
    if "database" not in st.session_state:
        st.session_state.database = Database()
        st.session_state.database.inisialisasi_database()
        st.session_state.manajer_laporan = ManajerLaporan(
            st.session_state.database,
            notifikasi=NotifikasiToast()
        )
    if "user_aktif" not in st.session_state:
        st.session_state.user_aktif = None


def buat_user(data_user):
    # Inheritance: object dibuat sesuai peran user.
    if data_user["peran"] == PERAN_MAHASISWA:
        return Mahasiswa(
            data_user["id_user"],
            data_user["username"],
            data_user["nama"],
            data_user["peran"],
        )
    return Petugas(
        data_user["id_user"],
        data_user["username"],
        data_user["nama"],
        data_user["peran"],
    )


def warna_status(status):
    return COLORS.get(status, COLORS[STATUS_BARU])["bg"]


def tampil_badge_status(status):
    info = COLORS.get(status, COLORS[STATUS_BARU])
    st.markdown(
        f"""<span class="status-badge" style="background:{info['bg']};color:white;">
        {info['icon']} {status}</span>""",
        unsafe_allow_html=True,
    )


def simpan_file_upload(file_upload):
    if file_upload is None:
        return ""

    UPLOAD_DIR.mkdir(exist_ok=True)
    waktu = datetime.now().strftime("%Y%m%d%H%M%S")
    nama_file = f"{waktu}_{file_upload.name.replace(' ', '_')}"
    path_file = UPLOAD_DIR / nama_file
    path_file.write_bytes(file_upload.getbuffer())
    return str(Path("uploads") / nama_file)


def render_star_rating(rating):
    if rating is None:
        return '<span class="star-rating" style="color:#64748b;">—</span>'
    stars = "★" * rating + "☆" * (5 - rating)
    return f'<span class="star-rating" style="color:#f59e0b;">{stars}</span>'


def hitung_ringkasan(laporan_list):
    rating_list = [
        laporan.rating for laporan in laporan_list if laporan.rating is not None
    ]
    rata_rating = None
    if rating_list:
        rata_rating = round(sum(rating_list) / len(rating_list), 1)

    return {
        "total": len(laporan_list),
        STATUS_BARU: len([l for l in laporan_list if l.status.nama == STATUS_BARU]),
        STATUS_DIPROSES: len(
            [l for l in laporan_list if l.status.nama == STATUS_DIPROSES]
        ),
        STATUS_SELESAI: len(
            [l for l in laporan_list if l.status.nama == STATUS_SELESAI]
        ),
        "rating": rata_rating,
    }


def tampil_metrik_laporan(laporan_list):
    ringkasan = hitung_ringkasan(laporan_list)
    rata_str = str(ringkasan["rating"]) if ringkasan["rating"] is not None else "—"

    metrics = [
        ("📊", ringkasan["total"], "Total", ACCENT),
        (COLORS[STATUS_BARU]["icon"], ringkasan[STATUS_BARU], "Baru", COLORS[STATUS_BARU]["bg"]),
        (COLORS[STATUS_DIPROSES]["icon"], ringkasan[STATUS_DIPROSES], "Diproses", COLORS[STATUS_DIPROSES]["bg"]),
        (COLORS[STATUS_SELESAI]["icon"], ringkasan[STATUS_SELESAI], "Selesai", COLORS[STATUS_SELESAI]["bg"]),
        ("⭐", rata_str, "Avg Rating", "#f59e0b"),
    ]

    cols = st.columns(5)
    for col, (icon, value, label, color) in zip(cols, metrics):
        col.markdown(f"""
        <div class="metric-card" style="--accent-color:{color};">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)


def tampil_chart_laporan(laporan_list):
    if not laporan_list:
        return

    counts = {STATUS_BARU: 0, STATUS_DIPROSES: 0, STATUS_SELESAI: 0}
    for l in laporan_list:
        status_nama = l.status.nama
        if status_nama in counts:
            counts[status_nama] += 1

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title"><span class="icon">🍩</span> Distribusi Status</div>', unsafe_allow_html=True)
        fig_donut = go.Figure(data=[go.Pie(
            labels=list(counts.keys()),
            values=list(counts.values()),
            hole=0.55,
            marker=dict(
                colors=[COLORS[s]["bg"] for s in counts.keys()],
                line=dict(color='rgba(255,255,255,1)', width=2)
            ),
            textinfo='label+value',
            textfont=dict(size=13, family='Inter'),
            hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>",
        )])
        fig_donut.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#475569"),
            height=300,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="right",
                x=1.3
            ),
            annotations=[dict(
                text=f"<span style='font-size:28px;font-weight:700;color:#1e293b'>{sum(counts.values())}</span><br><span style='font-size:12px;color:#64748b'>Laporan</span>",
                x=0.5, y=0.5,
                showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, width="stretch", config={"displayModeBar": False})

    with col2:
        st.markdown('<div class="section-title"><span class="icon">📊</span> Jumlah per Status</div>', unsafe_allow_html=True)
        fig_bar = go.Figure(data=[go.Bar(
            x=list(counts.keys()),
            y=list(counts.values()),
            marker=dict(
                color=[COLORS[s]["bg"] for s in counts.keys()],
                cornerradius=8,
                line=dict(width=0),
            ),
            text=list(counts.values()),
            textposition='outside',
            textfont=dict(size=14, weight='bold', family='Inter', color='#334155'),
            hovertemplate="<b>%{x}</b><br>Jumlah: %{y}<extra></extra>",
        )])
        fig_bar.update_layout(
            margin=dict(l=20, r=20, t=10, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#475569", family="Inter, sans-serif", size=11),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=300,
            bargap=0.35,
        )
        st.plotly_chart(fig_bar, width="stretch", config={"displayModeBar": False})


def render_report_card(laporan):
    info = COLORS.get(laporan.status.nama, COLORS[STATUS_BARU])
    stars = render_star_rating(laporan.rating)

    # Build photo HTML
    foto_html = ""
    path_foto = Path(__file__).parent / laporan.foto_path
    if laporan.foto_path and path_foto.exists():
        import base64
        img_bytes = path_foto.read_bytes()
        b64 = base64.b64encode(img_bytes).decode()
        suffix = path_foto.suffix.lstrip('.').lower()
        mime = f"image/{'jpeg' if suffix in ('jpg','jpeg') else suffix}"
        foto_html = (
            f'<img src="data:{mime};base64,{b64}" '
            f'style="width:100%;max-height:140px;object-fit:cover;border-radius:8px;margin-top:8px;">'
        )

    # Minified HTML — Streamlit markdown parser breaks on line breaks between nested tags
    badge = f'<span class="status-badge" style="background:{info["bg"]};color:white;margin-right:8px;">{info["icon"]} {laporan.status.nama}</span>'
    footer = (
        f'<div class="report-footer">'
        f'<span class="report-user">👤 {laporan.nama_mahasiswa}</span>'
        f'<span>{badge}{stars}</span>'
        f'</div>'
    )
    header = (
        f'<div class="report-header">'
        f'<span class="report-id">#{laporan.id_laporan:04d}</span>'
        f'<span class="report-date">🕐 {laporan.dibuat_pada}</span>'
        f'</div>'
    )

    return (
        f'<div class="report-card">'
        f'{header}'
        f'<div class="report-location">📍 {laporan.lokasi}</div>'
        f'<div class="report-desc">{laporan.deskripsi}</div>'
        f'{foto_html}'
        f'{footer}'
        f'</div>'
    )


def filter_laporan(laporan_list, status_filter, kata_kunci):
    hasil = laporan_list
    if status_filter != "Semua":
        hasil = [laporan for laporan in hasil if laporan.status.nama == status_filter]

    kata_kunci = kata_kunci.strip().lower()
    if kata_kunci:
        hasil = [
            laporan
            for laporan in hasil
            if kata_kunci in laporan.lokasi.lower()
            or kata_kunci in laporan.deskripsi.lower()
            or kata_kunci in laporan.nama_mahasiswa.lower()
        ]
    return hasil


def tampil_tabel_dan_detail(laporan_list, key_prefix):
    if not laporan_list:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📭</div>
            <p>Belum ada laporan.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    kolom_filter1, kolom_filter2 = st.columns([1, 2])
    status_filter = kolom_filter1.selectbox(
        "🔍 Filter status",
        ["Semua"] + DAFTAR_STATUS,
        key=f"{key_prefix}_status_filter",
    )
    kata_kunci = kolom_filter2.text_input(
        "🔎 Cari laporan",
        placeholder="Cari lokasi, deskripsi, atau nama mahasiswa",
        key=f"{key_prefix}_cari",
    )

    laporan_filter = filter_laporan(laporan_list, status_filter, kata_kunci)

    if not laporan_filter:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🔍</div>
            <p>Tidak ada laporan yang cocok.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f'<div class="section-title"><span class="icon">📋</span> {len(laporan_filter)} Laporan</div>', unsafe_allow_html=True)

    # Render styled report cards
    for laporan in laporan_filter:
        st.markdown(render_report_card(laporan), unsafe_allow_html=True)

    # Detail selector
    st.markdown("---")
    pilihan = st.selectbox(
        "🔎 Lihat detail laporan",
        laporan_filter,
        format_func=lambda laporan: f"#{laporan.id_laporan:04d} — {laporan.lokasi}",
        key=f"{key_prefix}_detail",
    )
    tampil_detail_laporan(pilihan)


def tampil_detail_laporan(laporan):
    with st.expander("📄 Detail Laporan", expanded=True):
        kolom1, kolom2 = st.columns([2, 1])
        with kolom1:
            st.markdown(f"**ID Laporan:** `#{laporan.id_laporan:04d}`")
            st.markdown(f"**Mahasiswa:** {laporan.nama_mahasiswa}")
            st.markdown(f"**Lokasi:** 📍 {laporan.lokasi}")
            st.markdown(f"**Deskripsi:** {laporan.deskripsi}")
            st.markdown(f"**Dibuat pada:** 🕐 {laporan.dibuat_pada}")
            st.write("**Status:**")
            tampil_badge_status(laporan.status.nama)
            st.caption(laporan.status.pesan())
            st.markdown(f"**Rating:** {render_star_rating(laporan.rating)}", unsafe_allow_html=True)

        with kolom2:
            st.markdown("**Foto:**")
            path_foto = Path(__file__).parent / laporan.foto_path
            if laporan.foto_path and path_foto.exists():
                st.image(str(path_foto), width="stretch")
            else:
                st.info(laporan.foto_path or "Tidak ada foto.")


def halaman_login():
    st.subheader("🔐 Login")
    with st.form("form_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        tombol_login = st.form_submit_button("Login", width="stretch")

    if tombol_login:
        data_user = st.session_state.database.ambil_user_login(username, password)
        if data_user is None:
            st.error("Login gagal.")
            return

        st.session_state.user_aktif = buat_user(data_user)
        st.success("Login berhasil.")
        st.rerun()


def halaman_register():
    st.subheader("📝 Register")
    with st.form("form_register"):
        nama = st.text_input("Nama lengkap")
        username = st.text_input("Username baru")
        password = st.text_input("Password baru", type="password")
        peran = st.selectbox("Peran", [PERAN_MAHASISWA, PERAN_PETUGAS])
        tombol_register = st.form_submit_button("Register", width="stretch")

    if tombol_register:
        if not nama.strip() or not username.strip() or not password.strip():
            st.error("Nama, username, dan password wajib diisi.")
            return
        if st.session_state.database.username_sudah_ada(username):
            st.error("Username sudah dipakai.")
            return

        id_user = st.session_state.database.tambah_user(
            username.strip(),
            password.strip(),
            nama.strip(),
            peran,
        )
        if id_user is None:
            st.error("Register gagal.")
            return

        st.success(f"Register berhasil. ID user: {id_user}. Silakan login.")


def halaman_awal():
    st.markdown("""
    <div class="login-header">
        <h1>🏫 CampusCare</h1>
        <p>Sistem Lapor Kerusakan Fasilitas Kampus</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("🔑 Akun demo: **mhs1**/123, **mhs2**/123, **petugas1**/123")

    tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])
    with tab_login:
        halaman_login()
    with tab_register:
        halaman_register()


def menu_sidebar():
    user = st.session_state.user_aktif
    initial = user.nama[0].upper() if user.nama else "?"
    role_label = "👨‍🎓 Mahasiswa" if user.peran == PERAN_MAHASISWA else "🔧 Petugas"

    st.sidebar.markdown(f"""
    <div style="text-align:center;padding:16px 0 8px 0;">
        <div style="font-size:28px;font-weight:800;
                    background:linear-gradient(135deg,#6366f1,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            🏫 CampusCare
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"""
    <div class="sidebar-user-info">
        <div class="sidebar-avatar">{initial}</div>
        <div>
            <div class="sidebar-user-name">{user.nama}</div>
            <div class="sidebar-user-role">{role_label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Notification Center
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="section-title"><span class="icon">🔔</span> Notifikasi</div>', unsafe_allow_html=True)

    if "notifikasi_list" not in st.session_state or not st.session_state.notifikasi_list:
        st.sidebar.markdown("""
        <div class="notif-item" style="text-align:center;color:#64748b;">
            Tidak ada notifikasi
        </div>
        """, unsafe_allow_html=True)
    else:
        count = 0
        for notif in st.session_state.notifikasi_list:
            if count >= 5:
                break
            penerima = notif["penerima"]
            # Petugas sees all, Mahasiswa sees their own or general/petugas updates they initiated
            if user.peran == PERAN_PETUGAS or penerima == "petugas" or penerima == user.nama:
                st.sidebar.markdown(f"""
                <div class="notif-item">
                    <div class="notif-time">{notif['waktu']}</div>
                    {notif['pesan']}
                </div>
                """, unsafe_allow_html=True)
                count += 1
        if count == 0:
            st.sidebar.markdown("""
            <div class="notif-item" style="text-align:center;color:#64748b;">
                Tidak ada notifikasi
            </div>
            """, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", width="stretch"):
        st.session_state.user_aktif = None
        st.rerun()

    st.sidebar.caption("Tugas Besar PBO — 2026")


def halaman_mahasiswa():
    user = st.session_state.user_aktif
    manajer = st.session_state.manajer_laporan
    laporan_saya = manajer.lihat_laporan_mahasiswa(user.id_user)

    menu_sidebar()
    st.markdown(f"""
    <div class="section-title" style="font-size:26px;margin-bottom:16px;">
        <span class="icon">👨‍🎓</span> Dashboard Mahasiswa
    </div>
    """, unsafe_allow_html=True)
    tampil_metrik_laporan(laporan_saya)
    st.markdown("<br>", unsafe_allow_html=True)

    tab_dashboard, tab_buat, tab_laporan, tab_rating, tab_batal = st.tabs(
        ["📊 Ringkasan", "➕ Buat Laporan", "📋 Laporan Saya", "⭐ Rating", "🗑️ Batalkan"]
    )

    with tab_dashboard:
        st.markdown('<div class="section-title"><span class="icon">📊</span> Ringkasan Laporan Saya</div>', unsafe_allow_html=True)
        tampil_chart_laporan(laporan_saya)
        tampil_tabel_dan_detail(laporan_saya, "mhs_ringkasan")

    with tab_buat:
        st.markdown('<div class="section-title"><span class="icon">➕</span> Buat Laporan Kerusakan</div>', unsafe_allow_html=True)
        with st.form("form_laporan"):
            lokasi = st.text_input("📍 Lokasi")
            deskripsi = st.text_area("📝 Deskripsi")
            file_upload = st.file_uploader(
                "📷 Upload foto kerusakan",
                type=["jpg", "jpeg", "png"],
            )
            foto_path_manual = st.text_input(
                "🔗 Foto path manual",
                placeholder="Contoh: foto/lampu_mati.jpg",
            )
            tombol_simpan = st.form_submit_button("💾 Simpan Laporan", width="stretch")

        if tombol_simpan:
            try:
                foto_path = simpan_file_upload(file_upload) or foto_path_manual
                id_laporan = user.buat_laporan(
                    manajer,
                    lokasi,
                    deskripsi,
                    foto_path,
                )
                st.success(f"✅ Laporan berhasil dibuat. ID laporan: {id_laporan}")
                st.rerun()
            except ValueError as error:
                st.error(str(error))

    with tab_laporan:
        st.markdown('<div class="section-title"><span class="icon">📋</span> Laporan Saya</div>', unsafe_allow_html=True)
        tampil_tabel_dan_detail(laporan_saya, "mhs_laporan")

    with tab_rating:
        st.markdown('<div class="section-title"><span class="icon">⭐</span> Beri Rating Laporan Selesai</div>', unsafe_allow_html=True)
        laporan_selesai = [
            laporan for laporan in laporan_saya if laporan.status.nama == STATUS_SELESAI
        ]

        if not laporan_selesai:
            st.markdown("""
            <div class="empty-state">
                <div class="icon">⭐</div>
                <p>Belum ada laporan selesai.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.form("form_rating"):
                pilihan = st.selectbox(
                    "Pilih laporan",
                    laporan_selesai,
                    format_func=lambda laporan: (
                        f"#{laporan.id_laporan:04d} — {laporan.lokasi}"
                    ),
                )
                rating = st.slider("⭐ Rating", 1, 5, 5)
                tombol_rating = st.form_submit_button("💾 Simpan Rating", width="stretch")

            if tombol_rating:
                try:
                    manajer.simpan_rating(pilihan.id_laporan, rating)
                    st.success("✅ Rating berhasil disimpan.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    with tab_batal:
        st.markdown('<div class="section-title"><span class="icon">🗑️</span> Batalkan Laporan Baru</div>', unsafe_allow_html=True)
        laporan_baru = [
            laporan for laporan in laporan_saya if laporan.status.nama == STATUS_BARU
        ]

        if not laporan_baru:
            st.markdown("""
            <div class="empty-state">
                <div class="icon">🗑️</div>
                <p>Tidak ada laporan baru yang bisa dibatalkan.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.form("form_batal"):
                pilihan = st.selectbox(
                    "Pilih laporan yang ingin dibatalkan",
                    laporan_baru,
                    format_func=lambda laporan: (
                        f"#{laporan.id_laporan:04d} — {laporan.lokasi} ({laporan.deskripsi[:30]}...)"
                    ),
                )
                tombol_batal = st.form_submit_button("🗑️ Batalkan Laporan", width="stretch")

            if tombol_batal:
                try:
                    user.batalkan_laporan(manajer, pilihan.id_laporan)
                    st.success(f"✅ Laporan ID {pilihan.id_laporan} berhasil dibatalkan.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))


def halaman_petugas():
    user = st.session_state.user_aktif
    manajer = st.session_state.manajer_laporan
    laporan_list = manajer.lihat_semua_laporan()

    menu_sidebar()
    st.markdown(f"""
    <div class="section-title" style="font-size:26px;margin-bottom:16px;">
        <span class="icon">🔧</span> Dashboard Petugas
    </div>
    """, unsafe_allow_html=True)
    tampil_metrik_laporan(laporan_list)
    st.markdown("<br>", unsafe_allow_html=True)

    tab_dashboard, tab_laporan, tab_update = st.tabs(
        ["📊 Ringkasan", "📋 Semua Laporan", "🔄 Update Status"]
    )

    with tab_dashboard:
        st.markdown('<div class="section-title"><span class="icon">📊</span> Ringkasan Semua Laporan</div>', unsafe_allow_html=True)
        tampil_chart_laporan(laporan_list)
        tampil_tabel_dan_detail(laporan_list, "petugas_ringkasan")

    with tab_laporan:
        st.markdown('<div class="section-title"><span class="icon">📋</span> Semua Laporan</div>', unsafe_allow_html=True)
        tampil_tabel_dan_detail(laporan_list, "petugas_laporan")

    with tab_update:
        st.markdown('<div class="section-title"><span class="icon">🔄</span> Update Status Laporan</div>', unsafe_allow_html=True)
        if not laporan_list:
            st.markdown("""
            <div class="empty-state">
                <div class="icon">📭</div>
                <p>Belum ada laporan.</p>
            </div>
            """, unsafe_allow_html=True)
            return

        with st.form("form_update_status"):
            pilihan = st.selectbox(
                "Pilih laporan",
                laporan_list,
                format_func=lambda laporan: (
                    f"#{laporan.id_laporan:04d} — {laporan.lokasi}"
                    f" ({laporan.status.nama})"
                ),
            )
            st.write("Status sekarang:")
            tampil_badge_status(pilihan.status.nama)
            status_baru = st.selectbox(
                "Status baru",
                DAFTAR_STATUS,
                index=DAFTAR_STATUS.index(pilihan.status.nama),
            )
            tombol_update = st.form_submit_button("🔄 Update Status", width="stretch")

        if tombol_update:
            try:
                user.update_status_laporan(
                    manajer,
                    pilihan.id_laporan,
                    status_baru,
                )
                st.success("✅ Status berhasil diupdate.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))


def main():
    st.set_page_config(
        page_title="CampusCare",
        page_icon="🏫",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()
    setup_aplikasi()

    user = st.session_state.user_aktif
    if user is None:
        halaman_awal()
    elif user.peran == PERAN_MAHASISWA:
        halaman_mahasiswa()
    elif user.peran == PERAN_PETUGAS:
        halaman_petugas()


if __name__ == "__main__":
    main()
