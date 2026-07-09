import streamlit as st
from src.data_loader import init_session_state, apply_filters, load_data
from src.analytics import calculate_suspicion_score
from src.ui_components import (
    render_kpi_metrics, 
    render_top_fox, 
    render_analytics_tab, 
    render_ai_worklog
)

# 1. PAGE CONFIG
st.set_page_config(
    page_title = "Fox Dispatcher • Лесной Смотритель", 
    page_icon = "🦊", 
    layout = "wide"
)

def main():
    # 2. APPLICATION BRANDING & STYLES
    st.markdown("""
    <style>
        .main-title { font-size: 38px; font-weight: 800; color: #1e293b; margin-bottom: 5px; }
        .small-text { color: #64748b; font-size: 15px; margin-bottom: 25px; }
        .suspicious { 
            padding: 20px; 
            border-radius: 12px; 
            background-color: #fef08a; 
            border-left: 5px solid #eab308;
        }
    </style>
    """, unsafe_allow_html = True)

    # 3. STATE MANAGEMENT
    init_session_state()
    base_df = st.session_state.fox_data

    # 4. HEADER
    st.markdown('<div class = "main-title">🦊 Fox Dispatcher</div>', unsafe_allow_html = True)
    st.markdown('<div class = "small-text">Интеллектуальная система мониторинга и многофакторного анализа активности лис</div>', unsafe_allow_html = True)

    # 5. SIDEBAR FILTERS CONTROL PANEL
    st.sidebar.header("🔎 Панель Фильтров Наблюдений")

    selected_locations = st.sidebar.multiselect(
        "📍 Локация встречи", 
        base_df["location"].unique(), 
        default = list(base_df["location"].unique())
    )

    selected_colors = st.sidebar.multiselect(
        "🎨 Окрас лисы", 
        base_df["color"].unique(), 
        default = list(base_df["color"].unique())
    )

    selected_ids = st.sidebar.multiselect(
        "🆔 Идентификатор (Fox ID)", 
        base_df["fox_id"].unique(), 
        default = list(base_df["fox_id"].unique())
    )

    prey_status = st.sidebar.selectbox(
        "🍖 Статус добычи", 
        ["All", "Has prey", "No prey"]
    )

    suspicion_range = st.sidebar.slider("⚠️ Уровень подозрительности", 0, 10, (0, 10))

    # Извлечение диапазона времени
    min_time = base_df["time"].min().to_pydatetime()
    max_time = base_df["time"].max().to_pydatetime()

    time_range = st.sidebar.slider(
        "⏰ Время фиксации", 
        min_value = min_time, 
        max_value = max_time, 
        value = (min_time, max_time), 
        format = "HH:mm"
    )

    # 6. DATA FILTERING PIPELINE
    filtered_df = apply_filters(
        base_df, 
        selected_locations, 
        selected_colors, 
        selected_ids, 
        prey_status, 
        suspicion_range, 
        time_range
    )

    # 7. MAIN DASHBOARD UI
    render_kpi_metrics(filtered_df)

    st.divider()

    # Аналитический блок "Самый подозрительный объект"
    st.subheader("🚨 Главный объект оперативного контроля")
    fox_scores = calculate_suspicion_score(filtered_df)

    if fox_scores is not None and not fox_scores.empty:
        render_top_fox(fox_scores.iloc[0])
    else:
        st.info("Нет доступных данных для скоринга на основе выбранных фильтров.")

    st.divider()

    # Вкладки нижнего яруса приложения
    tab_charts, tab_data, tab_log = st.tabs(
        [
            "📊 Аналитические отчеты", 
            "✏️ Оперативное управление данными", 
            "🤖 AI Worklog"
        ]
    )

    with tab_charts:
        render_analytics_tab(filtered_df)

    with tab_data:
        st.header("✏️ Редактор базы наблюдений")
        st.write("Любые изменения в таблице ниже мгновенно пересчитывают аналитические отчеты и скоринг безопасности.")
        
        # Интерактивный UI-редактор пандас-датафрейма
        edited_df = st.data_editor(
            base_df, 
            use_container_width = True, 
            num_rows = "dynamic",
            column_config = {
                "has_prey": st.column_config.CheckboxColumn("Наличие добычи"),
                "suspicion_level": st.column_config.NumberColumn(
                    "Уровень подозрительности", 
                    min_value = 0, 
                    max_value = 10
                )
            }
        )
        
        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("💾 Применуть и сохранить изменения", use_container_width = True):
                st.session_state.fox_data = edited_df
                st.success("База данных успешно обновлена локально!")
                st.rerun()
                
        with col_reset:
            if st.button("🔄 Сбросить к исходному JSON", use_container_width = True):
                st.session_state.fox_data = load_data()
                st.success("Данные восстановлены из первоначального файла.")
                st.rerun()

    with tab_log:
        render_ai_worklog()

if __name__ == "__main__":
    main()