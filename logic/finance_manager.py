def calculate_future_prediction(transactions):
    work_tx = [tx for tx in transactions if tx[1] == "Работа"]
    
    if not work_tx:
        return (
            "⚠️ Нет данных о доходах\n\n"
            "Добавьте операции с тегом 'Работа', указав "
            "периодичность (в неделю, месяц или год)."
        )

    total_weekly = 0.0
    total_monthly = 0.0
    total_yearly = 0.0

    for amount, tag, extra, date_str in work_tx:
        if "неделю" in extra.lower():
            total_weekly += amount
            total_monthly += (amount / 7) * 30
            total_yearly += (amount / 7) * 365
        elif "месяц" in extra.lower():
            total_weekly += amount / 4.35
            total_monthly += amount
            total_yearly += amount * 12
        elif "год" in extra.lower():
            total_weekly += amount / 52.14
            total_monthly += amount / 12
            total_yearly += amount

    result = (
        f"📊 Анализ доходов на основе {len(work_tx)} источника(ов):\n"
        f"  • Расчет построен на стабильных циклах выплат.\n\n"
        f"🔮 Математический прогноз заработка:\n"
        f"  📈 В неделю:  +{total_weekly:,.2f} денег\n"
        f"  💰 В месяц:   +{total_monthly:,.2f} денег\n"
        f"  👑 В год:     +{total_yearly:,.2f} денег"
    )
    return result
