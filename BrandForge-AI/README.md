# BrandForge AI

An AI-powered brand building assistant that guides founders through a structured 90-day brand development process.

## 🚀 Features

- **AI-Powered Strategy**: Uses Google Gemini Pro 3 to generate vision, mission, and positioning
- **90-Day Launch Plan**: Week-by-week roadmap customized for your brand type
- **KPI Dashboard**: Interactive projections and Google Sheets integration
- **Complete Export**: Download your entire brand playbook as a ZIP file

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Orchestration**: LangGraph
- **AI Model**: Google Gemini 2.0 Flash (Pro 3) via LangChain
- **Data**: Pandas, Plotly

## 📦 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd BrandForge-AI
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API key:
```
GOOGLE_API_KEY=your_api_key_here
```

### Getting Your Gemini API Key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)
5. Paste it into your `.env` file

## 🎯 Usage

1. **Start the application**
```bash
streamlit run main.py
```

2. **Open in browser**
The app will automatically open at `http://localhost:8501`

3. **Follow the workflow**
- Start with Brand Foundations
- Generate AI recommendations
- Review and edit outputs
- Export your complete brand playbook

## 📁 Project Structure

```
BrandForge-AI/
├── main.py                      # Main Streamlit application
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create from .env.example)
├── modules/
│   ├── state.py                 # BrandState schema and management
│   ├── graph_nodes.py           # LangGraph workflow nodes
│   ├── langchain_agents.py      # AI agent functions
│   └── utils.py                 # Helper utilities
├── templates/
│   ├── prompts.py               # AI prompts
│   └── launch_plan_template.py  # 90-day plan structure
└── assets/
    └── styles.css               # Custom styling
```

## 🧪 Development Status

### ✅ Completed (Phase 0-1)
- [x] Project structure setup
- [x] BrandState schema implementation
- [x] Session state management
- [x] Auto-save functionality
- [x] Main UI framework
- [x] Navigation system
- [x] Progress tracking

### 🚧 In Progress (Phase 2)
- [ ] Gemini API integration
- [ ] LangChain agent functions
- [ ] Brand foundations generator
- [ ] Market analysis generator

### 📋 Planned
- [ ] LangGraph workflow (Phase 3)
- [ ] Complete UI pages (Phase 4-7)
- [ ] Advanced features (Phase 8)
- [ ] Testing & polish (Phase 9)
- [ ] Deployment (Phase 10)

## 🎨 Features by Phase

### Phase 1: Brand Foundations
- Company name, vision, mission
- Target audience definition
- Core values identification
- AI-generated brand strategy

### Phase 2: Identity & Assets
- Color palette recommendations
- Typography suggestions
- Brand messaging guide
- One-pager copy generation

### Phase 3: 90-Day Launch Plan
- Week-by-week task breakdown
- Editable calendar view
- CSV export functionality
- Brand-type specific customization

### Phase 4: KPI Dashboard
- Interactive projections
- Revenue forecasting
- Google Sheets formulas
- AI-powered insights

## 🤝 Contributing

This is an MVP prototype. Contributions welcome after initial release.

## 📄 License

See LICENSE.md

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini](https://deepmind.google/technologies/gemini/)
- Orchestrated with [LangGraph](https://github.com/langchain-ai/langgraph)

## 📞 Support

For issues or questions, please open a GitHub issue.

---

**Current Version**: 0.1.0  
**Last Updated**: December 21, 2025
