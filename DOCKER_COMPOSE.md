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
- **Port**: 8000
- **Health Check**: `http://localhost:8000/`
- **Volumes**: 
  - `./playbooks:/app/playbooks` (playbook files)

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

## Troubleshooting

### Port already in use
If ports 8000 or 4173 are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

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

