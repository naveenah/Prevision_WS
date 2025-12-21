# BrandForge AI

An AI-powered brand building assistant that guides founders through a structured 90-day brand development process.

## 🚀 Features

- **AI-Powered Strategy**: Uses Google Gemini 2.5 Flash to generate vision, mission, and positioning
- **Brand Identity System**: AI-generated colors, typography, and messaging guide
- **90-Day Launch Plan**: Week-by-week roadmap customized for your brand type (SaaS, D2C, Agency)
- **KPI Dashboard**: Interactive projections with 13-week forecasting
- **AI Refinement Loop**: Iterate and improve content with natural language feedback
- **Demo Mode**: Pre-filled examples for quick exploration (3 complete brands)
- **Complete Export**: Download playbook (Markdown), data (CSV), and ZIP package
- **Production Ready**: Docker support, Streamlit Cloud config, full test coverage

## 🛠️ Tech Stack

- **Frontend**: Streamlit 1.40+
- **AI Orchestration**: LangGraph 0.2+
- **AI Model**: Google Gemini 2.5 Flash via LangChain
- **Data Processing**: Pandas, Plotly
- **State Management**: TypedDict with auto-save
- **Export**: Markdown, CSV, ZIP packages
- **Testing**: 44 tests (100% passing)
- **Deployment**: Docker, Streamlit Cloud ready

## 📦 Quick Start

### Automated Setup (Recommended)
```bash
git clone <your-repo-url>
cd BrandForge-AI
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create virtual environment
- Install dependencies
- Create .env file
- Run tests
- Verify configuration

### Manual Setup
```bash
# 1. Clone and navigate
git clone <your-repo-url>
cd BrandForge-AI

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
nano .env  # Add your GOOGLE_API_KEY
```

### Getting Your Gemini API Key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
### Local Development
```bash
# Activate virtual environment
source venv/bin/activate

# Start application
streamlit run main.py

# Access at http://localhost:8501
```

### Docker Deployment
```bash
# Quick start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

### Workflow
1. **Try Demo Mode**: Load pre-filled examples (FlowSync AI, EcoBloom, Quantum Creative)
2. **Brand Foundations**: Enter company details, generate vision/mission/values
3. *Dockerfile                   # Docker container configuration
├── docker-compose.yml           # Docker Compose setup
├── setup.sh                     # Development setup script
├── setup_production.sh          # Production setup script
├── .env.example                 # Environment template
├── modules/
│   ├── state.py                 # BrandState schema (TypedDict)
│   ├── graph_nodes.py           # LangGraph workflow nodes
│   ├── langchain_agents.py      # AI agent functions (Gemini)
│   ├── demo_data.py             # Demo mode sample data
│   └── utils.py                 # Helper utilities & exports
├── templates/
│   ├── prompts.py               # AI prompts library
│   └── launch_plan_template.py  # 90-day plan templates
├── tests/
│   ├─All Phases Complete (10/10)

**Phase 1-2: Foundation & API Integration**
- [x] Project structure & state management
- [x] Gemini 2.5 Flash API integration
- [x] AI-powered content generation
- [x] Brand foundations (vision, mission, values)
- [x] Positioning & competitor analysis

**Phase 3: LangGraph Workflow**
- [x] Workflow orchestration with LangGraph
- [x] 5-step sequential workflow
- [x] State graph compilation
- [x] Progress tracking & prerequisites

**Phase 4: Brand Identity**
- [x] Color palette generation
- [x] Typography recommendations
- [x] Brand messaging guide
- [x] Complete identity system

**Phase 5: Launch Planning**
- [x] 90-day customized roadmaps
- [x] Brand-type specific templates (SaaS, D2C, Agency)
- [x] 13-week task breakdown
- [x] CSV export functionality

**Phase 6: KPI Dashboard**
- [x] Interactive projections (13 weeks)
- [x] Revenue & visitor forecasting
- [x] Growth rate modeling
- [x] CSV/JSON export

**Phase 7: Export & Polish**
- [x] Markdown playbook generation
- [x] Complete ZIP package export
- [x] Google Sheets formula templates
- [x] Multi-format exports

**Phase 8: AI Refinement**
- [x] Content refinement with feedback
- [x] Alternative version generation
- [x] Version comparison metrics
- [x] Refinement history tracking

**Phase 9: Testing & UX**
- [x] Comprehensive test suite (44/44 passing)
- [x] Key Features

### 🤖 AI-Powered Generation
- **Vision & Mission**: Aspirational statements tailored to your brand
- **Core Values**: 5 values with detailed descriptions
- **Positioning**: Unique market positioning statement
- **Identity**: Complete brand system (colors, fonts, messaging)
- **Launch Plan**: Customized 13-week roadmap with specific tasks
- **KPI Projections**: Financial forecasting with growth modeling

### 🔄 AI Refinement Loop
- **Natural Language Feedback**: Improve any content with simple instructions
- **Alternative Versions**: Generate 3 unique variations of any text
- **Version Comparison**: Track changes and improvements
- **History Tracking**: Keep record of all refinements

### 🎬 Demo Mode
- **FlowSync AI**: SaaS automation platform example
- **EcoBloom Organics**: D2C wellness brand example
- **Quantum Creative**: Creative agency example
- **One-Click Load**: Instant exploration without setup

### 📤 Export Options
- **Markdown Playbook**: Complete brand strategy document
- **CSV Data**: Launch plan and KPI projections
- **ZIP Package**: All assets in one download
- *🚀 Deployment

### Quick Deploy Options

**Streamlit Cloud (Recommended):**
```bash
# Push to GitHub
git push origin main

# Deploy at share.streamlit.io
# Add GOOGLE_API_KEY in Secrets
```

**Docker:**
```bash
# Build and run
docker-compose up -d
```

**Cloud Platforms:**
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure Container Apps

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 🧪 Testing

```bash
# Run all tests
for test in tests/test_phase*.py; do python "$test"; done

# Run specific phase test
python tests/test_phase9_integration.py

# Test results: 44/44 passing (100%)
```

## 📚 Documentation

- **[Setup Guide](docs/SETUP_GUIDE.md)**: Development environment setup
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment instructions
- **[Test Summary](docs/TEST_SUMMARY.md)**: Complete test coverage report
- **[Phase Documentation](docs/)**: Detailed implementation docs for each phase

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

See [LICENSE.md](LICENSE.md)

## 🙏 Acknowledgments

- **Built with**: [Streamlit](https://streamlit.io/) - Interactive web framework
- **Powered by**: [Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/) - AI generation
- **Orchestrated with**: [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow management
- **AI Framework**: [LangChain](https://www.langchain.com/) - LLM integration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: See `/docs` folder
- **Questions**: Open a discussion or issue

---

**Current Version**: 1.0.0 (Phase 10 Complete)  
**Last Updated**: December 21, 2025  
**Status**: ✅ Production Ready

---

## 🌟 What's Next?

BrandForge AI is complete and production-ready! Future enhancements could include:
- Multi-language support
- Team collaboration features
- Advanced analytics dashboard
- Integration with design tools
- Mobile app version

**Ready to build your brand? Get started now!** 🚀**
- [x] **Foundation builder (Vision/Mission/Values)**
- [x] **Positioning statement generator**
- [x] **Competitor analysis**
- [x] **Brand identity generator**

### 🚧 In Progress (Phase 3)
- [ ] LangGraph workflow orchestration
- [ ] State graph compilation
- [ ] Node-based processing

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
