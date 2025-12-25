# Serv00 Monitor

A lightweight Python script that monitors [serv00.com](https://www.serv00.com/) for available registration slots and sends notifications to Discord.

## Features

- **Automated Monitoring**: Uses Playwright to accurately scrape the account counter from the Serv00 homepage.
- **Discord Notifications**: Sends an alert to your Discord channel via Webhook when slots become available.
- **Dual Mode**:
  - **Daemon Mode**: Runs continuously (ideal for Docker or background processes).
  - **One-Shot Mode**: Runs once and exits (ideal for GitHub Actions).
- **Docker Support**: Easy deployment using Docker and Docker Compose.

## Configuration

The script is configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_WEBHOOK` | **Required**. Your Discord Webhook URL. | - |
| `CHECK_INTERVAL` | Interval between checks in seconds (Daemon mode only). | `300` |
| `ONCE_MODE` | Set to `true` for a single check (One-shot mode). | `false` |
| `TZ` | Timezone for log timestamps. | `UTC` |

## Deployment

### Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone git@github.com:wulukewu/serv00-monitor.git
   cd serv00-monitor
   ```

2. Edit `docker-compose.yml` to include your Discord Webhook URL:
   ```yaml
   environment:
     - DISCORD_WEBHOOK=https://discord.com/api/webhooks/your/webhook/here
     - CHECK_INTERVAL=300
   ```

3. Start the container:
   ```bash
   docker-compose up -d
   ```

### Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Run the script:
   ```bash
   export DISCORD_WEBHOOK="your_webhook_url"
   python monitor.py
   ```

### GitHub Actions

You can use the provided workflows to run the monitor on a schedule. Make sure to add `DISCORD_WEBHOOK` and `PAT` (if using the registry) to your repository secrets.

## Docker Registry

Images are automatically built and pushed to **GitHub Container Registry (GHCR)**:
- `ghcr.io/wulukewu/serv00-monitor:latest`

## License

Apache License 2.0
