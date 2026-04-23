import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Thêm thư mục gốc project vào PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # sources/utils -> sources -> root
sys.path.insert(0, str(ROOT_DIR))

from config import settings
import plotly.express as px
import plotly.graph_objects as go


def load_daily_price():
    path = settings.GOLD_DAILY_FILE
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_top_change():
    latest = max(settings.GOLD_DIR.glob("????????_top_10_change.parquet"), default=None)
    if not latest:
        return pd.DataFrame()
    df = pd.read_parquet(latest)
    df["date"] = pd.to_datetime(df["date"])
    return df


def calculate_kpis(df):
    """Tính toán các KPI chính"""
    if df.empty:
        return None
    
    try:
        today = df["date"].max()
        yesterday = today - timedelta(days=1)
        
        today_data = df[df["date"] == today]
        yesterday_data = df[df["date"] == yesterday]
        
        # KPI 1: Giá trung bình hôm nay
        avg_price_today = today_data["avg_price"].mean() if not today_data.empty else 0
        
        # KPI 2: % tăng trưởng so với hôm qua
        avg_price_yesterday = yesterday_data["avg_price"].mean() if not yesterday_data.empty else avg_price_today
        if avg_price_yesterday > 0:
            growth_pct = ((avg_price_today - avg_price_yesterday) / avg_price_yesterday) * 100
        else:
            growth_pct = 0
        
        # KPI 3: Loại nông sản biến động mạnh nhất
        df_top_change = load_top_change()
        if not df_top_change.empty:
            top_volatile = df_top_change.iloc[0] if len(df_top_change) > 0 else None
        else:
            top_volatile = None
        
        return {
            "avg_price_today": avg_price_today,
            "growth_pct": growth_pct,
            "top_volatile": top_volatile,
            "today": today,
            "yesterday": yesterday
        }
    except Exception as e:
        st.warning(f"Lỗi khi tính KPI: {e}")
        return None


