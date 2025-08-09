# 🎬 Short Video Generator

An automated AI-powered system for generating and uploading short videos to multiple social media platforms. Perfect for content creators, marketers, and anyone looking to automate their video content pipeline.

## ✨ Features

- **AI-Powered Content Generation**: Uses Stable Diffusion and other AI models to create engaging video content
- **Multi-Platform Upload**: Automatically uploads to YouTube, Instagram, and TikTok
- **Smart Scheduling**: Intelligent content scheduling and optimal upload timing
- **Web Dashboard**: Beautiful web interface for monitoring and controlling the system
- **CLI Interface**: Command-line tools for automation and scripting
- **Database Management**: Persistent storage for content and upload tracking
- **Modular Architecture**: Easy to extend and customize

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for video processing)
- GPU recommended (for faster AI generation)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd short-generator
   ```

2. **Run the installation script**
   ```bash
   python install.py
   ```

3. **Configure your environment**
   ```bash
   # Edit the .env file with your settings
   cp config.env.example .env
   # Edit .env with your API keys and preferences
   ```

4. **Test the installation**
   ```bash
   python test_system.py
   ```

## 🎯 Usage

### Command Line Interface

The system provides a comprehensive CLI for all operations:

```bash
# Generate new content
python cli.py generate --count 5 --theme cute_animals

# List all content
python cli.py list --limit 20

# Upload content to social media
python cli.py upload --content-id idea_123

# Show system status
python cli.py status

# Get help
python cli.py --help
```

### Web Dashboard

Start the web dashboard for a visual interface:

```bash
python main.py
```

Then open your browser to `http://localhost:8000`

### Programmatic Usage

```python
from short_generator import ShortVideoGenerator

# Create generator instance
generator = ShortVideoGenerator()

# Initialize system
await generator.initialize()

# Generate daily content
await generator.generate_daily_content()

# Run upload cycle
await generator.run_upload_cycle()
```

## ⚙️ Configuration

### Environment Variables

Key configuration options in your `.env` file:

```bash
# Content Generation
DAILY_VIDEO_COUNT=3
VIDEO_DURATION=15
VIDEO_RESOLUTION=1080x1920

# AI Models
USE_GPU=true
SD_MODEL=runwayml/stable-diffusion-v1-5
VIDEO_MODEL=damo-vilab/text-to-video-zero

# Social Media APIs
YOUTUBE_API_KEY=your_key_here
INSTAGRAM_USERNAME=your_username
TIKTOK_ACCESS_TOKEN=your_token_here

# Web Dashboard
WEB_HOST=0.0.0.0
WEB_PORT=8000
```

### Content Themes

The system supports multiple content themes:

- `cute_animals` - Adorable animal content
- `funny_pets` - Humorous pet videos
- `heartwarming_stories` - Emotional content
- `educational_facts` - Informative videos
- `seasonal_content` - Time-based themes

## 🏗️ Architecture

### Core Components

- **Content Agent**: Generates video ideas and scripts using AI
- **Video Agent**: Creates videos using Stable Diffusion and video models
- **Audio Agent**: Adds background music and sound effects
- **Upload Agent**: Handles social media platform uploads
- **Scheduler**: Manages content timing and upload schedules
- **Database Manager**: Handles data persistence and retrieval

### Data Flow

1. **Content Generation**: AI generates creative video ideas
2. **Video Creation**: Stable Diffusion creates video content
3. **Audio Enhancement**: Background music and effects added
4. **Quality Check**: Content validated and optimized
5. **Scheduling**: Content queued for optimal upload times
6. **Multi-Platform Upload**: Automated upload to all platforms
7. **Analytics**: Performance tracking and reporting

## 🔌 Social Media Integration

### YouTube

- Automated video uploads
- Custom titles, descriptions, and tags
- Privacy and category settings
- Analytics integration

### Instagram

- Reels and story uploads
- Caption and hashtag optimization
- Engagement tracking
- Session management

### TikTok

- Video uploads with trending sounds
- Hashtag optimization
- Engagement metrics
- Content scheduling

## 📊 Monitoring & Analytics

### Web Dashboard Features

- Real-time system status
- Content generation metrics
- Upload success rates
- Platform performance
- Queue management
- Manual content generation triggers

### Logging & Debugging

- Comprehensive logging system
- Error tracking and reporting
- Performance monitoring
- Debug mode for development

## 🛠️ Development

### Project Structure

```
short-generator/
├── agents/           # AI agents for different tasks
├── config/          # Configuration and settings
├── utils/           # Utility functions and helpers
├── web/             # Web dashboard and API
├── cli.py           # Command line interface
├── main.py          # Main application entry point
├── install.py       # Installation script
└── requirements.txt # Python dependencies
```

### Adding New Features

1. **New Content Themes**: Extend the `ContentAgent` class
2. **Additional Platforms**: Implement new upload methods in `UploadAgent`
3. **Custom AI Models**: Modify the video and content generation agents
4. **Enhanced Analytics**: Extend the database and dashboard

### Testing

```bash
# Run system tests
python test_system.py

# Run specific component tests
python -m pytest tests/

# Test CLI commands
python cli.py status
```

## 🚨 Troubleshooting

### Common Issues

**AI Models Not Loading**
- Check GPU drivers and CUDA installation
- Verify model download paths
- Use CPU fallback if GPU unavailable

**Upload Failures**
- Verify API credentials in `.env`
- Check rate limits and quotas
- Review platform-specific requirements

**Video Generation Issues**
- Ensure FFmpeg is installed
- Check available disk space
- Verify video codec support

### Getting Help

1. Check the logs in the `logs/` directory
2. Review the configuration in `.env`
3. Run `python cli.py status` for system health
4. Check the web dashboard for detailed metrics

## 📈 Performance Optimization

### GPU Acceleration

- Enable CUDA for faster AI generation
- Use appropriate model sizes for your hardware
- Batch processing for multiple videos

### Content Pipeline

- Parallel content generation
- Intelligent queuing and scheduling
- Background processing for non-blocking operations

### Storage Management

- Automatic cleanup of temporary files
- Configurable backup retention
- Efficient video compression

## 🔒 Security & Privacy

- Environment-based configuration
- Secure API key management
- No hardcoded credentials
- Configurable access controls

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on:

- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## 📞 Support

- **Documentation**: This README and inline code comments
- **Issues**: GitHub issue tracker
- **Discussions**: GitHub discussions for questions and ideas
- **Wiki**: Additional documentation and tutorials

## 🎉 Acknowledgments

- Stable Diffusion team for the amazing AI models
- FastAPI for the excellent web framework
- All contributors and users of this project

---

**Happy Video Generating! 🎬✨**
