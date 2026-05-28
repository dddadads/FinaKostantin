import streamlit as st
import re
from datetime import datetime
from logic.database import init_db, register_user, get_last_user_data, add_transaction, get_transactions
from logic.finance_manager import calculate_future_prediction

# Настройка страницы (поддерживает и ПК, и Айфон)
st.set_page_config(page_title="FinaKostantin", page_icon="💎", layout="wide")

# Старт базы данных
init_db()

# --- МЕГА КРАСИВЫЙ НЕОНОВЫЙ ЦИФРОВОЙ ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    /* Глубокий премиальный темный фон */
    .stApp {
        background-color: #0B0F19 !important;
        color: #F1F5F9 !important;
        font-family: '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', sans-serif;
    }
    
    /* Стилизация бокового меню (Sidebar) как на ПК */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1E293B;
    }
    
    /* Основной неоновый виджет баланса */
    .balance-box {
        background: linear-gradient(135deg, #1E1B4B 0%, #111827 100%);
        padding: 30px;
        border-radius: 24px;
        border: 1px solid #4F46E5;
        text-align: center;
        box-shadow: 0 0 25px rgba(79, 70, 229, 0.25);
        margin-bottom: 30px;
    }
    .balance-title {
        color: #A5B4FC;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .balance-amount {
        color: #10B981;
        font-size: 42px;
        font-weight: 800;
        margin-top: 10px;
        text-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
    }
    
    /* Закругленные вкладки управления */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #111827;
        padding: 8px;
        border-radius: 16px;
        border: 1px solid #1E293B;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border-radius: 12px;
        color: #94A3B8 !important;
        font-weight: 600;
        font-size: 15px;
        border: none;
        padding: 0px 24px;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5 !important;
        color: #FFF !important;
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.4);
    }
    
    /* Премиальные карточки истории из оригинального PyQt6 */
    .tx-card {
        background-color: #111827;
        padding: 20px 24px;
        border-radius: 18px;
        margin-bottom: 12px;
        border: 1px solid #1E293B;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .tx-card:hover {
        transform: translateY(-2px);
        border-color: #312E81;
    }
    .tx-title {
        color: #E2E8F0;
        font-size: 16px;
        font-weight: 600;
    }
    .tx-info {
        color: #64748B;
        font-size: 14px;
        font-weight: 400;
    }
    .tx-date {
        color: #475569;
        font-size: 12px;
        margin-top: 6px;
    }
    .tx-money {
        font-size: 20px;
        font-weight: 700;
    }

    /* Футуристичные поля ввода */
    input, select, textarea {
        background-color: #111827 !important;
        border: 2px solid #1E293B !important;
        border-radius: 14px !important;
        color: #FFF !important;
        padding: 14px !important;
        font-size: 15px !important;
    }
    input:focus {
        border-color: #4F46E5 !important;
    }
    
    /* Фирменная фиолетовая кнопка ПЛЮС */
    .stButton>button {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        height: 52px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
    }
    
    /* Блок Умного Прогноза */
    .prediction-box {
        color: #E2E8F0;
        font-size: 16px;
        line-height: 1.8;
        padding: 26px;
        background-color: #111827;
        border-radius: 20px;
        border: 1px solid #1E293B;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- БОКОВАЯ ПАНЕЛЬ ДЛЯ ПК (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #FFF; font-size: 22px; font-weight: 800; margin-bottom: 25px;'>💎 FinaKostantin</h2>", unsafe_allow_html=True)
    
    user_data = get_last_user_data()
    if user_data:
        username, balance, user_id = user_data
        txs = get_transactions(user_id)
        current_balance = balance + sum(tx[0] for tx in txs)
        
        st.markdown(f"""
            <div style='text-align: center; padding: 15px; background-color: #1E293B; border-radius: 14px; border: 1px solid #334155;'>
                <span style='color: #94A3B8; font-size: 12px;'>АКТИВНЫЙ ПРОФИЛЬ</span><br>
                <strong style='color: #FFF; font-size: 18px;'>👤 {username}</strong>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Профиль не создан")

# --- ОСНОВНОЙ ЭКРАН (ПК И АЙФОН) ---
if not user_data:
    st.markdown("<h3 style='color: #FFF;'>👋 Добро пожаловать! Давайте создадим профиль сестры</h3>", unsafe_allow_html=True)
    username = st.text_input("Имя пользователя", "Константин")
    init_balance = st.number_input("Стартовый баланс (денег)", min_value=0.0, value=1000.0)
    if st.button("Создать аккаунт", type="primary"):
        user_id = register_user(username, "1234", init_balance)
        if user_id:
            st.rerun()
else:
    # Отрендерить красивый неоновый виджет баланса
    st.markdown(f"""
        <div class="balance-box">
            <div class="balance-title">Текущее состояние счета</div>
            <div class="balance-amount">{current_balance:,.2f} денег</div>
        </div>
    """, unsafe_allow_html=True)

    # Вкладки управления
    tab1, tab2, tab3 = st.tabs(["📊 Финансы и Долги", "🤖 Робот-Автоимпорт", "🔮 Прогноз Будущего"])

    with tab1:
        st.markdown("<h4 style='color: #A5B4FC; margin-bottom: 15px;'>Внести операцию вручную</h4>", unsafe_allow_html=True)
        
        # На ПК выстроится в ряд, на Айфоне — в столбик (идеальный адаптив!)
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Сумма (Расход пиши с минусом)", value=0.0, step=100.0)
            tag = st.selectbox("Категория операции (Тег)", ["Обычный", "Купила", "Долг", "Работа"])
        with col2:
            extra = st.text_input("Дополнительная инфо", placeholder="Что купила / Когда вернуть")

        if st.button("➕ Записать транзакцию", type="primary"):
            if amount != 0:
                add_transaction(user_id, amount, tag, extra)
                st.rerun()

        st.markdown("<br><h4 style='color: #A5B4FC; margin-bottom: 15px;'>📋 История операций</h4>", unsafe_allow_html=True)
        history_filter = st.radio("Фильтр списка:", ["Все операции", "Только Долги"], horizontal=True)
        
        if txs:
            for amt, t, ext, dt in reversed(txs):
                if history_filter == "Только Долги" and t != "Долг":
                    continue
                
                color = "#10B981" if amt > 0 else "#F43F5E"
                sign = "+" if amt > 0 else ""
                info_text = f" — <span class='tx-info'>{ext}</span>" if ext else ""
                
                try:
                    time_formatted = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                except:
                    time_formatted = dt

                # Отрисовка элитной карточки транзакции
                st.markdown(f"""
                    <div class="tx-card">
                        <div>
                            <span class="tx-title">{username}: {t}</span>{info_text}<br>
                            <div class="tx-date">🕒 {time_formatted}</div>
                        </div>
                        <div class="tx-money" style="color: {color};">{sign}{amt:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("История операций пока пуста.")

    with tab2:
        st.markdown("<h4 style='color: #A5B4FC; margin-bottom: 15px;'>🤖 Умный робот-автоимпорт</h4>", unsafe_allow_html=True)
        st.write("Скопируй пуш или СМС от банка на Айфоне/Макбуке и вставь текст ниже:")
        
        clipboard_text = st.text_area("Текст уведомления от банка:", height=130, placeholder="Перевод 500р от Иван И. / Покупка в супермаркете 1200р...")
        
        if st.button("🤖 Распознать и занести в систему"):
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
                    st.success("Робот успешно расшифровал и добавил запись!")
                    st.rerun()
                else:
                    st.error("Ошибка: Робот не смог найти сумму денег в тексте.")

    with tab3:
        st.markdown("<h4 style='color: #A5B4FC; margin-bottom: 15px;'>🔮 Математический прогноз доходов</h4>", unsafe_allow_html=True)
        prediction_text = calculate_future_prediction(txs)
        
        st.markdown(f"""
            <div class="prediction-box">
                {prediction_text.replace('\n', '<br>')}
            </div>
        """, unsafe_allow_html=True)
