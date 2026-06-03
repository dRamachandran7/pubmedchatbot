# Railway Deployment Guide

## Prerequisites
- GitHub account with your repository pushed
- Railway account (free at railway.app)
- Environment variables ready

## Deployment Steps

### 1. Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up or log in with GitHub
3. Click "Create a New Project"
4. Select "Deploy from GitHub repo"
5. Authorize Railway to access your GitHub account
6. Select your `pubmedchatbot` repository

### 2. Railway Auto-Detection
Railway will automatically:
- Detect the `docker-compose.yml` file
- Identify backend (Node.js) and rag-service (Python) services
- Create separate deployments for each service

### 3. Configure Environment Variables

In the Railway dashboard, set these variables:

**For Backend Service:**
- `PORT`: 3000
- `PYTHON_RAG_SERVICE_URL`: Will be auto-populated by Railway's service discovery
  - Format: `http://rag-service:5000` (Railway auto-configures this)
- `NODE_ENV`: production

**For RAG Service:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `PUBMED_EMAIL`: Your PubMed email
- `PORT`: 5000

### 4. Set Up Service Discovery
Railway automatically configures environment variables for inter-service communication:
- Services can reference each other by name
- `rag-service` service is accessible as `http://rag-service:5000`
- `backend` service is accessible as `http://backend:3000`

### 5. Deploy
1. Commit your code and push to GitHub
2. Railway automatically deploys on push to main branch
3. Monitor deployment in the Railway dashboard
4. Once deployed, Railway provides a public URL for your backend

### 6. Connect Frontend
Update your frontend to use the public Railway backend URL:
- Get the public URL from Railway dashboard
- Set `VITE_API_URL` environment variable or update API calls
- Deploy frontend to Vercel with this URL

## Environment Variable Setup

### In Railway Dashboard

1. Go to your project
2. Select "backend" service → Settings → Variables
3. Add each variable from above
4. Repeat for "rag-service"

### Database & Data Persistence

Your `chroma/` database is automatically persisted in Railway:
- Located at `./data/chroma/`
- Persists between deployments
- If needed, you can add a volume in the docker-compose.yml

## Troubleshooting

### Service Communication Issues
- Ensure `PYTHON_RAG_SERVICE_URL` is set correctly
- Check logs in Railway dashboard for detailed errors
- Services should use service name, not localhost

### Missing Environment Variables
- All required env vars must be set in Railway dashboard
- Check logs for "undefined" or "null" errors

### Build Failures
- Check build logs in Railway
- Ensure Dockerfiles are correctly configured
- Verify all dependencies in package.json and requirements.txt

### Slow First Deployment
- First deployment includes dependency installation
- Subsequent deploys are faster with Docker layer caching

## Monitoring & Logs

In Railway Dashboard:
- **Logs**: Real-time application logs
- **Metrics**: CPU, Memory, Network usage
- **Deployments**: History of all deployments
- **Usage**: Track resource consumption

## Scaling & Limits

- Free tier: Suitable for development/testing
- Paid tier: For production with higher resource limits
- Railway bills based on resources used

## Frontend Deployment (Optional - Keep on Vercel)

If deploying frontend separately to Vercel:

1. Create `frontend/.env.production`
```
VITE_API_URL=https://your-railway-backend-url.railway.app
```

2. Update `frontend/src/App.jsx` to use this URL for API calls

3. Deploy to Vercel normally

## Redeploying

To redeploy:
1. Push changes to GitHub (main branch)
2. Railway automatically rebuilds and deploys
3. Monitor deployment in dashboard

Or manually trigger from Railway dashboard under Deployments.

## Next Steps

1. Test the deployed backend API
2. Monitor logs for any issues
3. Set up custom domain (if desired)
4. Configure production database (if needed)
5. Set up CI/CD best practices
