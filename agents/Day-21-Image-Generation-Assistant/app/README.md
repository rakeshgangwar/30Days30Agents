# Image Generation Assistant

A powerful AI-powered image generation assistant built with **Pydantic AI** that helps you create, enhance, and manage AI-generated images using **OpenAI's DALL-E** and **Fal.ai** models.

## 🎨 Features

### Core Capabilities
- **Multi-Provider Support**: Generate images using both OpenAI DALL-E and Fal.ai models
- **Text-to-Image Generation**: Create images from detailed text descriptions
- **Prompt Enhancement**: AI-powered prompt refinement optimized for each provider
- **Parameter Control**: Fine-tune style, aspect ratio, quality, and advanced parameters
- **Image Management**: Automatic saving, organized storage, and searchable history
- **Image Processing**: Upscaling and variation generation
- **Multiple Interfaces**: Web UI, CLI commands, and conversational chat mode

### Advanced Features
- **Smart Prompt Enhancement**: Provider-optimized prompt improvement using GPT-4
- **Style Templates**: Pre-defined artistic styles compatible with both providers
- **Generation History**: Track and search through all your generated images
- **Provider Filtering**: Filter history and operations by provider
- **Rate Limiting**: Built-in API rate limiting to manage costs
- **Queue Monitoring**: Real-time Fal.ai queue status and progress tracking
- **Error Handling**: Robust error handling with helpful suggestions
- **Metadata Storage**: Complete generation metadata for each image

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- At least one API key: OpenAI API key and/or Fal.ai API key

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd ImageAssistant
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up your API keys:**
```bash
python main.py setup
```
*Or create a `.env` file manually with your API keys:*
```
OPENAI_API_KEY=your_openai_api_key_here
FAL_KEY=your_fal_api_key_here
```

4. **Start using the assistant:**

**Web UI (Recommended):**
```bash
python main.py
# Select option 1 for Web UI
```

**Or launch directly:**
```bash
python main.py web
```

**Command Line:**
```bash
python main.py generate "A serene mountain landscape at sunset"
```

## 🌐 Web Interface

The **Gradio Web UI** provides a beautiful, intuitive interface for all features:

### Features
- **🎨 Generate Images**: Full-featured image generation with real-time model info
- **✨ Enhance Prompts**: AI-powered prompt improvement with provider optimization
- **📚 History**: View and search your generation history with provider filtering
- **❓ Help & Info**: Complete documentation and usage guides

### Launch Options
```bash
# Launch with default settings (localhost:7860)
python main.py web

# Launch with public sharing
python main.py web --share

# Launch on different port
python main.py web --port 8080

# Launch with authentication
python main.py web --auth "username:password"

# Launch on all interfaces
python main.py web --host 0.0.0.0
```

### Web UI Screenshots
The web interface includes:
- **Dynamic UI**: Interface adapts based on selected model (OpenAI vs Fal.ai)
- **Real-time Feedback**: Progress indicators and generation status
- **Model Information**: Detailed model capabilities and parameter info
- **Advanced Parameters**: Fal.ai specific controls (seed, guidance, steps)
- **API Status**: Real-time API key configuration status
- **Cross-tab Integration**: Copy enhanced prompts to generation tab

## 💻 Usage

### Web Interface (Recommended)

1. **Launch Web UI**: Run `python main.py` and select Web UI
2. **Select Model**: Choose from OpenAI DALL-E or Fal.ai models
3. **Enter Prompt**: Describe your desired image
4. **Customize Settings**: Adjust style, size, and advanced parameters
5. **Generate**: Click generate and watch the magic happen!

### Command Line Interface

#### Generate Images

**OpenAI DALL-E:**
```bash
# Basic generation with DALL-E 3
python main.py generate "A futuristic city at night" --model dall-e-3

# DALL-E 2 with multiple images
python main.py generate "A cat wearing a wizard hat" \
  --model dall-e-2 \
  --style natural \
  --count 4
```

**Fal.ai Models:**
```bash
# Fast SDXL with advanced parameters
python main.py generate "A dragon in a mystical forest" \
  --model fal-ai/fast-sdxl \
  --style photographic \
  --size landscape \
  --seed 12345 \
  --guidance 7.5 \
  --steps 50 \
  --negative "blurry, low quality"

# Flux model for high quality
python main.py generate "A serene landscape" \
  --model fal-ai/flux/schnell \
  --size square_hd
```

#### Interactive Chat Mode
```bash
python main.py chat
```

