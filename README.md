# Ampoulex

## Quick Start Guide

To get started quickly, clone the repository and run the application:

```bash
git clone https://github.com/jjarral/ampoulex.git
cd ampoulex
npm install
npm start
```

## Tech Stack

- **Frontend:** React, Redux
- **Backend:** Node.js, Express
- **Database:** MongoDB
- **Deployment Platforms:** Docker, Cloud Run, Vercel

## Deployment Options

### Docker

To deploy with Docker, follow these steps:

1. Build the Docker image:
   
   ```bash
   docker build -t ampoulex .
   ```

2. Run the Docker container:
   
   ```bash
   docker run -p 3000:3000 ampoulex
   ```

### Cloud Run

To deploy on Google Cloud Run:

1. Ensure you are authenticated:
   
   ```bash
   gcloud auth login
   ```

2. Deploy to Cloud Run:
   
   ```bash
   gcloud run deploy ampoulex --image gcr.io/YOUR_PROJECT_ID/ampoulex
   ```

### Vercel

To deploy on Vercel, simply run:

```bash
vercel
```

## Troubleshooting

- **Issue:** Application crashes on startup.
  - **Solution:** Check the environment variables and ensure all dependencies are installed.
  
- **Issue:** Cannot connect to database.
  - **Solution:** Verify the database URL and connection settings in your environment variables.

## Project Structure

```
ampoulex/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
├── public/
├── package.json
├── Dockerfile
└── README.md
```

## Conclusion

This documentation should give you a comprehensive overview of how to set up and deploy Ampoulex. For further details, please refer to the respective documentation of the tools mentioned.