# 💰 Lynce Finance - Personal Financial Management System

[![Streamlit](https://img.shields.io/badge/Streamlit-1.48.1-red.svg)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
[![Google Sheets](https://img.shields.io/badge/Google%20Sheets-API-green.svg)](https://developers.google.com/sheets/api)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT-orange.svg)](https://openai.com/)

A comprehensive personal financial management application built with Streamlit, featuring multi-language support, Google Sheets integration, AI-powered insights, and interactive data analysis.

## 🌟 Features

### 📊 **Core Financial Management**
- **Account Balances** - Real-time balance tracking across multiple accounts
- **Transaction Management** - Add, edit, and categorize financial transactions
- **Credit Card Management** - Track credit card expenses and bill payments
- **Income vs Expenses** - Comprehensive revenue and expense analysis
- **Multi-Currency Support** - Handle transactions in different currencies

### 🔧 **Advanced Features**
- **Multi-Language Support** - Portuguese, English, and Russian interfaces
- **Google Sheets Integration** - Cloud-based data storage and synchronization
- **AI-Powered Insights** - OpenAI GPT integration for financial analysis
- **Interactive Data Analysis** - Pygwalker integration for advanced analytics
- **User Authentication** - Secure login system with session management
- **Responsive Design** - Modern UI with Material Design icons

### 📈 **Analytics & Reporting**
- **Interactive Charts** - Plotly-powered visualizations
- **Real-time Dashboards** - Live financial overview
- **Custom Reports** - Generate detailed financial reports
- **Data Export** - Export data for external analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Cloud Platform account
- OpenAI API key (for AI features)
- Google Sheets API access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Purcineli/Lynce_Finance.git
   cd Lynce_Finance
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud credentials**
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create a service account and download credentials
   - Add credentials to `.streamlit/secrets.toml`

4. **Configure secrets**
   Create `.streamlit/secrets.toml` with:
   ```toml
   gcp_service_account = {
       # Your Google Cloud service account credentials
   }
   idkey = "your_google_sheets_id"
   namekey = "your_sheet_name"
   OPENAI_API_KEY = "your_openai_api_key"
   ```

5. **Run the application**
   ```bash
   streamlit run LYNCE.py
   ```

## 📁 Project Structure

```
Lynce_Finance/
├── LYNCE.py                 # Main application entry point
├── requirements.txt         # Python dependencies
├── shared_components.py     # Shared navigation and UI components
├── TRADUTOR.py             # Multi-language translation system
├── dependencies.py         # Google Sheets integration utilities
├── cookies_manager.py      # Session and cookie management
├── pages/                  # Application pages
│   ├── 1_SALDOS.py        # Account balances and overview
│   ├── 2_LANCAMENTOS.py   # Transaction management
│   ├── 3_CONFIGURACOES.py # System configuration
│   ├── 4_CARTOES DE CREDITO.py # Credit card management
│   ├── 5_RECEITAS X DESPESAS.py # Income vs expenses
│   ├── 6_VERSAO.py        # About and version info
│   ├── 7_IA.py            # AI-powered financial insights
│   └── 8_PYGWALKER.py     # Interactive data analysis
├── .streamlit/             # Streamlit configuration
├── venv/                   # Virtual environment
└── .gitignore             # Git ignore rules
```

## 🎯 Key Components

### **LYNCE.py** - Main Application
- User authentication system
- Session management
- Application routing

### **shared_components.py** - Shared UI Components
- Centralized sidebar navigation
- Multi-language support
- Logout functionality

### **TRADUTOR.py** - Translation System
- Comprehensive translation dictionaries
- Support for Portuguese, English, and Russian
- Dynamic text replacement

### **dependencies.py** - Google Sheets Integration
- Secure API authentication
- Data synchronization
- Error handling and retry logic

## 📊 Data Structure

The application uses Google Sheets with the following structure:

### **Main Sheets:**
1. **Transactions** - Bank and credit card transactions
2. **Credit Cards** - Credit card expenses and bills
3. **Bank Accounts** - Account configurations
4. **Accounting Accounts** - Category and account mappings
5. **Projects/Events** - Project-based expense tracking
6. **AI Configuration** - OpenAI integration settings

### **Data Fields:**
- `ID` - Unique transaction identifier
- `DATA` - Transaction date
- `PROPRIETÁRIO` - Account owner
- `LANÇAMENTO` - Transaction type
- `CATEGORIA` - Expense category
- `VALOR` - Transaction amount
- `DESCRIÇÃO` - Transaction description
- `ANALISE` - Analysis type (Receita/Despesa)
- `PROJETO/EVENTO` - Associated project
- `MOEDA` - Currency
- `CONCILIADO` - Reconciliation status

## 🌍 Multi-Language Support

The application supports three languages:
- **Portuguese (PORTUGUÊS)** - Default language
- **English (ENGLISH)** - International support
- **Russian (РУССКИЙ)** - Russian language support

Language selection is available in the sidebar and persists across sessions.

## 🤖 AI Integration

### **OpenAI GPT Features:**
- Financial data analysis
- Spending pattern insights
- Budget recommendations
- Anomaly detection
- Natural language queries

### **Pygwalker Analytics:**
- Interactive data exploration
- Custom visualizations
- Advanced filtering
- Real-time data analysis

## 🔐 Security Features

- **Secure Authentication** - User login with session management
- **Encrypted Cookies** - Secure session storage
- **Google Cloud Security** - OAuth2 authentication
- **API Key Protection** - Secure credential management

## 🛠️ Configuration

### **Environment Variables:**
- `GOOGLE_APPLICATION_CREDENTIALS` - Google Cloud credentials
- `OPENAI_API_KEY` - OpenAI API access
- `STREAMLIT_SERVER_PORT` - Application port

### **Google Sheets Setup:**
1. Create a new Google Sheets document
2. Set up the required worksheets
3. Configure API access permissions
4. Update secrets with sheet ID and name

## 📈 Usage Examples

### **Adding a Transaction:**
1. Navigate to "Lançamentos" page
2. Select account and category
3. Enter amount and description
4. Save transaction

### **Viewing Balances:**
1. Go to "Saldos" page
2. View real-time account balances
3. Analyze spending patterns
4. Export data if needed

### **AI Analysis:**
1. Access "IA" page
2. Upload financial data
3. Get AI-powered insights
4. Review recommendations

## 🚀 Deployment

### **Streamlit Cloud:**
1. Connect your GitHub repository
2. Configure secrets in Streamlit Cloud
3. Deploy automatically

### **Local Deployment:**
```bash
streamlit run LYNCE.py --server.port 8501
```

### **Docker Deployment:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "LYNCE.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### **Development Setup:**
```bash
git clone https://github.com/Purcineli/Lynce_Finance.git
cd Lynce_Finance
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run LYNCE.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web framework
- **Google Sheets API** - For cloud data storage
- **OpenAI** - For AI-powered insights
- **Pygwalker** - For interactive data analysis
- **Plotly** - For beautiful visualizations

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code examples

## 🔄 Version History

- **v1.0.0** (2025-01-07) - Initial release
  - Core financial management features
  - Multi-language support
  - Google Sheets integration
  - AI-powered insights
  - Interactive analytics

---

**Made with ❤️ for better financial management**
