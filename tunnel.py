from pyngrok import ngrok, conf
import time

# Start ngrok tunnel on port 8501 (where Streamlit is running)
print("Opening ngrok tunnel to http://localhost:8501 ...")

try:
    tunnel = ngrok.connect(8501, "http")
    public_url = tunnel.public_url
    print("\n" + "="*60)
    print("  ✅ YOUR PUBLIC LINK IS READY!")
    print("="*60)
    print(f"\n  👉  {public_url}\n")
    print("  Share this link with anyone — it works globally!")
    print("  (Keep this window open to keep the link alive)")
    print("="*60)
    
    # Keep tunnel alive
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nTunnel closed.")
        ngrok.disconnect(public_url)
        ngrok.kill()

except Exception as e:
    print(f"\n❌ Error creating tunnel: {e}")
    print("\nAlternative: Try visiting http://localhost:8501 directly in your browser.")
