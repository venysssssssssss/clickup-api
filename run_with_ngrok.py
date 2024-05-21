from pyngrok import ngrok
import uvicorn

if __name__ == "__main__":
    # Iniciar um túnel ngrok na porta 8000
    public_url = ngrok.connect(8000)
    print(f"ngrok public URL: {public_url}")

    # Iniciar o servidor FastAPI usando Uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
