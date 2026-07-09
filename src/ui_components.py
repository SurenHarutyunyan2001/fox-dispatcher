import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def render_kpi_metrics(filtered_df):
    # Отрисовка верхних карточек суммарной статистики леса.
    st.subheader("📌 Forest Overview")
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.metric("Total Observations", len(filtered_df))
    with k2:
        st.metric("Unique Foxes Spotted", filtered_df["fox_id"].nunique() if not filtered_df.empty else 0)
    with k3:
        avg = round(filtered_df["suspicion_level"].mean(), 2) if not filtered_df.empty else 0
        st.metric("Average Suspicion", avg)
    with k4:
        # Проверка на пустые значения локаций перед поиском самой популярной
        if not filtered_df.empty and len(filtered_df["location"].dropna()) > 0:
            location = filtered_df["location"].value_counts().idxmax()
        else:
            location = "-"
        st.metric("Most Active Location", location)

def render_scoring_rationale():
    # Математическое и продуктовое обоснование скоринга угрозы.
    with st.expander("ℹ️ Как рассчитывается рейтинг угрозы? (Продуктовая логика)", expanded = False):
        st.markdown("""
        Для выявления наиболее опасных особей используется алгоритм взвешенного многофакторного анализа. 
        Простая фильтрация по уровню подозрительности неэффективна, так как она упускает системные паттерны поведения.

        $$Score = (\\mu_{suspicion} \\times 10) + (N_{obs} \\times 5) + (S_{prey} \\times 10) + (L_{uniq} \\times 3)$$

        **Обоснование весовых коэффициентов:**
        * **$\\mu_{suspicion} \\times 10$ (Базовый риск):** Средний уровень подозрительности имеет высокий приоритет. Показывает базовую агрессию или странность поведения лисы.
        * **$N_{obs} \\times 5$ (Фактор навязчивости):** Каждое повторное появление лисы увеличивает её оценку угрозы. Системное присутствие в лесу критичнее разового появления.
        * **$S_{prey} \\times 10$ (Активная фаза):** Если лиса успешно охотится, её скрытность и потенциальная опасность для экосистемы возрастают.
        * **$L_{uniq} \\times 3$ (Миграционный штраф):** Перемещение между разными локациями расширяет зону потенциального инцидента.
        """)

