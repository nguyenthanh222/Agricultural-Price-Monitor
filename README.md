
# 📊 Vietnam Agricultural Price Monitor — Modern Data Pipeline

![Python](https://img.shields.io/badge/Python-3.13-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.56-green) ![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green) ![dbt](https://img.shields.io/badge/dbt-Core-orange) ![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-blue)

A professional, end-to-end data pipeline for monitoring and analyzing agricultural commodity prices in Vietnam. This project implements a Modern Data Stack (MDS) architecture to scrape, ingest, transform, and visualize price trends for three major agricultural categories: rice, coffee, and vegetables/fruits.

## 🏗️ System Architecture

This project follows a complete medallion architecture pipeline from raw data collection to final business intelligence:

<img width="1068" height="151" alt="image" src="https://github.com/user-attachments/assets/ee5c4a53-d9fd-4a10-9c57-1dab87d064b7" />



### Pipeline Stages

| Stage | Tool | Description |
|-------|------|-------------|
| **Extraction** | Python + BeautifulSoup4 | Scrape VNSAT price data with ASP.NET form handling |
| **Landing** | CSV Files | Raw data storage in Bronze layer |
| **Normalization** | Python + Pandas | Clean and standardize data in Silver layer |
| **Aggregation** | Python + Pandas | Calculate daily averages and trends in Gold layer |
| **Storage** | MongoDB | Persistent storage of historical data |
| **Visualization** | Streamlit + Plotly | Interactive dashboard with KPIs and trends |
| **Orchestration** | Shell Scripts | Manual and automated pipeline execution |

## 💡 Why This Project?

Vietnam's agricultural commodity market is highly volatile. This project was built to solve the market monitoring challenge by:

- 🤖 **Automation**: Structured pipeline that can run on any schedule
- ⏳ **Historical Accuracy**: Building rich historical database for trend analysis
- 🧠 **Informed Decisions**: Pre-calculated visualizations showing market patterns
- 🚀 **Modern Data Stack**: Using industry-standard tools (BeautifulSoup, dbt-ready structure, MongoDB)
- 📊 **Multi-Category Support**: Track rice (Lúa gạo), coffee (Cà phê), and vegetables/fruits (Rau quả)

## 📊 Supported Agricultural Categories

<img width="1447" height="300" alt="ca_phe_linechart" src="https://github.com/user-attachments/assets/ac714b55-c170-4fea-bbd8-d9d4c281eba1" />

<img width="1447" height="400" alt="products" src="https://github.com/user-attachments/assets/1ac4bd3f-4a3c-4a33-8698-38eb5a5e601f" />

<img width="1447" height="400" alt="newplot (1)" src="https://github.com/user-attachments/assets/7f4cbe81-9c9f-498a-bcbf-effb80816da5" />

<img width="1243" height="521" alt="image" src="https://github.com/user-attachments/assets/4f496660-3d41-4016-9667-bf4148322ec8" />

<img width="1447" height="300" alt="newplot (4)" src="https://github.com/user-attachments/assets/1b467da7-fcff-4fb4-9280-9b2614346d5f" />


## 📸 Dashboard Features
<img width="1918" height="868" alt="Screenshot 2026-04-23 190142" src="https://github.com/user-attachments/assets/fb8a5cc9-3167-479c-9f5e-f780fa81fc55" />

### KPI Metrics
- 💰 **Average Price Today**: Current day average across all products
- 📈 **Daily Change**: % change from previous day
- 🔥 **Highest Volatility**: Most volatile product from top 10 changes

### Visualizations
- **Line Chart**: Price trends by category with date filtering
- **Bar Chart**: Comparison of average prices across categories with unit normalization
- **Data Table**: Detailed price records with region and product info
- **Top 10 Changes**: Products with highest % price changes

### Interactive Features
- 🔍 **Category Filter**: Select one or multiple agricultural categories
- 📦 **Product Filter**: Choose specific products to analyze
- 📅 **Date Range**: View trends over specific time periods
- 🔗 **Hover Details**: Detailed information on data points

## 📁 Project Structure

```
agricultural-products-monitoring/
├── .github/workflows/          # CI/CD Automation (GitHub Actions - future)
├── config/
│   └── settings.py             # Central configuration (paths, URLs, categories)
├── dbt_project/                # dbt Models & Configuration
│   └── dbt_project.yml         # dbt project configuration
├── sources/                    # Core Python Processing Scripts
│   ├── scraper/
│   │   ├── scraper.py          # Web Scraper for VNSAT prices
│   │   └── inspect_form.py     # Debug utility for form fields
│   ├── dlt/
│   │   └── dlt_ingestion.py    # Data Loading to MongoDB
│   ├── mongodb/
│   │   └── connection.py       # MongoDB connection utilities
│   └── utils/
│       ├── transform_to_silver.py  # Silver layer normalization
│       ├── analysis.py             # Gold layer aggregation
│       └── visualize.py            # Streamlit dashboard
├── data/
│   ├── bronze/                 # Raw CSV data from scraper
│   ├── silver/                 # Normalized Parquet files
│   └── gold/                   # Aggregated analysis files
├── notebook/                   # Jupyter notebooks for exploration
├── activate_venv.sh            # Activate virtual environment
├── run_pipeline.sh             # Full pipeline execution script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.13+ |
| Web Scraping | BeautifulSoup4, Requests | 4.12.3 |
| Data Processing | Pandas | 3.0.2 |
| Visualization | Streamlit, Plotly | 1.56.0, 5.18.0 |
| Database | MongoDB, Parquet | Latest |
| Data Transform | dbt Core | Configured |
| CI/CD | GitHub Actions | - |

## 🚀 Getting Started

### 1️⃣ Prerequisites

- Python 3.13+
- MongoDB (local or Atlas)
- Git

### 2️⃣ Installation

```bash
# Clone repository
git clone https://github.com/yourusername/Agricultural-Price-Monitor
.git
cd Agricultural-Price-Monitor

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configuration

Create a `.env` file in the project root:

```bash
# MongoDB Connection
MONGO_URI=mongodb://localhost:27017  # or your MongoDB Atlas URI
```

Update `config/settings.py` if needed:
- `VNSAT_PRICES_URL`: Target website URL
- `CATEGORIES`: Agricultural categories to scrape
- Data directories for Bronze/Silver/Gold layers

### 4️⃣ Run Full Pipeline

```bash
# Option 1: Using shell script (recommended)
chmod +x run_pipeline.sh activate_venv.sh
./run_pipeline.sh

# Option 2: Manual step-by-step
# Activate venv
source activate_venv.sh

# Step 1: Scrape data for each category
python -m sources.scraper.scraper lua_gao
python -m sources.scraper.scraper ca_phe
python -m sources.scraper.scraper rau_qua

# Step 2: Transform to silver layer
python -m sources.utils.transform_to_silver

# Step 3: Build gold layer (analysis)
python -m sources.utils.analysis

# Step 4: Ingest to MongoDB (all categories)
python -m sources.dlt.dlt_ingestion

# Step 5: Launch Streamlit dashboard
streamlit run sources/utils/visualize.py
```

The dashboard will open at `http://localhost:8501`

## 📋 Pipeline Details

### 1. Web Scraper (`sources/scraper/scraper.py`)

- **Target**: VNSAT (https://thitruongnongsan.gov.vn/vn/nguonwmy.aspx)
- **Method**: Form-based POST requests with ViewState handling
- **Output**: CSV files in `data/bronze/` (format: `YYYYMMDD_gia_CATEGORY_raw.csv`)
- **Categories**: Lúa gạo, Cà phê, Rau quả
- **Fields Extracted**: Product, Region, Date, Price

**Usage**:
```bash
python -m sources.scraper.scraper lua_gao          # Single category
python -m sources.scraper.scraper                  # All categories
```

### 2. Silver Layer Transform (`sources/utils/transform_to_silver.py`)

- **Input**: Bronze CSV files
- **Process**: 
  - Normalize product names per category
  - Standardize units (VND/kg, VND/tấn, etc.)
  - Clean price values
  - Parse dates to DD-MM-YYYY format
- **Output**: `data/silver/gia_nong_san_clean.parquet`

**Columns**: `date`, `category`, `product_normalized`, `region`, `unit_normalized`, `price_number`

### 3. Gold Layer Analysis (`sources/utils/analysis.py`)

- **Input**: Silver parquet file
- **Process**:
  - Group by date/category/product/region
  - Calculate daily average prices
  - Compute % price changes vs previous day
  - Identify top 10 products by volatility
- **Outputs**:
  - `data/gold/daily_price_by_product_region.parquet` (daily aggregates)
  - `data/gold/YYYYMMDD_top_10_change.parquet` (daily top changes)

### 4. MongoDB Ingestion (`sources/dlt/dlt_ingestion.py`)

- **Database**: `agricultural_price_monitoring`
- **Collections**: `bronze_lua_gao`, `bronze_ca_phe`, `bronze_rau_qua`
- **Process**: Load bronze CSV data into MongoDB for historical tracking

**Usage**:
```bash
python -m sources.dlt.dlt_ingestion lua_gao          # Single category
python -m sources.dlt.dlt_ingestion                  # All categories
```

### 5. Streamlit Dashboard (`sources/utils/visualize.py`)

**Features**:
- Real-time KPI cards (avg price, daily change, volatility)
- Multi-category price comparison (line chart with log scale)
- Category comparison (bar chart with min/max info)
- Interactive filters (category, product)
- Debug info expander for data validation

**Launch**:
```bash
streamlit run sources/utils/visualize.py
```

## 🔧 Debugging & Utilities

### Inspect Form Fields
Debug the VNSAT website form structure:

```bash
python sources/scraper/inspect_form.py
```

This will print:
- All form input fields and their names
- POST response table structure
- Sample data from the website

### Debug Dashboard
The Streamlit dashboard includes a **Debug Info** expander showing:
- DataFrame shape and columns
- Unique categories and date range
- First few rows of data
- Data validation info


## 🛡️ Error Handling & Validation

The pipeline includes:
- ✅ Date parsing with coerce mode (invalid dates become NaT)
- ✅ Empty DataFrame checks before visualization
- ✅ Form field validation in scraper
- ✅ Unit normalization to prevent category mixing
- ✅ MongoDB connection error handling

## 📊 Future Enhancements

- [ ] GitHub Actions CI/CD workflows for automated scheduling
- [ ] dbt models for advanced transformations
- [ ] Email/Slack alerts for price anomalies
- [ ] Multi-region analysis and regional trends
- [ ] Forecasting models (ARIMA/Prophet)
- [ ] API endpoint for price data access
- [ ] Enhanced data quality metrics

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Data source: VNSAT (Thị trường nông sản)
- Built with Python, Streamlit, and MongoDB
- Inspired by modern data stack architecture best practices

## 📧 Support

For questions or issues:
- Open a GitHub Issue
- Check existing documentation in `/notebook/`
- Review debug logs from pipeline execution

---

**Built with ❤️ for agricultural market monitoring in Vietnam**
=======
# Agricultural-Price-Monitor
>>>>>>> 5297de5c39ee17c1a04aac3a180fa4b41416fdec
