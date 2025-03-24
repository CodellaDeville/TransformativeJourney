# Installation Guide: From Crisis to Creating Coaching Application

This guide provides detailed instructions for installing and configuring the "From Crisis to Creating" coaching application on your server.

## Prerequisites

Before installation, ensure your server meets the following requirements:

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows Server
- **Node.js**: Version 14.0.0 or higher
- **MongoDB**: Version 4.4 or higher
- **NPM**: Version 6.0.0 or higher
- **Disk Space**: At least 1GB of free disk space
- **Memory**: Minimum 2GB RAM recommended

## Frontend Installation

### Step 1: Deploy the Static Files

1. Copy the contents of the build directory to your web server's public directory:
   ```
   cp -r /path/to/build/* /var/www/html/
   ```

2. If using Nginx, configure your server block:
   ```
   server {
       listen 80;
       server_name your-domain.com;
       root /var/www/html;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

3. If using Apache, ensure your .htaccess file contains:
   ```
   RewriteEngine On
   RewriteBase /
   RewriteRule ^index\.html$ - [L]
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteCond %{REQUEST_FILENAME} !-d
   RewriteRule . /index.html [L]
   ```

### Step 2: Configure Environment Variables

Create a `.env` file in your frontend directory with the following variables:
```
REACT_APP_API_URL=https://your-domain.com/api
REACT_APP_VERSION=1.0.0
```

## Backend Installation

### Step 1: Set Up MongoDB

1. Install MongoDB if not already installed:
   ```
   sudo apt update
   sudo apt install -y mongodb
   sudo systemctl start mongodb
   sudo systemctl enable mongodb
   ```

2. Create a database for the application:
   ```
   mongo
   > use crisis_to_creating
   > db.createUser({user: "appuser", pwd: "your_secure_password", roles: [{role: "readWrite", db: "crisis_to_creating"}]})
   > exit
   ```

### Step 2: Configure the Backend

1. Navigate to the server directory:
   ```
   cd /path/to/server
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file with the following variables:
   ```
   PORT=5000
   MONGODB_URI=mongodb://appuser:your_secure_password@localhost:27017/crisis_to_creating
   JWT_SECRET=your_jwt_secret_key
   NODE_ENV=production
   ```

### Step 3: Start the Backend Server

1. For development:
   ```
   npm run dev
   ```

2. For production (using PM2):
   ```
   npm install -g pm2
   pm2 start src/server.js --name crisis-to-creating-api
   pm2 save
   pm2 startup
   ```

## SSL Configuration (Recommended)

For production environments, configure SSL:

1. Obtain SSL certificates (Let's Encrypt recommended):
   ```
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. Update your Nginx configuration to use HTTPS.

## Troubleshooting

### Common Issues

1. **MongoDB Connection Errors**:
   - Verify MongoDB is running: `sudo systemctl status mongodb`
   - Check connection string in `.env` file
   - Ensure network allows connections to MongoDB port (27017)

2. **API Connection Issues**:
   - Verify API URL in frontend `.env` file
   - Check server logs: `pm2 logs crisis-to-creating-api`
   - Ensure proxy settings are correct in web server config

3. **PDF Generation Errors**:
   - Ensure PDFKit dependencies are installed
   - Check write permissions for temporary directories

## Backup and Maintenance

### Database Backup

Set up regular MongoDB backups:
```
mongodump --db crisis_to_creating --out /path/to/backup/directory
```

### Application Updates

1. Pull the latest code
2. Build the frontend: `npm run build`
3. Copy new build files to web server
4. Update backend: `cd server && npm install`
5. Restart backend: `pm2 restart crisis-to-creating-api`

## Security Considerations

1. Keep all dependencies updated
2. Use strong passwords for MongoDB
3. Implement rate limiting for API endpoints
4. Configure proper CORS settings
5. Regularly audit user permissions

For additional support, contact the development team at support@crisistocreating.com.
