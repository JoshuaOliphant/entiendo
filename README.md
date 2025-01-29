# Entiendo - Document Understanding Assistant

Entiendo is an AI-powered web application that helps users understand complex documents by providing plain-language explanations with verifiable citations. It leverages Anthropic's Claude API to ensure explanations are grounded in the source material.

## Features

- Upload and process PDF and text documents
- Get plain language explanations of document segments
- View citations and references to the original text
- Modern, responsive user interface
- Interactive document viewer
- Logging and monitoring with Logfire

## Requirements

- Python 3.12 or higher
- Anthropic API key
- Logfire token (for logging)

## Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd entiendo
```

2. Create a `.env` file in the `src/services` directory:
```bash
ANTHROPIC_API_KEY=your_api_key_here
LOGFIRE_TOKEN=your_logfire_token_here
```

3. Install dependencies using uv:
```bash
uv pip install -r requirements.txt
```

4. Start the development server:
```bash
uvicorn src.main:app --reload --port 8000
```

5. Open your browser and navigate to:
```
http://localhost:8000
```

## Docker Deployment

1. Build and run using Docker:
```bash
# Build the image
docker build -t entiendo .

# Run the container
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_api_key_here \
  -e LOGFIRE_TOKEN=your_logfire_token_here \
  entiendo
```

Alternatively, use the provided script:
```bash
./run-docker.sh
```

1. Deploy:
```bash
fly deploy
```

## API Endpoints

- `GET /`: Main web interface
- `POST /upload`: Upload a document (PDF/TXT)
- `GET /document/{doc_id}`: Retrieve document details
- `POST /analyze`: Analyze document segments

## Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude
- `LOGFIRE_TOKEN`: Your Logfire token for logging and monitoring

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.