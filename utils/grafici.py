import streamlit  as st 
import pandas as pd 
import plotly_express as px
import plotly.graph_objects as go

def pareto(df, label, value ,stile):
    '''
    - La funzione crea l'aggregazione dei valori per categoria, ordina decrescente e calcola la pct cumulativa
    - Fa il grafico
    - Label è la colonna con la categoria da raggruppare
    - Value è il valore, che viene SOMMATO
    
    '''
    df_work = df[[label, value]].groupby(by=label, as_index=False).sum()

    df_work = df_work.sort_values(by=value, ascending=False)
    df_work['pct'] = df_work[value] / df_work[value].sum()
    df_work['pct_cum'] = df_work['pct'].cumsum()
    pareto = go.Figure()

    pareto.add_trace(go.Bar(
        x=df_work[label],
        y=df_work[value],
        name=stile['name_bar'],
        marker_color=stile['colore_barre']
    ))

    pareto.add_trace(go.Scatter(
        x=df_work[label],
        y=df_work['pct_cum'],
        yaxis='y2',
        name=stile['name_cum'],
        marker_color=stile['colore_linea']
        )
    )

    pareto.update_layout(
        showlegend=False,
        yaxis=dict(
            title=dict(text=stile['y_name'], font = dict(size=stile['tick_size'])),
            side="left",
            tickfont=dict(size=stile['tick_size'])
            
        ),
        yaxis2=dict(
            title=dict(text=stile['y2_name'], font = dict(size=stile['tick_size'])),
            side="right",
            range=[0, 1],
            overlaying="y",
            tickmode="sync",
            tickformat=".0%",
            tickfont=dict(size=stile['tick_size'])

        ),
        xaxis=dict(
            tickfont=dict(size=stile['tick_size']),
            tickangle=stile['angle']
        )
    )

    return pareto