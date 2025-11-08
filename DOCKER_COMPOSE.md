# Docker Compose Setup

This project includes Docker Compose configuration for running the entire application stack.

## Quick Start

Build and start all services:

```bash
docker-compose up --build
```

This will:
- Build and start the backend API on `http://localhost:8000`
- Build and start the frontend on `http://localhost:4173`
- Set up proper networking between services
- Configure health checks

## Services

### Backend (`heimdall-backend`)
- **Port**: 8000 (on host network)
- **Network Mode**: `host` - allows access to simulator/drone on host machine
- **Health Check**: `http://localhost:8000/`
- **Volumes**: 
  - `./playbooks:/app/playbooks` (playbook files)

**Note**: The backend uses `network_mode: host` to access the Parrot Sphinx simulator or physical drone running on the host machine. This allows the container to connect to services on `10.202.0.1` (default simulator IP) or other host network addresses.

### Frontend (`heimdall-frontend`)
- **Port**: 4173
- **Health Check**: `http://localhost:4173`
- **Environment Variables**:
  - `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)
  - `VITE_WS_URL`: WebSocket URL (default: `ws://localhost:8000`)

## Common Commands

### Start services in background
```bash
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f
```

### View logs for specific service
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop services
```bash
docker-compose down
```

### Rebuild and restart
```bash
docker-compose up --build --force-recreate
```

### Execute commands in containers
```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh
```

## Environment Variables

You can override environment variables by creating a `.env` file in the project root:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

Or pass them directly:

```bash
VITE_API_URL=http://custom-backend:8000 docker-compose up
```

## Network Configuration

### Host Network Mode

The backend service uses `network_mode: host` to access the Parrot Sphinx simulator or physical drone on the host network. This means:

- ✅ Backend can connect to simulator at `10.202.0.1` (default)
- ✅ Backend can access any service on the host network
- ✅ No port mapping needed (backend listens directly on host's port 8000)
- ⚠️ On macOS/Windows Docker Desktop: Uses the VM's network, not the physical host network

**For Linux**: Full host network access works perfectly.

**For macOS/Windows**: If you need to access a simulator on the physical host, you may need to:
1. Run the simulator inside the Docker VM, or
2. Use Docker Desktop's host networking features, or
3. Run backend directly on host (outside Docker) for simulator access

## Troubleshooting

### Port already in use
If port 8000 is already in use, stop the conflicting service or change the backend port in `backend/api/main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change port
```

Then update frontend `VITE_API_URL` to match.

### Frontend can't connect to backend
- Ensure backend is healthy: `curl http://localhost:8000/`
- Check backend logs: `docker-compose logs backend`
- Verify environment variables are set correctly

### Build failures
- Clear Docker cache: `docker-compose build --no-cache`
- Check Docker has enough resources allocated
- Ensure all dependencies are listed in `requirements.txt` and `package.json`

## Production Deployment

For production, consider:
1. Remove volume mounts for source code
2. Use environment-specific `.env` files
3. Set up proper reverse proxy (nginx/traefik)
4. Enable HTTPS
5. Configure proper CORS origins
6. Use Docker secrets for sensitive data

