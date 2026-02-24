from pyngrok import ngrok
import time

def start_tunnel():
    try:
        # Connect to localhost:8501
        public_url = ngrok.connect(8501).public_url
        print("\n" + "="*50)
        print(f"LINK TRUY CẬP CÔNG KHAI CỦA BẠN:")
        print(f"{public_url}")
        print("="*50)
        print("\nHãy gửi link trên cho bạn bè của bạn.")
        print("Lưu ý: Không tắt cửa sổ terminal này khi đang sử dụng.")
        
        # Keep the script running
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    start_tunnel()
