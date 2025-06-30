import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

LOG_FILE = 'logs/memory_stats.jsonl'

def load_stats():
    records = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return pd.DataFrame(records)

st.title("Dashboard Mémoire Nina")

df = load_stats()
if df.empty:
    st.warning("Aucun log de mémoire trouvé. Exécutez quelques interactions pour générer des logs.")
else:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')

    st.subheader("Évolution du nombre de conversations et de mémoires compressées")
    st.line_chart(df[['conversations', 'compressed_memories']])

    st.subheader("Taille du graphe (entités et connexions)")
    st.line_chart(df[['entities_in_graph', 'total_connections']])

    st.subheader("Statistiques détaillées")
    st.dataframe(df) 