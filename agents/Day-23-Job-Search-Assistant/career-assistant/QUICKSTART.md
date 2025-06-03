# 🚀 Quick Start Guide

## Get Started in 3 Minutes

### 1. ⚡ Install Dependencies
```bash
# Install dependencies using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. 🔑 Set Up OpenAI API Key
Create a `.env` file in the project root:
```bash
# Copy the example and add your key
cp env_example.txt .env

# Edit .env and add your OpenAI API key:
OPENAI_API_KEY=your_actual_api_key_here
```

### 3. 🎯 Try the Demo (No API Key Required)
```bash
# Run the example demonstration
uv run python example.py
# or
python example.py
```

### 4. 🚀 Run the Full Application
```bash
# Start the interactive CLI
uv run python main.py
# or  
python main.py
```

## 📋 First Time Setup

When you run the application for the first time, you'll be guided through creating your profile:

1. **Personal Information** - Name, email, contact details
2. **Skills & Experience** - Technical skills with proficiency levels
3. **Work History** - Previous jobs and achievements
4. **Career Goals** - Target roles and experience level

## 🎯 Main Features

### 1. **Job Match Analysis**
- Paste any job description
- Get compatibility score and recommendations
- Identify skill gaps and strengths

### 2. **Resume Optimization**
- Generate tailored bullet points
- Get ATS-friendly keywords
- Optimize for specific roles

### 3. **Cover Letter Generation**
- Create personalized cover letters
- Highlight relevant achievements
- Match company culture and values

### 4. **Interview Preparation**
- Get role-specific questions
- Practice behavioral scenarios
- Receive strategic preparation tips

### 5. **Job Posting Analysis**
- Break down requirements and responsibilities
- Identify key technologies and skills
- Get application strategy advice

## 💡 Pro Tips

- **Keep your profile updated** - Regular updates improve matching accuracy
- **Use specific job descriptions** - More details = better analysis
- **Quantify achievements** - Numbers make your profile stand out
- **Update career goals** - Keep target roles current with your aspirations

## 🛠️ Troubleshooting

### Import Errors
```bash
# Ensure all dependencies are installed
uv sync

# Check if core modules work
uv run python -c "import models, utils; print('✅ Core modules OK')"
```

### OpenAI API Issues
- Check your API key is set correctly in `.env`
- Verify you have credits/usage available
- Make sure the key has the right permissions

### Need Help?
- Check the full README.md for detailed documentation
- Run `python example.py` to test without API requirements
- Ensure you're using Python 3.11 or higher

---

**Ready to optimize your career applications!** 🎯 