# JobSweep - Job Listings Aggregator

A robust Python-based web application that aggregates job listings from multiple platforms including LinkedIn, Indeed, Jobstreet, and Kalibrr. The system uses both API integration (BrightData) and direct web scraping (Selenium) to collect comprehensive job listing data.

## 🚀 Features

- Multi-platform job listing aggregation
- Real-time data streaming with Server-Sent Events (SSE)
- JWT-based authentication
- CORS support
- Flexible storage handling
- Configurable logging system
- Support for both development and production environments

## 🛠️ Technology Stack

- **Backend Framework**: Flask
- **Authentication**: JWT (JSON Web Tokens)
- **Web Scraping**: 
  - Selenium WebDriver
  - BrightData API Integration
- **Data Processing**: BeautifulSoup4
- **State Management**: Python Transitions
- **Development Tools**: 
  - WebDriver Manager
  - Python Dotenv

## 📋 Prerequisites

- Python 3.8+
- Chrome Browser (for Selenium scraping)
- BrightData API credentials
- Valid environment variables configuration

## ⚙️ Installation

1. Clone the repository:
2. Create and activate a virtual environment
3. Install dependencies
4. Set up environment variables (.env)

## 🚀 Running the Application

gunicorn "app:app" --bind 0.0.0.0:5000 --workers 4

## 🔒 API Authentication

The API uses JWT for authentication. To access protected endpoints:

## 📡 API Endpoints

- `POST /login` - Authentication endpoint
- `GET /health` - Health check endpoint
- `GET /ping` - Simple ping endpoint
- `GET /fetch-listings` - Retrieve job listings (Protected)
- `POST /listings` - Initiate new job listings scrape (Protected)
- `GET /jobsweep-sse` - Server-Sent Events endpoint (Protected)


## 👥 Authors

- Made with lots of 💖 by jagger85

## 🙏 Acknowledgments

- BrightData API
- Selenium WebDriver
- Flask Framework