def main():
    st.set_page_config(page_title="Giá Nông Sản Việt Nam", layout="wide")
    st.title("📊 Giá Nông Sản Việt Nam (VNSAT)")

    df = load_daily_price()
    if df.empty:
        st.warning("Chưa có dữ liệu Gold để hiển thị.")
        st.info("📌 Hãy chạy pipeline trước:")
        st.code("""
python -m sources.scraper.scraper lua_gao
python -m sources.scraper.scraper ca_phe
python -m sources.scraper.scraper rau_qua
python -m sources.utils.transform_to_silver
python -m sources.utils.analysis
        """)
        return
    
    # Debug: Hiển thị info dữ liệu
    with st.expander("🔍 Debug Info"):
        st.write(f"Shape: {df.shape}")
        st.write(f"Columns: {df.columns.tolist()}")
        st.write(f"Categories: {df['category'].unique().tolist() if 'category' in df.columns else 'N/A'}")
        st.write(f"Date range: {df['date'].min()} to {df['date'].max()}")
        st.dataframe(df.head())

    # === KPIs ===
    kpis = calculate_kpis(df)
    if kpis:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💰 Giá TB hôm nay",
                f"{kpis['avg_price_today']:.0f} VND",
                f"Ngày {kpis['today'].strftime('%d/%m/%Y')}"
            )
        
        with col2:
            growth_color = "green" if kpis['growth_pct'] >= 0 else "red"
            st.metric(
                "📈 Tăng/Giảm so với hôm qua",
                f"{kpis['growth_pct']:+.2f}%",
                delta_color="off"
            )
        
        with col3:
            if kpis['top_volatile'] is not None:
                volatile_product = kpis['top_volatile'].get('product_normalized', 'N/A')
                volatile_change = kpis['top_volatile'].get('change_pct', 0)
                st.metric(
                    "🔥 Biến động mạnh nhất",
                    f"{volatile_product}",
                    f"{volatile_change:+.2f}%"
                )
            else:
                st.metric("🔥 Biến động mạnh nhất", "N/A", "Chưa có dữ liệu")
        
        st.divider()

    # Sidebar: filter
    categories = sorted(df["category"].unique())
    selected_category = st.sidebar.multiselect(
        "Chọn ngành hàng",
        options=categories,
        default=categories,
    )

    df_filtered = df[df["category"].isin(selected_category)]
    products = sorted(df_filtered["product_normalized"].unique())
    selected_product = st.sidebar.multiselect(
        "Chọn mặt hàng",
        options=products,
        default=products[:3] if len(products) >= 3 else products,
    )

    if not selected_product:
        st.info("Hãy chọn ít nhất 1 mặt hàng.")
        return

    df_plot = df_filtered[df_filtered["product_normalized"].isin(selected_product)].copy()
    
    if df_plot.empty:
        st.warning("Không có dữ liệu cho các mặt hàng đã chọn. Hãy chọn lại hoặc kiểm tra dữ liệu.")
        return
    
    df_plot = df_plot.sort_values("date")
    price_col = "avg_price" if "avg_price" in df_plot.columns else "avgprice" if "avgprice" in df_plot.columns else None
    if price_col is None:
        st.error("Thiếu cột giá avg_price/avgprice trong dữ liệu.")
        return

    with st.expander("Debug dữ liệu trước khi vẽ line chart"):
        st.write("Số category trong df_plot:", df_plot["category"].unique())
        st.write("Số product:", df_plot["product_normalized"].unique())
        st.dataframe(df_plot.groupby(["category", "product_normalized"]).size())

    # === Biểu đồ giá - So sánh giữa các ngành hàng ===
    st.subheader("📈 Biểu đồ giá - So sánh giữa các ngành hàng")

    if not df_plot.empty:
        # Tính trung bình giá theo ngày, category và unit_normalized (đảm bảo không trộn lẫn đơn vị)
        df_category_avg = df_plot.groupby(["date", "category", "unit_normalized"], as_index=False)[price_col].mean()
        df_category_avg = df_category_avg.rename(columns={price_col: "avg_price"})
        df_category_avg["category"] = df_category_avg["category"].astype(str)
        df_category_avg["unit_normalized"] = df_category_avg["unit_normalized"].astype(str)
    
        # Loại bỏ category rỗng (nếu có)
        df_category_avg = df_category_avg[
            df_category_avg["category"].notna() & 
            (df_category_avg["category"] != "") &
            (df_category_avg["avg_price"] > 0)  # thêm điều kiện này để tránh giá 0
        ].sort_values("date")

        if not df_category_avg.empty and len(df_category_avg["category"].unique()) >= 1:
            try:
                fig_line = px.line(
                    df_category_avg,
                    x="date",
                    y="avg_price",
                    color="category",
                    line_dash="unit_normalized",
                    markers=True,
                    labels={"avg_price": "Giá trung bình (VND)", "date": "Ngày", "category": "Ngành hàng", "unit_normalized": "Đơn vị"},
                    title="Giá trung bình theo ngày - So sánh các ngành hàng (phân biệt theo đơn vị)",
                    log_y=True,                    # ← Dùng log scale để so sánh tốt hơn
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_line.update_layout(
                    hovermode="x unified",
                    height=500,
                yaxis_title="Giá trung bình (VND) - Log scale",
                yaxis=dict(
                    tickformat=",.0f",
                    exponentformat="none"   # tránh hiển thị dạng 1e4
                    )
                )
                st.plotly_chart(fig_line, use_container_width=True)
            except Exception as e:
                st.error(f"Lỗi khi vẽ biểu đồ line: {e}")
                st.write("Debug df_category_avg:", df_category_avg)
        else:
            st.warning("Không đủ dữ liệu để so sánh giữa các ngành hàng. Hãy chọn nhiều ngành hàng và mặt hàng hơn.")
    else:
        st.warning("Không có dữ liệu sau khi lọc.")

    # === Biểu đồ cột so sánh 3 category ===
    st.subheader("📊 Biểu đồ cột - So sánh giá TB các category")
    
    df_category_stats = df_plot.groupby(["date", "category", "unit_normalized"]).agg({
        "avg_price": ["mean", "min", "max"]
    }).reset_index()
    df_category_stats.columns = ["date", "category", "unit_normalized", "mean", "min", "max"]
    df_category_stats["category"] = df_category_stats["category"].astype(str)
    df_category_stats["unit_normalized"] = df_category_stats["unit_normalized"].astype(str)
    df_category_stats["date_str"] = df_category_stats["date"].dt.strftime("%d/%m/%Y")
    df_category_stats["category_date"] = df_category_stats["category"] + " - " + df_category_stats["date_str"]
    df_category_stats = df_category_stats.dropna(subset=["mean"])

    if not df_category_stats.empty:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=df_category_stats["category_date"],
            y=df_category_stats["mean"],
            customdata=np.stack([df_category_stats["min"], df_category_stats["max"], df_category_stats["unit_normalized"]], axis=-1),
            marker_color="#1f77b4",
            hovertemplate="%{x}<br>Giá TB: %{y:,.0f} %{customdata[2]}<br>Min: %{customdata[0]:,.0f}<br>Max: %{customdata[1]:,.0f}<extra></extra>"
        ))
        fig_bar.update_layout(
            title="Giá trung bình - So sánh các category",
            xaxis_title="Ngành hàng",
            yaxis_title="Giá trung bình (VND)",
            hovermode="x unified",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Không có đủ dữ liệu thống kê cho các mặt hàng này.")

    # === Biểu đồ chi tiết theo sản phẩm (optional, để lại cũ) ===
    st.subheader("📈 Giá theo sản phẩm (Chi tiết)")
    
    tab_individual, tab_table = st.tabs(["Biểu đồ riêng lẻ", "Bảng dữ liệu"])
    
    with tab_individual:
        for product in selected_product:
            df_p = df_plot[df_plot["product_normalized"] == product]
            if not df_p.empty:
                st.write(f"**{product.upper()}**")
                fig_p = px.line(
                    df_p.sort_values("date"),
                    x="date",
                    y="unit_normalized",
                    color="category",
                    markers=True,
                    labels={"avg_price": "Giá (VND)", "date": "Ngày"}
                )
                fig_p.update_layout(height=300)
                st.plotly_chart(fig_p, use_container_width=True)
    
    with tab_table:
        st.dataframe(
            df_plot.sort_values(["category", "date"], ascending=[True, False]),
            use_container_width=True,
            height=400
        )

    # Top biến động
    st.subheader("🔥 Top 10 biến động")
    df_top = load_top_change()
    if not df_top.empty:
        df_top = df_top.sort_values("change_pct", ascending=False)
        
        fig_top = px.bar(
            df_top,
            x="change_pct",
            y="product_normalized",
            color="change_pct",
            orientation="h",
            labels={"change_pct": "% Thay đổi", "product_normalized": "Mặt hàng"},
            title="Top 10 Sản phẩm biến động mạnh nhất",
            color_continuous_scale="RdYlGn"
        )
        fig_top.update_layout(height=400)
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.write("Chưa có dữ liệu biến động.")


if __name__ == "__main__":
    main()