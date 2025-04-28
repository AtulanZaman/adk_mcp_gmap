# ADK MCP Agent

A streaming chat agent using Google ADK and the Model Context Protocol (MCP) Google Maps toolset.

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Set up `.env` in `app/` with your API keys.

3. Run locally:
   ```
   export SSL_CERT_FILE=$(python -m certifi)
   uvicorn app.main:app --reload
   ```

## Deployment

To test and run the app locally with the UI:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Create a `.env` file inside the `app/` directory with your API keys:
     ```env
     GOOGLE_GENAI_USE_VERTEXAI=FALSE
     GOOGLE_API_KEY=your_genai_api_key
     GOOGLE_MAPS_API_KEY=your_google_maps_api_key
     ```

3. **Run the FastAPI app:**
   ```bash
   export SSL_CERT_FILE=$(python -m certifi)
   uvicorn app.main:app --reload
   ```

4. **Access the UI:**
   - Open your browser and go to [http://localhost:8000](http://localhost:8000)
   - You can now interact with the chat interface and test the agent locally.

## License

MIT