Then chat naturally:
- "Generate a sunset over mountains using fal-ai"
- "Make it more photorealistic"
- "Show me my recent Fal.ai images"
- "Use seed 12345 for the next generation"

### Available Models

#### OpenAI DALL-E
- **dall-e-3**: Latest model, best quality, 1 image per request
- **dall-e-2**: Faster model, up to 10 images per request

#### Fal.ai Models
- **fal-ai/fast-sdxl**: Fast SDXL, supports negative prompts, many styles
- **fal-ai/flux/schnell**: Fast Flux model, excellent quality
- **fal-ai/flux/dev**: Premium Flux model (requires subscription)
- **fal-ai/stable-diffusion-v3-medium**: Latest Stable Diffusion
- **fal-ai/aura-flow**: Creative flow model with unique style

### Available Styles

#### Universal Styles (Both Providers)
- `photorealistic`: High-detail photography style
- `artistic`: Creative and expressive
- `cartoon`: Animated, colorful style
- `digital_art`: Modern digital art
- `vintage`: Retro, nostalgic style
- `minimalist`: Simple, clean lines
- `cyberpunk`: Neon, futuristic, dark
- `fantasy`: Magical, ethereal

#### Fal.ai Specific Styles
- `anime`: Japanese animation style
- `photographic`: Realistic photography
- `comic_book`: Bold comic book style
- `line_art`: Black and white, sketch
- `neon_punk`: Vibrant neon colors

### Image Sizes

#### OpenAI DALL-E
- `1024x1024`: Square format
- `1792x1024` or `landscape`: Wide format
- `1024x1792` or `portrait`: Tall format
- `512x512`, `256x256`: Smaller formats (DALL-E 2)

#### Fal.ai Models
- `square`: Standard square format
- `portrait`: Vertical format
- `landscape`: Horizontal format
- `square_hd`: High-definition square

## 🏗️ Architecture

The Image Generation Assistant is built using **Pydantic AI** and follows a modular architecture with multi-provider support:

### Core Components

1. **Agent (`agent.py`)**: Main Pydantic AI agent with provider-aware routing
2. **Services (`services.py`)**: 
   - `UnifiedImageGenerationService`: Routes requests to appropriate providers
   - `ImageGenerationService`: OpenAI DALL-E integration
   - `FalImageGenerationService`: Fal.ai model integration with queue monitoring
3. **Models (`models.py`)**: Provider-agnostic Pydantic data models
4. **Configuration (`config.py`)**: Multi-provider configuration management
5. **CLI (`cli.py`)**: Rich command-line interface with provider support
6. **Web UI (`gradio_ui.py`)**: Beautiful Gradio web interface

### Interface Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   CLI           │    │   Chat Mode     │
│   (Gradio)      │    │   (Typer/Rich)  │    │   (Interactive) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │              Pydantic AI Agent                      │
         │         (Multi-Provider Routing)                    │
         └─────────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │          Unified Image Generation Service           │
         └─────────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │    OpenAI Service     │      Fal.ai Service         │
         │    - DALL-E 2/3       │      - Fast SDXL            │
         │    - Direct API       │      - Flux Models          │
         │    - Prompt Revision  │      - Queue Monitoring     │
         └─────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ImageAssistant/
├── agent-spec.md          # Original specification
├── requirements.txt       # Python dependencies (includes gradio)
├── config.py             # Multi-provider configuration
├── models.py             # Provider-agnostic data models
├── services.py           # Provider services and unified routing
├── agent.py              # Main Pydantic AI agent
├── cli.py                # Enhanced CLI with provider support
├── gradio_ui.py          # Gradio Web UI (NEW!)
├── main.py               # Application entry point with interface selection
├── README.md             # This file
├── .env                  # Environment variables (create this)
├── generated_images/     # Generated images (auto-created)
└── metadata/             # Generation metadata (auto-created)
```

## 🔧 Configuration

The application supports both providers through environment variables in `.env`:

```env
# API Keys (at least one required)
OPENAI_API_KEY=your_openai_api_key_here
FAL_KEY=your_fal_api_key_here

# Optional Fal.ai configuration
FAL_ENABLE_QUEUE_MONITORING=true
FAL_MAX_QUEUE_WAIT_TIME=300

# Storage and other settings
IMAGE_STORAGE_DIR=generated_images
CLEANUP_AFTER_DAYS=30
RATE_LIMIT_RPM=50
```

## 📊 Example Workflows

### 1. **Web UI Workflow:**
1. Run `python main.py` and select Web UI
2. Choose a model (e.g., `fal-ai/fast-sdxl`)
3. Enter prompt: "A cyberpunk street scene"
4. Select style: "neon_punk"
5. Set advanced parameters (seed: 42, guidance: 8.0)
6. Click "Generate Images"
7. View results in gallery, copy seed for reproducible results

### 2. **Cross-Provider Comparison:**
```bash
# Generate with DALL-E 3
python main.py generate "A mystical forest" --model dall-e-3

