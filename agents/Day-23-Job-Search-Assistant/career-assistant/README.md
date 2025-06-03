# 🚀 AI-Powered Career Assistant

A sophisticated multi-agent career application assistant powered by **PydanticAI** with **Model Context Protocol (MCP)** integration for real-time web research and intelligent application generation.

## ✨ Features

### 🤖 Multi-Agent Intelligence
- **Resume Analysis Agent**: AI-powered extraction and analysis of resumes
- **Job Analysis Agent**: Intelligent job posting analysis with real-time company research
- **Application Generation Agent**: Tailored resume and cover letter creation
- **Interview Prep Agent**: STAR method responses and company-specific preparation

### 🌐 Real-Time Web Research
- **Exa Search Integration**: Advanced web search for company research
- **Firecrawl Scraping**: Intelligent web scraping for job postings and company data
- **Live Company Intelligence**: Up-to-date company news, culture, and insights

### 📄 Intelligent Document Processing
- Multi-format resume parsing (PDF, DOCX, TXT)
- ATS-optimized content generation
- Industry-specific keyword matching
- Skills gap analysis and recommendations

### 🎯 Personalized Application Materials
- Tailored resumes for specific job postings
- Compelling cover letters with company research
- Interview preparation with STAR responses
- Application strategy recommendations

## 🛠️ Prerequisites

1. **Python 3.12+**
2. **Node.js 18+** (for MCP servers)
3. **API Keys**:
   - OpenAI API key
   - Exa API key (for web search)
   - Firecrawl API key (for web scraping)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and setup
git clone <repository-url>
cd career-assistant

# Initialize with uv
uv init
uv add pydantic-ai python-dotenv rich pypdf2 python-docx beautifulsoup4 httpx requests

# Or install dependencies
uv sync
```

### 2. Environment Setup

```bash
# Copy environment template
cp env_example.txt .env

# Edit .env with your API keys
# OPENAI_API_KEY=your_openai_api_key_here
# EXA_API_KEY=your_exa_api_key_here  
# FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### 3. Verify Setup

```bash
python setup_mcp.py
```

This will check:
- ✅ Node.js installation
- ✅ MCP server availability
- ✅ Environment variables
- ✅ Dependencies

### 4. Run the Assistant

```bash
# Option 1: Use main entry point (recommended)
python main.py

# Option 2: Run directly
python streamlined_cli.py
```

## 🔧 API Keys Setup

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an API key
3. Add to `.env` as `OPENAI_API_KEY`

### Exa API Key
1. Visit [Exa.ai](https://exa.ai/)
2. Sign up and get your API key
3. Add to `.env` as `EXA_API_KEY`

### Firecrawl API Key
1. Visit [Firecrawl](https://firecrawl.dev/)
2. Sign up and get your API key  
3. Add to `.env` as `FIRECRAWL_API_KEY`

## 🎯 Usage Flow

### 1. 📄 Resume Upload & AI Analysis
- Upload your resume (PDF, DOCX, or TXT)
- AI agents extract:
  - Contact information
  - Skills (technical, soft, domain)
  - Work experience with achievements
  - Education and certifications

### 2. 💼 Job Intelligence Gathering
Choose from:
- **URL Scraping**: Paste job posting URL for automatic extraction
- **Manual Entry**: Input job details manually

The system will:
- Analyze job requirements and responsibilities
- Research the company using live web data
- Identify culture fit and interview insights

### 3. 🎨 AI-Generated Application Package
Receive:
- **Tailored Resume**: Optimized for the specific role
- **Custom Cover Letter**: Incorporating company research
- **Interview Preparation**: 
  - Common and role-specific questions
  - STAR method responses
  - Company insights for conversation

### 4. 📥 Export & Apply
- Download all materials as formatted documents
- Get strategic application advice
- Receive follow-up recommendations

## 🏗️ Architecture

### Multi-Agent System
```
┌─────────────────────────────────────────────────────────┐
│                Career Assistant Orchestrator            │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐│
│  │Resume Analysis│  │Job Analysis  │  │Application Gen  ││
│  │Agent          │  │Agent         │  │Agent            ││
│  └───────────────┘  └──────────────┘  └─────────────────┘│
│  ┌───────────────────────────────────────────────────────┐│
│  │           Interview Preparation Agent                 ││
│  └───────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────┤
│  MCP Integrations:                                      │
│  • Exa Search (Web Research)                            │
│  • Firecrawl (Web Scraping)                             │
└─────────────────────────────────────────────────────────┘
```

### Key Components

- **PydanticAI Agents**: Specialized AI agents with structured outputs
- **MCP Servers**: Model Context Protocol for external tool integration
- **Structured Data Models**: Type-safe data handling with Pydantic
- **Rich CLI Interface**: Beautiful terminal UI with progress indicators

## 🔍 Advanced Features

### Intelligent Skill Matching
- Keyword extraction and mapping
- Skill gap identification
- Proficiency level assessment
- Industry-specific recommendations

### ATS Optimization
- Keyword density optimization
- Format compatibility
- Section structure optimization
- Bullet point enhancement

### Company Research Intelligence
- Recent news and developments
- Culture and values analysis
- Competitive landscape insights
- Interview process intelligence

### STAR Method Generation
- Situation identification from experience
- Task clarification and context
- Action steps and methodologies
- Result quantification and impact

## 🛡️ Privacy & Security

- **Local Processing**: Resume analysis happens locally
- **API Security**: Secure API key management
- **No Data Storage**: No personal data stored permanently
- **Encrypted Transmission**: Secure communication with AI services

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**MCP Server Errors**:
```bash
# Reinstall Node.js packages
npx -y exa-mcp-server --help
npx -y firecrawl-mcp --help
```