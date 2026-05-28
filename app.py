import streamlit as st
import re
from datetime import datetime
from logic.database import init_db, register_user, get_last_user_data, add_transaction, get_transactions
from logic.finance_manager import calculate_future_prediction

# Настройка для Айфона/Айпада
st.set_page_config(page_title="FinaKostantin", page_icon="💰", layout="centered")

# Инициализация базы
init_db()

# --- МАГИЯ ДИЗАЙНА ПРЯМО ИЗ PyQt6 ---
st.markdown("""
    <style>
    /* Главный фон — глубокий тёмно-синий, как в оригинале */
    .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        font-family: '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Переделываем стандартные вкладки Стримлита под неоновый стиль */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111827;
        padding: 6px;
        border-radius: 14px;
        border: 1px solid #1E293B;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre;
        background-color: transparent;
        border-radius: 10px;
        color: #94A3B8 !important;
        font-weight: 600;
        border: none;
        padding: 0px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #FFF !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Красивые карточки транзакций из оригинального ui/dashboard.py */
    .tx-card {
        background-color: #1E293B;
        padding: 18px 24px;
        border-radius: 16px;
        margin-bottom: 12px;
        border: 1px solid #2D3748;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .tx-left {
        display: flex;
        flex-direction: column;
    }
    .tx-title {
        color: #E2E8F0;
        font-size: 16px;
        font-weight: 500;
    }
    .tx-date {
        color: #64748B;
        font-size: 12px;
        margin-top: 4px;
    }
    .tx-money {
        font-size: 18px;
        font-weight: 700;
    }

    /* Мощные круглые поля ввода */
    input, select, textarea {
        background-color: #1E293B !important;
        border: 2px solid #2D3748 !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 12px !important;
    }
    
    /* Фирменная фиолетовая кнопка ПЛЮС */
    .stButton>button {
        background-color: #7C3AED !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        height: 48px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    .stButton>button:active {
        transform: scale(0.98);
        background-color: #6D28D9 !important;
    }
    
    /* Зелёная кнопка Автоимпорта */
    div[data-testid="stForm"] .stButton>button, .auto-btn>div>button {
        background-color: #10B981 !important;
    }
    
    /* Блок Прогноза (Будущее) */
    .prediction-box {
        color: #E2E8F0;
        font-size: 16px;
        line-height: 1.8;
        padding: 24px;
        background-color: #1E293B;
        border-radius: 16px;
        border: 1px solid #2D3748;
    }
    </style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown("<h1 style='text-align: center; font-size: 28px; color: #F8FAFC;'>👑 Личный кабинет FinaKostantin</h1>", unsafe_allow_html=True)
st.write("")

user_data = get_last_user_data()

if not user_data:
    st.subheader("👋 Создайте профиль сестры:")
    username = st.text_input("Имя сестры", "Константин")
    init_balance = st.number_input("Стартовый баланс денег", min_value=0.0, value=1000.0)
    if st.button("Создать профиль", type="primary"):
        user_id = register_user(username, "1234", init_balance)
        if user_id:
            st.rerun()
else:
    username, balance, user_id = user_data
    txs = get_transactions(user_id)
    
    current_balance = balance + sum(tx[0] for tx in txs)
    
    # Виджет баланса
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 24px; border-radius: 20px; border: 1px solid #334155; text-align: center; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); margin-bottom: 25px;'>
            <div style='color: #94A3B8; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Привет, {username}! Твой баланс:</div>
            <div style='color: #10B981; font-size: 36px; font-weight: 800; margin-top: 8px;'>{current_balance:,.2f} денег</div>
        </div>
    """, unsafe_allow_html=True)

    # Вкладки на Айпаде
    tab1, tab2, tab3 = st.tabs(["📊 Финансы и Долги", "🤖 Робот-Автоимпорт", "🔮 Прогноз"])

    with tab1:
        st.markdown("<h3 style='font-size: 18px; color: #94A3B8;'>Добавить операцию руками</h3>", unsafe_allow_html=True)
        amount = st.number_input("Сумма (расход пиши с минусом)", value=0.0, step=50.0)
        tag = st.selectbox("Категория (Тег)", ["Обычный", "Купила", "Долг", "Работа"])
        extra = st.text_input("Инфо (Продукт / Сроки возврата / Цикл работы)")

        if st.button("➕ Добавить операцию", type="primary"):
            if amount != 0:
                add_transaction(user_id, amount, tag, extra)
                st.rerun()

        st.markdown("<br><h3 style='font-size: 18px; color: #94A3B8;'>📋 История операций</h3>", unsafe_allow_html=True)
        history_filter = st.radio("Фильтр списка:", ["Все операции", "Только Долги"], horizontal=True)
        
        if txs:
            for amt, t, ext, dt in reversed(txs):
                if history_filter == "Только Долги" and t != "Долг":
                    continue
                
                color = "#10B981" if amt > 0 else "#F43F5E"
                sign = "+" if amt > 0 else ""
                info = f" [{ext}]" if ext else ""
                
                try:
                    time_formatted = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                except:
                    time_formatted = dt

                # Рендерим точно такую же карточку, как была в PyQt6!
                st.markdown(f"""
                    <div class="tx-card">
                        <div class="tx-left">
                            <span class="tx-title">{username}: {t}{info}</span>
                            <span class="tx-date">🕒 {time_formatted}</span>
                        </div>
                        <div class="tx-money" style="color: {color};">{sign}{amt:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("История операций пуста.")

    with tab2:
        st.markdown("<h3 style='font-size: 18px; color: #94A3B8;'>🤖 Автоимпорт карт и чеков</h3>", unsafe_allow_html=True)
        st.caption("Скопируй СМС или пуш от банка на Айпаде и вставь сюда:")
        clipboard_text = st.text_area("Текст банковского уведомления:", height=120, placeholder="Покупка 450р, Магнит...")
        
        st.markdown("<div class='auto-btn'>", unsafe_allow_html=True)
        if st.button("🤖 Запустить робота-помощника"):
            if clipboard_text:
                numbers = re.findall(r'[-+]?\d*\.\d+|\d+', clipboard_text.replace(",", "."))
                if numbers:
                    detected_amt = float(numbers[0])
                    detected_tag = "Купила"
                    detected_ext = "Автоимпорт"
                    
                    lower_text = clipboard_text.lower()
                    if any(w in lower_text for w in ["зачисление", "зарплата", "перевод", "доход", "+"]):
                        detected_tag = "Работа"
                        detected_ext = "Раз в месяц"
                    else:
                        detected_amt = -abs(detected_amt)
                    
                    add_transaction(user_id, detected_amt, detected_tag, detected_ext)
                    st.success("Робот успешно считал карту!")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<h3 style='font-size: 18px; color: #94A3B8;'>🔮 Анализ и прогноз</h3>", unsafe_allow_html=True)
        prediction_text = calculate_future_prediction(txs)
        
        # Красивый закругленный блок для вывода прогнозов из финансового модуля
        st.markdown(f"""
            <div class="prediction-box">
                {prediction_text.replace('\n', '<br>')}
            </div>
        """, unsafe_allow_html=True)