# Generate same prompt with Fal.ai
python main.py generate "A mystical forest" --model fal-ai/fast-sdxl
```

### 3. **Advanced Fal.ai Generation:**
```bash
python main.py generate "A cyberpunk street scene" \
  --model fal-ai/fast-sdxl \
  --style neon-punk \
  --size landscape \
  --seed 42 \
  --guidance 8.0 \
  --steps 40 \
  --negative "people, cars, blurry"
```

### 4. **Web UI with Authentication:**
```bash
python main.py web --auth "admin:secret123" --port 8080 --share
```

## 🤖 Pydantic AI Integration

This project showcases advanced **Pydantic AI** features with multi-provider support:

### Agent Definition
- Provider-aware routing based on model selection
- Type-safe dependencies with `UnifiedImageGenerationService`
- Dynamic system prompts with provider-specific guidance

### Multi-Provider Architecture
- Unified interface for different image generation providers
- Provider-specific parameter validation and conversion
- Intelligent routing based on model names

### Advanced Tool Usage
- Provider-aware prompt enhancement
- Contextual parameter suggestions
- Cross-provider comparison capabilities

### Queue Monitoring (Fal.ai)
- Real-time queue position tracking
- Progress logging and user feedback
- Graceful handling of long-running operations

## 🛠️ Development

### Adding New Interface Components

1. **Gradio Components**: Add new tabs or features in `gradio_ui.py`
2. **CLI Commands**: Add new commands in `cli.py`
3. **Agent Tools**: Add new tools in `agent.py`

### Adding New Providers

1. **Create Provider Service**: Add a new service class in `services.py`
2. **Update Models**: Add provider-specific enums and parameters
3. **Extend Configuration**: Add provider config in `config.py`
4. **Update Agent**: Add routing logic in `agent.py`
5. **Update UI**: Add provider support in `gradio_ui.py`

## 🌐 Deployment

### Local Development
```bash
python main.py web
```

### Public Sharing (Gradio)
```bash
python main.py web --share
```

### Production Deployment
```bash
# With authentication and custom port
python main.py web --auth "admin:password" --host 0.0.0.0 --port 8080
```

## 💰 Cost Considerations

### OpenAI DALL-E Pricing
- DALL-E 3: ~$0.04-0.08 per image
- DALL-E 2: ~$0.02-0.04 per image

### Fal.ai Pricing
- Generally more cost-effective
- Pay-per-use model
- Some premium models require subscription

### Cost Management Features
- Built-in rate limiting
- Provider comparison for cost optimization
- Queue monitoring to avoid unnecessary requests
- Web UI shows cost-relevant model information

## 🚨 Important Notes

- **API Keys**: At least one provider API key is required
- **Rate Limits**: Both providers have rate limits; built-in limiting helps manage usage
- **Storage**: Images are saved locally; configure cleanup policies as needed
- **Queue Times**: Fal.ai models may have queue wait times during peak usage
- **Content Policies**: Both providers have content policies; prompts may be rejected

## 🆚 Provider Comparison

| Feature | OpenAI DALL-E | Fal.ai |
|---------|---------------|---------|
| **Quality** | Excellent | Very Good to Excellent |
| **Speed** | Fast | Fast (with queues) |
| **Styles** | Limited (2) | Many (8+ per model) |
| **Advanced Params** | No | Yes (seed, guidance, steps) |
| **Negative Prompts** | No | Yes (select models) |
| **Multiple Images** | Up to 10 (DALL-E 2) | Up to 4 |
| **Cost** | Higher | Generally Lower |
| **Queue System** | No | Yes |
| **Web UI Support** | ✅ Full | ✅ Full |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add provider support or new features
4. Test with both CLI and Web UI
5. Submit a pull request

## 📄 License

This project is open-source and available under the MIT License.

## 🙏 Acknowledgments

- **Pydantic AI** for the excellent agent framework
- **OpenAI** for the DALL-E image generation models
- **Fal.ai** for fast and affordable AI model hosting
- **Gradio** for the beautiful web interface framework
- **Typer** and **Rich** for the elegant CLI interface

---

**Happy Image Generating with Multiple Interfaces! 🎨✨🌐** 