# PIIDM Backend - Production Build

This is a production-ready build of the PIIDM Backend Flask application.

## Installation

### Windows
1. Run `install.bat` to set up the environment and install dependencies
2. Run `start.bat` to start the application in development mode

### Linux/macOS
1. Run `./install.sh` to set up the environment and install dependencies
2. Run `./start.sh` to start the application in development mode
3. Run `./start_production.sh` to start the application in production mode with Gunicorn

## Configuration

- Edit `.env` file to configure production settings
- The application will run on `http://localhost:3002` by default
- Database file: `piidm_online_sqlite.db`

## Directory Structure

- `app.py` - Main Flask application
- `data/` - Uploaded files and assets
- `migrations/` - Database migrations
- `scripts/` - Utility scripts
- `jobs/` - Background job scripts

## API Documentation

The application provides REST APIs for:
- User management
- Lead management
- Student management
- Course management
- Assignment management
- And more...

## Support

For support and documentation, refer to the original project repository.

Build Date: 2025-10-13 17:52:55
