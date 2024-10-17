import streamlit as st
import pathlib
from PIL import Image
import google.generativeai as genai

# Định nghĩa ứng dụng WSGI

# Configure the API key directly in the script
API_KEY = 'AIzaSyCR-XxNPJ3BcLkx5GymmZ-a1miuEw1cJI8'
genai.configure(api_key=API_KEY)

# Generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Model name
MODEL_NAME = "gemini-1.5-pro-latest"

# Framework selection (e.g., Tailwind, Bootstrap, etc.)
framework = "Regular CSS use flex grid etc"  # Change this to "Bootstrap" or any other framework as needed

# Create the model
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    safety_settings=safety_settings,
    generation_config=generation_config,
)

# Start a chat session
chat_session = model.start_chat(history=[])

# Function to send a message to the model
def send_message_to_model(message, image_path):
    image_input = {
        'mime_type': 'image/jpeg',
        'data': pathlib.Path(image_path).read_bytes()
    }
    response = chat_session.send_message([message, image_input])
    return response.text

# Streamlit app
def main():
    # st.title("Tự động code giao diện theo hình ảnh 👨‍💻 ")
    st.subheader('Tự động code giao diện theo hình ảnh 👨‍💻')

    uploaded_file = st.file_uploader("Chọn hình ảnh...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            # Load and display the image
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image.', use_column_width=True)

            # Convert image to RGB mode if it has an alpha channel
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            # Save the uploaded image temporarily
            temp_image_path = pathlib.Path("temp_image.jpg")
            image.save(temp_image_path, format="JPEG")

            # Generate UI description
            if st.button("Bắt đầu phần tích & code UI"):
                st.write("🧑‍💻 Đang xem giao diện của bạn...")
                prompt = "Mô tả giao diện người dùng (UI) một cách chính xác. Khi bạn tham chiếu đến một phần tử UI, hãy đặt tên của nó và hộp giới hạn theo định dạng: [tên đối tượng (y_min, x_min, y_max, x_max)]. Cũng hãy mô tả màu sắc của các phần tử."
                description = send_message_to_model(prompt, temp_image_path)
                st.write(description)

                # Refine the description
                st.write("🔍 Làm tinh chỉnh mô tả với so sánh hình ảnh...")
                refine_prompt = f"So sánh các phần tử UI đã mô tả với hình ảnh được cung cấp và xác định bất kỳ phần tử nào bị thiếu hoặc không chính xác. Cũng hãy mô tả màu sắc của các phần tử. Cung cấp một mô tả tinh chỉnh và chính xác về các phần tử UI dựa trên sự so sánh này. Đây là mô tả ban đầu: {description}"
                refined_description = send_message_to_model(refine_prompt, temp_image_path)
                st.write(refined_description)

                # Generate HTML
                st.write("🛠️ Đang tạo website...")
                html_prompt = f"Tạo một tệp HTML dựa trên mô tả UI sau đây, sử dụng các phần tử UI được mô tả trong phản hồi trước. Bao gồm CSS {framework} trong tệp HTML để định dạng các phần tử. Đảm bảo rằng các màu sắc được sử dụng giống như giao diện gốc. Giao diện cần phải đáp ứng và ưu tiên di động, khớp với giao diện gốc một cách gần nhất có thể. Không bao gồm bất kỳ giải thích hoặc bình luận nào. Tránh sử dụng html. và ở cuối. CHỈ trả về mã HTML với CSS nội tuyến. Đây là mô tả tinh chỉnh: {refined_description}"
                initial_html = send_message_to_model(html_prompt, temp_image_path)
                st.code(initial_html, language='html')

                # Refine HTML
                st.write("🔧 Tinh chỉnh website...")
                refine_html_prompt = f"Xác thực mã HTML sau đây dựa trên mô tả UI và hình ảnh và cung cấp một phiên bản tinh chỉnh của mã HTML với CSS {framework} nhằm cải thiện độ chính xác, khả năng đáp ứng và tuân thủ thiết kế gốc. CHỈ trả về mã HTML tinh chỉnh với CSS nội tuyến. Tránh sử dụng html. và ở cuối. Đây là mã HTML ban đầu: {initial_html}"
                refined_html = send_message_to_model(refine_html_prompt, temp_image_path)
                st.code(refined_html, language='html')

                # Save the refined HTML to a file
                with open("index.html", "w", encoding='utf-8') as file:  # Thêm encoding='utf-8'
                    file.write(refined_html)
                st.success("Tệp HTML 'index.html' đã được tạo.")

                # Provide download link for HTML
                st.download_button(label="Tải code giao diện", data=refined_html, file_name="index.html", mime="text/html")
        except Exception as e:
            st.error(f"Đã xảy ra lỗi: {e}")



if __name__ == "__main__":
    main()
