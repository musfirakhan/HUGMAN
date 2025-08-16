# HUGMAN Character Generator - Docker Deployment

This guide explains how to deploy the HUGMAN Character Generator using Docker for cross-platform compatibility.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- At least 4GB of RAM available for the container

## Quick Start

### 1. Build and Run with Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 2. Manual Docker Build

```bash
# Build the image
docker build -t hugman-character-generator .

# Run the container
docker run -p 5001:5001 -v $(pwd)/generated_characters:/app/generated_characters -v $(pwd)/output:/app/output hugman-character-generator
```

## Accessing the Application

Once the container is running, open your web browser and navigate to:
```
http://localhost:5001
```

## File Structure

The Docker container maps the following directories:
- `./generated_characters` → `/app/generated_characters` (character data)
- `./output` → `/app/output` (generated models)
- `./animations` → `/app/animations` (animation files)
- `./data` → `/app/data` (asset data)

## Windows Deployment

### Using Docker Desktop for Windows

1. Install Docker Desktop for Windows
2. Enable WSL 2 backend (recommended)
3. Clone this repository
4. Open PowerShell or Command Prompt in the project directory
5. Run: `docker-compose up --build`

### Using WSL 2

1. Install WSL 2 and Docker
2. Clone the repository in WSL
3. Run: `docker-compose up --build`

## Troubleshooting

### Port Already in Use
If port 5001 is already in use, modify the `docker-compose.yml` file:
```yaml
ports:
  - "5002:5001"  # Change 5001 to 5002 or another port
```

### Permission Issues (Linux/Mac)
```bash
# Fix permissions for mounted volumes
sudo chown -R $USER:$USER generated_characters output animations data
```

### Memory Issues
If the container runs out of memory:
1. Increase Docker memory limit in Docker Desktop settings
2. Or run with more memory:
```bash
docker run -m 4g -p 5001:5001 hugman-character-generator
```

### Viewing Logs
```bash
# View container logs
docker-compose logs -f

# Or for manual Docker run
docker logs <container_id>
```

## Stopping the Application

```bash
# Stop with Docker Compose
docker-compose down

# Stop manual Docker container
docker stop <container_id>
```

## Development

For development, you can mount the source code:
```bash
docker run -p 5001:5001 -v $(pwd):/app hugman-character-generator
```

## Environment Variables

You can customize the deployment by setting environment variables:
- `PYTHONPATH`: Python path (default: `/app`)
- `FLASK_APP`: Flask application file (default: `animations/web_server.py`)
- `FLASK_ENV`: Flask environment (default: `production`)

## Notes

- The container uses Python 3.9 for compatibility
- All dependencies are automatically installed during build
- The application runs on port 5001 inside the container
- Generated files are persisted through volume mounts
