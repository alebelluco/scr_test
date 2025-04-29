import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import datetime as dt
from datetime import timedelta
import numpy as np
from utils import persistence_ab as pe 
import plotly_express as px
import plotly.graph_objects as go

st.set_page_config(layout='wide')

head_sx, head_dx = st.columns([4,1])
with head_sx:
    st.title('Produttività reparti')
with head_dx:
    st.image('logo.png')

# CREDENZIALI ====================


token = st.secrets['token']
psw = st.secrets['password']
username = st.secrets['username']
repository_name = st.secrets['repository_name']
file_path = st.secrets['file_path']

db_path_stampa = 'db_stampa'
db_path_fustella = 'db_fustella'
db_path_incolla = 'db_inco'

# INFO STATICHE============================================================================

orari_turni = {
    't1':{'inizio':dt.time(5,30), 'fine':dt.time(13,30)},
    't2':{'inizio':dt.time(13,30), 'fine':dt.time(21,30)},
    't3':{'inizio':dt.time(21,30), 'fine':dt.time(5,30)}
    }

reparti = {
    'STM':'STAM',
    'FST':'FUST',
    'INC':'INCO',
}


if not st.toggle('Nessun nuovo dato, visualizza storico'):
    # CARICAMENTO FILE =========================================================================
    
    input_sx, input_dx = st.columns([1,1])
    with input_sx:
        path_pdf = st.sidebar.file_uploader('Caricare il PDF ore Zucchetti')
        if not path_pdf:
            st.warning('PDF ore non caricato')
            st.stop()
    
    
    with input_dx:
        path = st.sidebar.file_uploader('Caricare il file excel Copia di SQL ...')
        if not path:
            st.warning('Excel ore non caricato')
            st.stop()
            pass
    
    db_fogli = pd.read_excel(path, sheet_name='Base_Dati')
    
    # db_mansioni è salvato su github criptato
    try:
        db_mansioni = pe.retrieve_file_decrypt(username, token, repository_name, file_path,psw)
        st.sidebar.success('Mansioni caricate correttamente')
        st.sidebar.write(db_mansioni)
        
    except:
        st.error('Problema nel caricamento delle mansioni')
        '''
        
        path_mansioni = st.file_uploader('caricare file mansioni')
        if not path_mansioni:
            st.stop()
        mansioni = pd.read_excel(path_mansioni)
        db_mansioni = mansioni[mansioni.columns[:3]]
        db_mansioni
        '''
        st.stop()
    # LETTURA PDF =========================================================================
    
    reader = PdfReader(path_pdf)
    pages = reader.pages
    #st.write(pages[1])
    
    text = pages[1].extract_text()
    words = list(text.split())
    #words
    #st.stop()
    
    db_presenze = pd.DataFrame(columns=['Tipo','Matricola','Cognome','Nome','Data','Orario'])
    for page in pages:
        text = page.extract_text()
        words = list(text.split())
        for i in range(len(words)):
            if (words[i] == 'E') or (words[i] == 'U') :
                tipo = words[i]
    
                if words[i-6]=='000009':
                    matricola = words[i-5]
                    cognome = words[i-4]
                    nome = words[i-3] +' '+ words[i-2]
                elif words[i-7]=='000009':
                    matricola = words[i-6]
                    cognome = words[i-5]
                    nome = words[i-4] +' '+ words[i-3]+' '+words[i-2]
                else:
                    matricola = words[i-4]
                    cognome = words[i-3]
                    nome = words[i-2]
                orario = words[i-1]
                if len(orario) > 5:
                    orario = orario[-5:]
                    nome = nome + orario[:-5]
    
                data = words[i+3]
    
                db_presenze.loc[len(db_presenze)]=[None,None,None,None,None,None]
                db_presenze.Tipo.iloc[-1]=tipo
                db_presenze.Matricola.iloc[-1]=matricola
                db_presenze.Cognome.iloc[-1]=cognome
                db_presenze.Nome.iloc[-1]=nome
                db_presenze.Data.iloc[-1]=data
                db_presenze.Orario.iloc[-1]=orario            
    
    # ELABORAZIONE DATI DI INPUT ========================================================================
    # correzione DB presenze togliendo primo record = uscita , ultimo record = entrata per ogni matricola
    
    db_presenze['data_']=[dt.datetime.strptime(data_str,'%d-%m-%Y').date() for data_str in db_presenze.Data.astype(str)]
    db_presenze['ora_']=[dt.datetime.strptime(data_str,'%H.%M').time() for data_str in db_presenze.Orario.astype(str)]
    db_presenze['data_ora'] = [dt.datetime.combine(db_presenze.data_.iloc[i],db_presenze.ora_.iloc[i]) for i in range(len(db_presenze))]
    #db_presenze=db_presenze[db_presenze.Cognome == 'GIORGIONI']
    
    corretti=[]
    
    
    for matricola in db_presenze.Matricola.unique():
        db_work = db_presenze[db_presenze.Matricola == matricola]
        if (len(db_work) > 1): #and (len(db_work)%2 == 0): # caso 1: righe pari, verifico se la prima e l'ultima sono corrette
        # se il primo record è una U e rappresenta una vera uscita (il delta con il record dopo è > 20h)
            if (db_work.Tipo.iloc[0]=='U') and (((db_work.data_ora.iloc[1]-db_work.data_ora.iloc[0]).seconds)/3600 > 10):
                    inizio = 1
            else:
                inizio = 0
            if (db_work.Tipo.iloc[-1]=='E') and (((db_work.data_ora.iloc[-1]-db_work.data_ora.iloc[-2]).seconds)/3600 > 10) :
                fine = -1
            else:
                fine = len(db_work)
    
            # qui metto la verifica del pari o dispari
            db_work = db_work[inizio:fine]
            if (len(db_work)%2 == 0):
                corretti.append(db_work)
            else:
                if len(db_work) != 1:
                    st.warning(f"Verificare l'orario della matricola {matricola}, registrazione mancante o <10h da uscita a entrata")
                else:
                    st.warning(f"Rimossa matricola {matricola}, un solo evento registrato")
    
                continue
    
    
    
    db_presenze_ok = pd.concat(corretti)
    db_presenze_ok = db_presenze_ok.sort_values(by=['Matricola','data_ora'])
    
    # correzione del file: eliminando le prime righe = uscita e le ultime = entrata il file deve iniziare con un E e alternare E-U
    # le righe sotto correggono entrate timbrate come uscita e viceversa
    
    db_presenze_ok.reset_index(drop=True, inplace=True)
    
    st.subheader('Riepilogo timbrature corrette', divider='grey')
    db_presenze_ok
    
    if db_presenze_ok.Tipo.iloc[0]!='E':
        st.warning("Attenzione, il file inizia con un'uscita")
        st.write('Corretta la prima riga con E')
    
    with st.expander('Registro correzioni file orari'):
        for i in range(1,len(db_presenze_ok)):
            if ((db_presenze_ok.Tipo.iloc[i-1] == 'E') and (db_presenze_ok.Tipo.iloc[i] != 'U')):
                st.write(f"Corretto il file alla riga {i} | Data {db_presenze_ok.Data.iloc[i]} | Operatore {db_presenze_ok.Cognome.iloc[i]} {db_presenze_ok.Nome.iloc[i]} modificato da E a U")
                db_presenze_ok.Tipo.iloc[i] = 'U'
            elif ((db_presenze_ok.Tipo.iloc[i-1] == 'U') and (db_presenze_ok.Tipo.iloc[i] != 'E')):
                st.write(f"Corretto il file alla riga {i} | Data {db_presenze_ok.Data.iloc[i]} | Operatore {db_presenze_ok.Cognome.iloc[i]} {db_presenze_ok.Nome.iloc[i]} modificato da U a E")
                db_presenze_ok.Tipo.iloc[i] = 'E'
            else:
                pass
    
    entrate = db_presenze_ok[db_presenze_ok.Tipo == 'E']
    uscite = db_presenze_ok[db_presenze_ok.Tipo == 'U']
    
    entrate['uscita']=list(uscite.data_ora)
    db_ore = entrate[['data_','Matricola','Cognome','Nome','data_ora','uscita']].rename(columns={'data_ora':'ingresso', 'data_':'Data'})
    
    
    delta = 120
    db_ore['Turno']=None
    db_ore['ingresso_adj']=None
    for i in range(len(db_ore)):
        lim_inf_t1 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t1']['inizio']) - dt.timedelta(minutes=delta)
        lim_sup_t1 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t1']['inizio']) + dt.timedelta(minutes=delta)
        lim_inf_t2 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t2']['inizio']) - dt.timedelta(minutes=delta)
        lim_sup_t2 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t2']['inizio']) + dt.timedelta(minutes=delta)
        lim_inf_t3 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t3']['inizio']) - dt.timedelta(minutes=delta)
        lim_sup_t3 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t3']['inizio']) + dt.timedelta(minutes=delta)
    
        check = db_ore.ingresso.iloc[i]
    
        if check > lim_inf_t1 and check < lim_sup_t1:
            db_ore['Turno'].iloc[i]='t1'
            db_ore['ingresso_adj'].iloc[i]=dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t1']['inizio'])
        elif check > lim_inf_t2 and check < lim_sup_t2:
            db_ore['Turno'].iloc[i]='t2'
            db_ore['ingresso_adj'].iloc[i]=dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t2']['inizio'])
        else:
            db_ore['Turno'].iloc[i]='t3'
            db_ore['ingresso_adj'].iloc[i]=dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t3']['inizio'])
    
    
    db_ore['Presenza_act']=[np.round(((db_ore.uscita.iloc[i] - db_ore.ingresso.iloc[i]).seconds)/3600, 1) for i in range(len(db_ore))]
    db_ore['Presenza_adj']=[np.round(((db_ore.uscita.iloc[i] - db_ore.ingresso_adj.iloc[i]).seconds)/3600, 1) for i in range(len(db_ore))]
    
    db_ore['cognome_nome']=[db_ore.Cognome.iloc[i]+' '+db_ore.Nome.iloc[i] for i in range(len(db_ore))]
    db_ore = db_ore.merge(db_mansioni[['cognome_nome','Mansione','classificazione','turnazione']], how='left', left_on='cognome_nome', right_on='cognome_nome')
    db_ore['turnazione'] = db_ore['turnazione'].fillna('turnista')
    db_ore['classificazione'] = db_ore['classificazione'].fillna('diretto')
    
    
    # aggiustamento ore
    db_ore['Presenza']=None
    for i in range(len(db_ore)):
        turnazione = db_ore.turnazione.iloc[i]
        if turnazione == 'turnista':
            if db_ore.Presenza_adj.iloc[i] > 8:
                if  (db_ore.Presenza_act.iloc[i] < 7 ):
                    db_ore.Presenza.iloc[i] = db_ore.Presenza_act.iloc[i] # intercetto uno straordinario oppure un turno parziale
                elif (db_ore.Presenza_act.iloc[i] > 8.5 ):
                    db_ore.Presenza.iloc[i] = db_ore.Presenza_adj.iloc[i]
                else:
                    db_ore.Presenza.iloc[i] = 8
            
            else:
                db_ore.Presenza.iloc[i] = db_ore.Presenza_adj.iloc[i]
        else:
            db_ore.Presenza.iloc[i] = db_ore.Presenza_act.iloc[i]
    
    db_ore = db_ore[db_ore.classificazione == 'diretto']
    db_ore['reparto'] = [mans[:3] for mans in db_ore.Mansione.astype(str)]
    ore_group = db_ore[['Data','reparto','Turno','Presenza']].groupby(by=['Data','reparto','Turno'], as_index=False).sum()
    #tengo solo la prima data delle due (il minimo), perchè è quella completa (l'ultimo turno della seconda è parziale)
    data_prima = ore_group.Data.min()
    ore_group = ore_group[ore_group.Data == data_prima]
    
    
    
    # con l'ingresso effettivo identifico il turno
    # in base al turno assegno l'ingresso adj
    # con uscita reale - ingresso adj calcolo le ore di presenza
    # se sotto le 8 ore, reale, sopra le 8 per meno di 1h: taglio a 8, se sopra le 8 di + di 1 h lo tengo come straordinario
    # caricamento fogli
    #db_fogli.columns = db_fogli.iloc[0]
    #db_fogli = db_fogli[1:]
    
    db_fogli['Data'] = [data.date() for data in db_fogli.DATA_ATTIVITA]
    db_fogli['orario'] = [data[-5:] for data in db_fogli.DATA_ORA.astype(str)]
    db_fogli['ora_']=[dt.datetime.strptime(data_str,'%H.%M').time() for data_str in db_fogli.orario.astype(str)]
    db_fogli['DATA_ATTIVITA'] = [dt.datetime.combine(db_fogli.Data.iloc[i],db_fogli.ora_.iloc[i]) for i in range(len(db_fogli))]
    
    db_fogli['turno']=None
    
    for i in range(len(db_fogli)):
        turni = orari_turni
        start = db_fogli['DATA_ATTIVITA'].iloc[i]
        
        if (start >= dt.datetime.combine(start.date(), turni['t1']['inizio'])) & (start < dt.datetime.combine(start.date(), turni['t1']['fine'])):
            turno = 't1'
        elif (start >= dt.datetime.combine(start.date(), turni['t2']['inizio'])) & (start < dt.datetime.combine(start.date(), turni['t2']['fine'])):
            turno = 't2'
        else:
            turno = 't3'
            if (start.time() >= dt.time(0,0)) & (start.time() < dt.time(21,0,0)):
                db_fogli['Data'].iloc[i] = db_fogli['Data'].iloc[i] - dt.timedelta(days=1)
    
        db_fogli['turno'].iloc[i] = turno
    
    db_fogli = db_fogli[db_fogli.Data == data_prima]
    
    #ore_group
    
    
    #STAMPA
    
    db_fogli_stam = db_fogli[db_fogli.DES_REPARTO == 'STAM'][['turno','QTA_PRODOTTA']].groupby(by='turno', as_index=False).sum()
    db_ore_stam = ore_group[ore_group.reparto == 'STM'].merge(db_fogli_stam, how='left',left_on='Turno',right_on='turno').drop(columns='turno')
    db_ore_stam['F/mh'] = np.round(db_ore_stam.QTA_PRODOTTA.astype(float) / db_ore_stam.Presenza.astype(float),0)
    
    # FUSTELLA
    
    db_fogli_fus = db_fogli[db_fogli.DES_REPARTO == 'FUST']
    db_fogli_fus = db_fogli[db_fogli.DES_REPARTO == 'FUST'][['turno','QTA_PRODOTTA']].groupby(by='turno', as_index=False).sum()
    db_ore_fus = ore_group[ore_group.reparto == 'FST'].merge(db_fogli_fus, how='left',left_on='Turno',right_on='turno').drop(columns='turno')
    db_ore_fus['F/mh'] = np.round(db_ore_fus.QTA_PRODOTTA.astype(float) / db_ore_fus.Presenza.astype(float),0)
    
    # PIEGA INCOLLA
    
    db_fogli_inco = db_fogli[db_fogli.DES_REPARTO == 'INCO'][['turno','QTA_PRODOTTA']].groupby(by='turno', as_index=False).sum()
    db_ore_inco = ore_group[ore_group.reparto == 'INC'].merge(db_fogli_inco, how='left',left_on='Turno',right_on='turno').drop(columns='turno')
    db_ore_inco = db_ore_inco[:2]
    db_ore_inco['F/mh'] = np.round(db_ore_inco.QTA_PRODOTTA.astype(float) / db_ore_inco.Presenza.astype(float),0)
    
    
    
    tab1, tab2 = st.tabs(['Ultima giornata caricata', 'Andamento'])
    
    with tab1:
        st.subheader(f'Produttività {data_prima}', divider='grey')
    
        st.subheader('Stampa', divider='grey')
        c1_st, c2_st, c3_st, c4_st = st.columns([2,1,1,1])
        with c1_st:
            db_ore_stam
        with c2_st:
            st.metric('FOGLI ORA UOMO T1', value=db_ore_stam['F/mh'].iloc[0], border=True)
        with c3_st:
            st.metric('FOGLI ORA UOMO T2', value=db_ore_stam['F/mh'].iloc[1], border=True)
        with c4_st:
            st.metric('FOGLI ORA UOMO T3', value=db_ore_stam['F/mh'].iloc[2], border=True)
    
        st.subheader('Fustella', divider='grey')
        c1_fs, c2_fs, c3_fs, c4_fs = st.columns([2,1,1,1])
        with c1_fs:
            db_ore_fus
        with c2_fs:
            st.metric('FOGLI ORA UOMO T1', value=db_ore_fus['F/mh'].iloc[0], border=True)
        with c3_fs:
            st.metric('FOGLI ORA UOMO T2', value=db_ore_fus['F/mh'].iloc[1], border=True)
        with c4_fs:
            st.metric('FOGLI ORA UOMO T3', value=db_ore_fus['F/mh'].iloc[2], border=True)
    
        st.subheader('Piega incolla', divider='grey')
        c1_in, c2_in, c3_in, c4_in = st.columns([2,1,1,1])
        with c1_in:
            
            db_ore_inco
        with c2_in:
            st.metric('FOGLI ORA UOMO T1', value=db_ore_inco['F/mh'].iloc[0], border=True)
        with c3_in:
            st.metric('FOGLI ORA UOMO T2', value=db_ore_inco['F/mh'].iloc[1], border=True)
    
    
        # PRIMO CARICAMENTO SU GITHUB =====================================================
        #pe.upload_file(username, token, db_ore_stam, repository_name, db_path_fustella)
        #pe.upload_file(username, token, db_ore_fus, repository_name, db_path_fustella)
        #pe.upload_file(username, token, db_ore_inco, repository_name, db_path_incolla)
    
        updated_stam = pe.retrieve_file(username, token, repository_name, db_path_stampa)
        updated_fust = pe.retrieve_file(username, token, repository_name, db_path_fustella)
        updated_inco = pe.retrieve_file(username, token, repository_name, db_path_incolla)
    
    
        if st.button('Aggiorna database'):
    
            try:
    
                updated_stam = pd.concat([updated_stam, db_ore_stam]).drop_duplicates().sort_values(by=['Data','Turno'])
                pe.upload_file(username, token, updated_stam, repository_name, db_path_stampa)
    
                updated_fust = pd.concat([updated_fust, db_ore_fus]).drop_duplicates().sort_values(by=['Data','Turno'])
                pe.upload_file(username, token, updated_fust, repository_name, db_path_fustella)
    
                updated_inco = pd.concat([updated_inco, db_ore_inco]).drop_duplicates().sort_values(by=['Data','Turno'])
                pe.upload_file(username, token, updated_inco, repository_name, db_path_incolla)
    
                st.success('Database aggiornato correttamente')
            
            except:
    
                st.error("Problema nell'aggiornamento del database ")
    
    
    
            #updated_stam
    
    
    with tab2:
    
        # test con stampa
        #graph_st = px.scatter(updated_stam, x='Data','Turno', y='F/mh')
        graph_st = go.Figure()
        graph_st.add_trace(go.Scatter(
            x=[updated_stam.Data,updated_stam.Turno],
            y=updated_stam['F/mh']
        ))
    
        graph_fu = go.Figure()
        graph_fu.add_trace(go.Scatter(
            x=[updated_fust.Data,updated_fust.Turno],
            y=updated_fust['F/mh']
        ))
    
        graph_in = go.Figure()
        graph_in.add_trace(go.Scatter(
            x=[updated_inco.Data,updated_inco.Turno],
            y=updated_inco['F/mh']
        ))
    
        st.subheader('Stampa')
        st.plotly_chart(graph_st, key='stampa')
        st.divider()
        st.subheader('Fustella')
        st.plotly_chart(graph_fu, key='fustella')
        st.divider()
        st.subheader('Piega incolla')
        st.plotly_chart(graph_in, key='incolla')
    
else:

    updated_stam = pe.retrieve_file(username, token, repository_name, db_path_stampa)
    updated_fust = pe.retrieve_file(username, token, repository_name, db_path_fustella)
    updated_inco = pe.retrieve_file(username, token, repository_name, db_path_incolla)

    graph_st = go.Figure()
    graph_st.add_trace(go.Scatter(
        x=[updated_stam.Data,updated_stam.Turno],
        y=updated_stam['F/mh']
    ))

    graph_fu = go.Figure()
    graph_fu.add_trace(go.Scatter(
        x=[updated_fust.Data,updated_fust.Turno],
        y=updated_fust['F/mh']
    ))

    graph_in = go.Figure()
    graph_in.add_trace(go.Scatter(
        x=[updated_inco.Data,updated_inco.Turno],
        y=updated_inco['F/mh']
    ))


    st.subheader('Andamento Stampa')
    st.plotly_chart(graph_st, key='stampa')

    st.subheader('Andamento Fustella')
    st.plotly_chart(graph_fu, key='fustella')

    st.subheader('Andamento Piega-incolla')
    st.plotly_chart(graph_in, key='incolla')
            



# eliminare indiretti nel confronto turni, ma tenerli in un kpi non diviso per turno
        
