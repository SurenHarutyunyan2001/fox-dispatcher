import pandas as pd

def calculate_suspicion_score(data):
    """
    Интеллектуальный скоринг лис на основе комплексных факторов.
    Формула учитывает среднюю подозрительность, частоту появлений, 
    наличие добычи и территориальную активность (уникальные локации).
    """
    if data is None or data.empty:
        return None

    stats = (
        data.groupby("fox_id")
        .agg(
            avg_suspicion = ("suspicion_level", "mean"),
            observations = ("id", "count"),
            prey_events = ("has_prey", "sum"),
            locations = ("location", "nunique")
        )
        .reset_index()
    )

    # Весовые коэффициенты для комплексной оценки угрозы особи
    stats["score"] = (
        stats["avg_suspicion"] * 10         # Базовый уровень подозрительности
        + stats["observations"] * 5         # Частота появления (навязчивость)
        + stats["prey_events"] * 10         # Активная фаза (успешная охота)
        + stats["locations"] * 3            # Миграционная активность по лесу
    )

    return stats.sort_values("score", ascending = False)