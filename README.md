# HUGMAN Character Generator

A 3D character generation system that creates animated human models from text descriptions using AI and 3D modeling.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- At least 4GB RAM available

### Installation & Run
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/hugman-character-generator.git
cd hugman-character-generator

# Build and run with Docker
docker-compose up --build

# Open your browser to: http://localhost:5001
```

## 🎯 Features

- **Text-to-Character**: Generate 3D characters from natural language descriptions
- **AI-Powered**: Uses LLM models for character attribute generation
- **3D Animation**: Supports animated characters with actions
- **Web Interface**: Modern web-based 3D viewer
- **Cross-Platform**: Works on Windows, Mac, and Linux via Docker

## 📁 Project Structure

```
├── animations/           # Animation and web server files
│   ├── web_server.py    # Main Flask web server
│   ├── animation_viewer.html  # 3D viewer interface
│   └── text2animations.py     # Animation generation
├── data/                # Character assets
│   ├── clothes/         # Clothing items
│   ├── hair/           # Hair styles
│   └── skins/          # Skin textures
├── llm.py              # AI character generation
├── character_pipeline_viewer.py  # Main pipeline
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
└── requirements.txt    # Python dependencies
```

## 🎮 Usage

1. **Start the application**: `docker-compose up --build`
2. **Open browser**: Navigate to `http://localhost:5001`
3. **Enter description**: Type a character description (e.g., "A young Asian woman in a business suit")
4. **Generate**: Click "Generate" to create your 3D character
5. **View**: Interact with the 3D model in the viewer

## 🔧 Configuration

### Environment Variables
- `PYTHONPATH`: Python path (default: `/app`)
- `FLASK_APP`: Flask application file (default: `animations/web_server.py`)
- `FLASK_ENV`: Flask environment (default: `production`)

### Port Configuration
To change the port, modify `docker-compose.yml`:
```yaml
ports:
  - "YOUR_PORT:5001"
```

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "5002:5001"
```

**Permission issues (Linux/Mac):**
```bash
sudo chown -R $USER:$USER generated_characters output animations data
```

**Memory issues:**
- Increase Docker memory limit in Docker Desktop settings
- Or run with: `docker run -m 4g -p 5001:5001 hugman-character-generator`

### Viewing Logs
```bash
# View container logs
docker-compose logs -f
```

## 🛠️ Development

### Local Development
```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/hugman-character-generator.git
cd hugman-character-generator

# Install dependencies
pip install -r requirements.txt

# Run locally
python animations/web_server.py
```

### Docker Development
```bash
# Run with source code mounted
docker run -p 5001:5001 -v $(pwd):/app hugman-character-generator
```

## 📦 Docker Commands

```bash
# Build image
docker build -t hugman-character-generator .

# Run container
docker run -p 5001:5001 hugman-character-generator

# Stop container
docker-compose down

# View logs
docker-compose logs -f
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MakeHuman for 3D character modeling
- Ollama for LLM integration
- Three.js for 3D web rendering
- Flask for web framework

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the Docker README for detailed setup instructions
