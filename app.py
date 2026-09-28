import streamlit as st
from groq import Groq
import base64
import json

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ROLLYPAY_LINK = st.secrets["ROLLYPAY_LINK"]
SECRET_PRO_CODE = st.secrets["SECRET_PRO_CODE"]
APP_URL = st.secrets.get("APP_URL", "https://твой-домен.streamlit.app")

client = Groq(api_key=GROQ_API_KEY)
st.set_page_config(page_title="AutoBrief", page_icon="📝", layout="centered")

def encode_data(name, project_type):
    data = json.dumps({"name": name, "type": project_type})
    return base64.urlsafe_b64encode(data.encode()).decode()

def decode_data(encoded_str):
    try:
        data = base64.urlsafe_b64decode(encoded_str.encode()).decode()
        return json.loads(data)
    except:
        return None

query_params = st.query_params
shared_data = decode_data(query_params.get("share", ""))

if shared_data:
    st.title(f"📝 Бриф: {shared_data['type']}")
    st.markdown(f"Заполните бриф для **{shared_data['name']}**.")
    client_input = st.text_area("Опишите задачу своими словами:", height=200)
    st.markdown("---")
    user_code = st.text_input("Код доступа", key="pro_code")
    is_pro = (user_code.strip().upper() == SECRET_PRO_CODE)
    
    if st.button("🚀 Сгенерировать ТЗ"):
        if len(client_input) < 10:
            st.warning("Опишите задачу подробнее.")
        else:
            with st.spinner("AI структурирует требования..."):
                prompt = f"Ты — опытный Project Manager. Преврати этот сырой текст в профессиональное ТЗ. Текст: '{client_input}'. Формат: Цель, Требования, Стек, Сроки/бюджет, Уточняющие вопросы. Только Markdown."
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-70b-versatile",
                    temperature=0.2
                )
                tz_text = response.choices[0].message.content
                
                if not is_pro:
                    viral_footer = f"\n\n---\n💡 *Сгенерировано через [AutoBrief AI]({APP_URL}). Создайте свою ссылку бесплатно.*"
                    tz_text += viral_footer
                    st.info("🔥 Хотите убрать водяной знак и добавить свой логотип?")
                    if st.button("💳 Купить Pro-доступ"):
                        st.markdown(f"👉 [Оплатить через RollyPay]({ROLLYPAY_LINK})")
                        st.success("После оплаты вы увидите код. Введите его выше и сгенерируйте ТЗ заново.")
                
                st.markdown(tz_text)
else:
    st.title("⚡ AutoBrief AI")
    st.markdown("Отправьте клиенту умную ссылку для сбора требований.")
    col1, col2 = st.columns(2)
    with col1:
        my_name = st.text_input("Ваше имя или студия", "Студия")
    with col2:
        project_type = st.text_input("Тип проекта", "Разработка сайта")
        
    if st.button("🔗 Сгенерировать ссылку"):
        share_code = encode_data(my_name, project_type)
        share_url = f"{APP_URL}/?share={share_code}"
        st.success("Ссылка готова!")
        st.code(share_url, language="text")