def render_top_fox(top_fox):
    """Отрисовка карточки самой подозрительной лисы дня с объяснением причин."""
    render_scoring_rationale()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class = "suspicious">
            <h3 style = 'margin:0;'>🦊 КРИТИЧЕСКИЙ ОБЪЕКТ: {top_fox['fox_id']}</h3>
            <h2 style = 'margin:10px 0 0 0; color: #b7791f;'>Рейтинг угрозы: {round(top_fox['score'], 1)}</h2>
        </div>
        """, unsafe_allow_html = True)
        
    with col2:
        st.write("### 📋 Анализ факторов риска:")
        reasons = []
        if top_fox["avg_suspicion"] >= 7:
            reasons.append(f"Высокий уровень агрессии/подозрительности ({round(top_fox['avg_suspicion'], 1)} из 10)")
        if top_fox["observations"] > 1:
            reasons.append(f"Повышенная частота фиксации в системе ({top_fox['observations']} раз(а))")
        if top_fox["prey_events"] > 0:
            reasons.append(f"Объект замечен с добычей ({top_fox['prey_events']} раз(а)) — активная фаза охоты")
        if top_fox["locations"] > 1:
            reasons.append(f"Высокая мобильность: перемещается между {top_fox['locations']} локациями")
            
        for reason in reasons:
            st.write("⚠️", reason)

def render_analytics_tab(filtered_df):
    """Интерактивные графики временной шкалы и гибкий конструктор."""
    if filtered_df.empty:
        st.info("Нет данных для построения графиков по текущим фильтрам.")
        return

    st.header("📈 Fox Timeline Explorer")
    metrics = st.multiselect(
        "Выберите метрики для отображения на графике:",
        ["Suspicion level", "Observation count", "Unique foxes", "Foxes with prey"],
        default=["Suspicion level"]
    )

    fig = go.Figure()
    df_sorted = filtered_df.sort_values("time")
    # Преобразуем время в строковый формат %H:%M для исправления бага с непрерывной шкалой Plotly
    time_str = df_sorted["time"].dt.strftime("%H:%M")

    if "Suspicion level" in metrics:
        fig.add_trace(
            go.Scatter(
                x = time_str, 
                y = df_sorted["suspicion_level"], 
                mode = "lines+markers", 
                name = "Уровень подозрительности", 
                line = dict(width = 3, color = '#f15a24')
                )
            )
    
    if "Observation count" in metrics:
        temp = df_sorted.groupby(df_sorted["time"].dt.strftime("%H:%M")).size().reset_index(name = "count")
        fig.add_trace(
            go.Bar(
                x = temp["time"], 
                y = temp["count"], 
                name = "Кол-во наблюдений", 
                marker_color = '#29abe2'
            )
        )
        
    if "Unique foxes" in metrics:
        temp = df_sorted.groupby(df_sorted["time"].dt.strftime("%H:%M"))["fox_id"].nunique().reset_index(name = "unique")
        fig.add_trace(
            go.Scatter(
                x = temp["time"], 
                y = temp["unique"], 
                mode = "lines+markers", 
                name = "Уникальные лисы", 
                line = dict(dash = 'dash', color = '#22b14c')
            )
        )
        
    if "Foxes with prey" in metrics:
        temp = df_sorted[df_sorted["has_prey"] == True].groupby(df_sorted["time"].dt.strftime("%H:%M")).size().reset_index(name = "prey")
        fig.add_trace(
            go.Bar(
                x = temp["time"], 
                y = temp["prey"], 
                name = "С добычей", 
                marker_color = '#ffc107'
            )
        )
    
    fig.update_layout(
        height = 400, 
        hovermode = "x unified", 
        xaxis_title = "Время фиксации", 
        yaxis_title = "Значение метрики", 
        margin = dict(l = 20, r = 20, t = 20, b = 20)
        )
    
    st.plotly_chart(fig, use_container_width = True)

    # Universal Graph Builder
    st.divider()
    st.header("🛠 Universal Graph Builder")
    col1, col2, col3 = st.columns(3)
    with col1: x_axis = st.selectbox("Ось X", ["time", "location", "color", "fox_id"])
    with col2: y_axis = st.selectbox("Ось Y", ["suspicion_level", "has_prey"])
    with col3: group = st.selectbox("Группировка по цвету", ["location", "color", "fox_id"])
    
    plot_df = filtered_df.copy()
    plot_df["time"] = plot_df["time"].dt.strftime("%H:%M")
    
    graph = px.scatter(
        plot_df, 
        x = x_axis, 
        y = y_axis, 
        color = group, 
        size = "suspicion_level",
        hover_data = ["fox_id", "location", "color", "has_prey", "time"],
        color_discrete_sequence = px.colors.qualitative.Pastel
    )

    st.plotly_chart(graph, use_container_width = True)

def render_ai_worklog():
    # Живой, развернутый отчет по требованиям AI-first ТЗ.
    st.header("🤖 AI Worklog / Как я работал с AI")
    st.write("Пошаговые ключевые чекпоинты совместной разработки приложения с LLM моделями.")
    
    with st.expander("Открыть лог итераций (Взаимодействие с ИИ)", expanded = True):
        st.markdown("""
        ### 📍 Чекпоинт 1 — Первичный промпт и декомпозиция
        * **Промпт к AI:** *«Привет! Я делаю тестовое приложение для лесного смотрителя. Вот ТЗ и JSON. Какие фичи мы можем добавить, чтобы интерфейс был не просто таблицей, а решал задачу аналитики и поиска аномалий? Предложи концепт на Python.»*
        * **Результат & Решение:** AI предложил сделать упор на выявление «критического объекта» и создать интерактивные таймлайны. Было принято решение отказаться от статических дашбордов в пользу SPA-системы на Streamlit.

        ### 📍 Чекпоинт 2 — Итеративная разработка формулы скоринга
        * **Промпт к AI:** *«Базовый уровень подозрительности из JSON не дает полной картины. Помоги составить комплексную формулу скоринга, которая учтет не просто разовую подозрительность, а частоту появлений лисы, её успешность в охоте и перемещения между локациями. Нам нужны веса.»*
        * **Результат:** AI предложил весовые коэффициенты (x10 за подозрительность, x10 за добычу, x5 за частоту, x3 за уникальные локации). Архитектурно этот алгоритм был сразу вынесен в отдельный изолированный модуль `analytics.py`, чтобы отделить бизнес-логику от UI.

        ### 📍 Чекпоинт 3 — Переход от монолита к модульной архитектуре
        * **Промпт к AI:** *«У меня получился один огромный файл Main.py на 300 строк кода. Код работает, но нарушает паттерны чистого кода. Помоги разбить его на модули так, чтобы Main выполнял только роль оркестратора интерфейса.»*
        * **Моё решение:** На основе предложенной AI структуры я создал пакет `src/` и изолировал загрузку данных, аналитику и UI-компоненты. Это позволило сделать код поддерживаемым и наглядно показало архитектурный подход к разработке.

        ### 📍 Чекпоинт 4 — Проектирование реактивного слоя данных (UX/UI)
        * **Промпт к AI:** *«В ТЗ просят, чтобы пользователь мог менять данные и видеть изменения. Как лучше это заверстать в Streamlit без подключения тяжелых баз данных?»*
        * **Результат:** Интегрирован компонент `st.data_editor` с жесткой валидацией типов (CheckboxColumn, NumberColumn). Изменения пишутся напрямую в `st.session_state`. Я самостоятельно добавил кнопки «Применить изменения» и «Сбросить данные», чтобы предотвратить случайную порчу исходного датасета.

        ### 📍 Чекпоинт 5 — Исправление бага с осями времени Plotly
        * **Промпт к AI:** *«При фильтрации данных Plotly некорректно отрисовывает временную шкалу X, превращая её в непрерывный таймлайн, из-за чего точки склеиваются. Как заставить график воспринимать время в формате %H:%M как дискретные категории?»*
        * **Результат:** Нашли слабое место в обработке типов данных. AI подсказал решение: трансформировать `pd.Timestamp` во временные строки непосредственно перед передачей в trace Plotly (`df.dt.strftime("%H:%M")`). Баг устранен.

        ### 📍 Чекпоинт 6 — Тестирование граничных состояний (Edge Cases)
        * **Моё решение:** При тестировании я заметил, что если выставить фильтры слишком агрессивно, приложение падает с ошибками Pandas из-за пустых выборок (`DataFrame.empty`). Я доработал функции `apply_filters` и `render_analytics_tab`, добавив явные проверки на пустоту (`if filtered_df.empty: return`), гарантируя отказоустойчивость интерфейса.
        """)