# OHS-Sound-and-Lights-Discord-bot

## Running with Docker Compose

You can run the OHS Sound and Lights Discord bot using Docker Compose for easy setup and deployment. This method is recommended if you want to avoid installing dependencies directly on your system.

### 1. Prerequisites

- Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.

### 2. Clone the Repository

```bash
git clone https://github.com/OaktonHSTech/OHS-Sound-and-Lights-Discord-bot.git
cd OHS-Sound-and-Lights-Discord-bot
```

### 3. Create and Edit Environment Variables

Create a `.env` file in the root of the project. This file will contain configuration variables such as your Discord bot token and any other settings the bot requires.

**Example `.env`:**
```
DISCORD_BOT_TOKEN=your-discord-bot-token
COMMAND_PREFIX=!
OTHER_SETTING=value
```
**Note:** Please refer to the source code or documentation for a full list of supported environment variables.

### 4. Create/Edit the `docker-compose.yml` File

If a `docker-compose.yml` file is not provided, create one in the root directory:

```yaml
version: "3"
services:
  bot:
    build: .
    env_file:
      - .env
    restart: unless-stopped
```

Or, if you want to use a pre-built image (replace `<image-name>` with your Docker Hub image if available):
```yaml
version: "3"
services:
  bot:
    image: <image-name>
    env_file:
      - .env
    restart: unless-stopped
```

### 5. Build and Run

```bash
docker-compose up --build -d
```

This will build the Docker image (if needed) and start the bot in detached mode.

### 6. Stopping the Bot

To stop and remove the running containers:
```bash
docker-compose down
```

## Customization Options

You can customize the bot's behavior by setting environment variables in your `.env` file. Common settings include:

- `DISCORD_BOT_TOKEN`: *(Required)* The Discord bot token.
- `COMMAND_PREFIX`: The prefix for bot commands (default might be `!`).
- Other custom environment variables as supported by the bot.

Check the documentation or source code (look for usage of `os.environ.get` or similar) to see what other settings you can adjust.

### Advanced Customization

- **Mounting Volumes:** You can mount volumes to persist data or provide config files.
- **Changing Ports:** If the bot exposes HTTP endpoints or other ports, map them in `docker-compose.yml`.
- **Multiple Services:** You can add other services (e.g., databases) to the `docker-compose.yml` as needed.

---

For more details, refer to Jessie or source code.

## Coding by ChatGPT and a lot of Cursor.
### README by copilot.
####(Jessie also helped.)