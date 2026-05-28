import streamlit as st
import re
from datetime import datetime
from logic.database import init_db, register_user, get_last_user_data, add_transaction, get_transactions
from logic.finance_manager import calculate_future_prediction

# 1. Настройка отображения для мобильных экранов iPhone/iPad
st.set_page_config(page_title="FinaKostantin", page_icon="💰", layout="centered")

# Инициализируем твою базу данных
init_db()

# Стильный тёмный дизайн, адаптированный под сенсорные экраны Apple
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F1F5F9; }
    div[data-testid="stMetricValue"] { color: #10B981; font-size: 28px; font-weight: bold; }
    .transaction-card {
        background-color: #1E293B; padding: 14px; border-radius: 12px;
        margin-bottom: 8px; border: 1px solid #2D3748;
    }
    /* Крупные удобные кнопки для нажатия пальцем */
    .stButton>button {
        width: 100% !important; height: 45px; border-radius: 10px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("👑 FinaKostantin")

# Проверяем, есть ли пользователь в базе
user_data = get_last_user_data()

if not user_data:
    st.subheader("👋 Добро пожаловать!")
    username = st.text_input("Имя пользователя", "Сестра")
    init_balance = st.number_input("Стартовый баланс (денег)", min_value=0.0, value=1000.0)
    if st.button("Создать профиль", type="primary"):
        user_id = register_user(username, "1234", init_balance)
        if user_id:
            st.success("Профиль создан! Обнови страницу.")
            st.rerun()
else:
    username, balance, user_id = user_data
    txs = get_transactions(user_id)
    
    # Считаем текущий баланс
    current_balance = balance + sum(tx[0] for tx in txs)
    
    # Большой красивый баланс на главном экране смартфона
    st.metric(label=f"Привет, {username}! Твой баланс:", value=f"{current_balance:,.2f} денег")

    # Переключатели вкладок, идеально подходящие для пальца
    tab1, tab2, tab3 = st.tabs(["📊 Финансы", "🤖 Автоимпорт", "🔮 Прогноз"])

    with tab1:
        st.subheader("Внести операцию вручную")
        amount = st.number_input("Сумма (расход пиши с минусом)", value=0.0, step=10.0)
        tag = st.selectbox("Категория (Тег)", ["Обычный", "Купила", "Долг", "Работа"])
        extra = st.text_input("Комментарий / Периодичность", placeholder="Например: кофе или раз в неделю")

        if st.button("➕ Добавить операцию", type="primary"):
            if amount != 0:
                add_transaction(user_id, amount, tag, extra)
                st.success("Успешно добавлено!")
                st.rerun()

        st.write("---")
        st.subheader("📋 История")
        history_filter = st.radio("Показывать:", ["Все", "Только Долги"], horizontal=True)
        
        if txs:
            for amt, t, ext, dt in reversed(txs): # Новые операции сверху
                if history_filter == "Только Долги" and t != "Долг":
                    continue
                color = "#10B981" if amt > 0 else "#F43F5E"
                sign = "+" if amt > 0 else ""
                st.markdown(f"""
                    <div class="transaction-card">
                        <span style="color: #94A3B8; font-size: 11px;">🕒 {dt}</span><br>
                        <strong>{t}</strong> <span style="color: #94A3B8; font-size: 13px;">({ext})</span>
                        <span style="float: right; color: {color}; font-weight: bold;">{sign}{amt:,.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Операций пока нет.")

    with tab2:
        st.subheader("🤖 Автоимпорт из буфера")
        st.caption("Скопируй текст пуша или СМС от банка и вставь его ниже:")
        clipboard_text = st.text_area("Текст уведомления:", height=100)
        
        if st.button("🤖 Распознать и записать"):
            if clipboard_text:
                numbers = re.findall(r'[-+]?\d*\.\d+|\d+', clipboard_text.replace(",", "."))
                if numbers:
                    detected_amt = float(numbers[0])
                    detected_tag = "Купила"
                    detected_ext = "Автоимпорт"
                    
                    lower_text = clipboard_text.lower()
                    if any(w in lower_text for w in ["зачисление", "зарплата", "перевод", "+", "доход"]):
                        detected_tag = "Работа"
                        detected_ext = "В месяц"
                    else:
                        detected_amt = -abs(detected_amt)
                    
                    add_transaction(user_id, detected_amt, detected_tag, detected_ext)
                    st.success(f"Робот внёс: {detected_amt:,.2f} денег")
                    st.rerun()
                else:
                    st.error("Не нашёл сумму в тексте.")

    with tab3:
        st.subheader("🔮 Финансовый прогноз")
        # Вызов твоего оригинального финансового модуля вычислений
        prediction_text = calculate_future_prediction(txs)
        st.info(prediction_text)