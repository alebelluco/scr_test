# Modifiche introdotte nella versione v1 del 22/05/2025
# Aggiunti number input per correggere le ore tagliate dal tool per problemi di timbratura
# A140 modificato reparto da MVAR a FUST
# A151 modificato reparto da FINE a INCO
# Tagliati a 3 parole max i nomi su mansioni per matcharli con le timbrature (chi aveva + di 3 nomi non veniva correttamente)
# riga 421 QTA prodotta = pezzi adj dopo sdoppiamento (prima calcolava 2 volte le righe sdoppiate a cavallo del turno)
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import datetime as dt
from datetime import timedelta
import numpy as np
from utils import persistence_ab as pe 
from utils import utility as ut
import plotly_express as px
import plotly.graph_objects as go

st.set_page_config(layout='wide')

head_sx, head_dx = st.columns([4,1])
with head_sx:
    st.title('Produttività reparti')
with head_dx:
    st.image('logo.png')

# COMMENTI
# riga 242 vengono filtrate le ore solo dei diretti

# CREDENZIALI ====================


token = st.secrets['token']

token = st.secrets['password']

username = st.secrets['username']

repository_name = st.secrets['repository_name']

file_path = st.secrets['file_path']

db_path_stampa = 'db_stampa'
db_path_fustella = 'db_fustella'
db_path_incolla = 'db_inco'


if not st.toggle('Nessun nuovo dato, visualizza storico'):

    # INFO STATICHE============================================================================

    orari_turni = {
        't1':{'inizio':dt.time(5,30), 'fine':dt.time(13,30)},
        't2':{'inizio':dt.time(13,30), 'fine':dt.time(21,30)},
        't3':{'inizio':dt.time(21,30), 'fine':dt.time(5,30)}
        }


    orari_turni2 = {
    'STAM':{
    't1':{'inizio':dt.time(5,30), 'fine':dt.time(13,30)},
    't2':{'inizio':dt.time(13,30), 'fine':dt.time(21,30)},
    't3':{'inizio':dt.time(21,30), 'fine':dt.time(5,30)}},
    'FUST':{
    't1':{'inizio':dt.time(5,30), 'fine':dt.time(13,30)},
    't2':{'inizio':dt.time(13,30), 'fine':dt.time(21,30)},
    't3':{'inizio':dt.time(21,30), 'fine':dt.time(5,30)}},
    'INCO':{
    't1':{'inizio':dt.time(5,30), 'fine':dt.time(13,30)},
    't2':{'inizio':dt.time(13,30), 'fine':dt.time(21,30)},
    't3':{'inizio':dt.time(21,30), 'fine':dt.time(5,30)}},
    'MVAR':{
    't1':{'inizio':dt.time(5,30), 'fine':dt.time(13,30)},
    't2':{'inizio':dt.time(13,30), 'fine':dt.time(21,30)},
    't3':{'inizio':dt.time(21,30), 'fine':dt.time(5,30)}},
    'CERN':{
    't1':{'inizio':dt.time(5,30), 'fine':dt.time(13,30)},
    't2':{'inizio':dt.time(13,30), 'fine':dt.time(21,30)},
    't3':{'inizio':dt.time(21,30), 'fine':dt.time(5,30)}},
    'ACCO':{
    't1':{'inizio':dt.time(5,30), 'fine':dt.time(13,30)},
    't2':{'inizio':dt.time(13,30), 'fine':dt.time(21,30)},
    't3':{'inizio':dt.time(21,30), 'fine':dt.time(5,30)}},
    'FINE':{
    't1':{'inizio':dt.time(5,30), 'fine':dt.time(13,30)},
    't2':{'inizio':dt.time(13,30), 'fine':dt.time(21,30)},
    't3':{'inizio':dt.time(21,30), 'fine':dt.time(5,30)}},
}


    reparti = {
        'STM':'STAM',
        'FST':'FUST',
        'INC':'INCO',
    }

    # CARICAMENTO FILE =========================================================================

    input_sx, input_dx = st.columns([1,1])
    with input_sx:
        path_pdf = st.sidebar.file_uploader('Caricare il PDF ore Zucchetti')
        if not path_pdf:
            st.sidebar.warning('PDF ore non caricato')
            st.stop()


    with input_dx:
        #path = st.sidebar.file_uploader('Caricare il file excel Copia di SQL ...')
        path = st.sidebar.file_uploader('Caricare il file excel Estrazione ultimi 30gg')
        if not path:
            st.sidebar.warning('Excel ore non caricato')
            st.stop()
            pass

    db_fogli = ut.upload(path, 'Base_Dati')
    #db_fogli = pd.read_excel(path, sheet_name='Base_Dati')
    db_fogli = db_fogli[db_fogli.RAGG_ATTIVITA =='PRODUZIONE']
    db_fogli['DES_REPARTO'] = np.where(db_fogli.COD_MACCHINA == 'A140 ', 'FUST', db_fogli['DES_REPARTO'])
    db_fogli['DES_REPARTO'] = np.where(db_fogli.COD_MACCHINA == 'A151 ', 'INCO', db_fogli['DES_REPARTO'])

    db_fogli = db_fogli[db_fogli.COD_MACCHINA != 'A176 ']
    db_fogli = db_fogli[db_fogli.COD_MACCHINA != 'A177 ']
    # db_mansioni è salvato su github criptato
    try:
        db_mansioni = pe.retrieve_file_decrypt(username, token, repository_name, file_path,psw)
        st.sidebar.success('Mansioni caricate correttamente')
        st.sidebar.write(db_mansioni)
        
    except Exception as e:
        st.error(f'Problema nel caricamento delle mansioni: {e}')
        st.stop()
    

    # correzione nomi + lunghi 3 parole
    for i in range(len(db_mansioni)):
        test = db_mansioni.cognome_nome.iloc[i]
        test_split = str.split(test, sep=' ')
        if len(test_split)>3:
            new_name = test_split[0]+' '+test_split[1]+' '+test_split[2]
            db_mansioni.cognome_nome.iloc[i] = new_name


    path_vel = st.sidebar.file_uploader('Caricare kpi_lean')
    if not path_vel:
        st.stop()
    v_tgt = ut.upload(path_vel, 'VI_LEAN_INDIC_TOT_SAS')
    v_tgt = v_tgt[v_tgt.PROGR_COMMESSA.astype(str)!='nan']

    v_tgt['PROGR_COMMESSA'] = [int(comm) for comm in v_tgt.PROGR_COMMESSA]
    v_tgt['PROGR_COMMESSA'] = [stringa[:4] for stringa in v_tgt['PROGR_COMMESSA'].astype(str)]
    v_tgt['ANNO_COMMESSA'] =  [stringa[:2] for stringa in v_tgt['ANNO_COMMESSA'].astype(str)]

    for i in range(len(v_tgt)):
        comm = v_tgt['PROGR_COMMESSA'].iloc[i]
        if len(comm) == 1:
            v_tgt['PROGR_COMMESSA'].iloc[i] = '000'+v_tgt['PROGR_COMMESSA'].iloc[i]
        elif len(comm) == 2:
            v_tgt['PROGR_COMMESSA'].iloc[i] = '00'+v_tgt['PROGR_COMMESSA'].iloc[i]
        elif len(comm) == 3:
            v_tgt['PROGR_COMMESSA'].iloc[i] = '0'+v_tgt['PROGR_COMMESSA'].iloc[i]
        else:
            v_tgt['PROGR_COMMESSA'].iloc[i] = v_tgt['PROGR_COMMESSA'].iloc[i]

    #v_tgt = v_tgt[["PROGR_COMMESSA","COD_MACCHINA","VEL_TIRATURA_PREVISTA",]]

    #if reparto=='INCO':
        #v_tgt = v_tgt.drop_duplicates()
    v_tgt['commessa'] = v_tgt['ANNO_COMMESSA'].astype(str)+ '00' + v_tgt['PROGR_COMMESSA']
    v_tgt['key'] = (v_tgt['COD_MACCHINA'].astype(str) + v_tgt['commessa']).str.replace(" ","")
    v_tgt = v_tgt[["key","VEL_TIRATURA_PREVISTA"]]
    #v_tgt = v_tgt[["key","VEL_TIRATURA_PREVISTA"]]
    v_tgt = v_tgt.drop_duplicates()

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


    matricole_nomi = db_presenze[['Matricola','Cognome','Nome']].drop_duplicates()
    matricole_nomi['fullname'] = matricole_nomi['Cognome'] +' '+ matricole_nomi['Nome']
    dic_matricole = dict(zip(matricole_nomi.Matricola, matricole_nomi.fullname))
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
                    st.warning(f"Verificare l'orario della matricola {matricola} - {dic_matricole[matricola]}, registrazione mancante o <10h da uscita a entrata")
                else:
                    st.warning(f"Rimossa matricola {matricola} - {dic_matricole[matricola]}, un solo evento registrato")

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

    with st.expander('Registro correzioni file orari', icon=':material/zoom_in:'):
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


    db_ore['cognome_nome']=[db_ore.Cognome.iloc[i]+' '+db_ore.Nome.iloc[i] for i in range(len(db_ore))]
    db_ore = db_ore.merge(db_mansioni[['cognome_nome','Mansione','classificazione','turnazione']], how='left', left_on='cognome_nome', right_on='cognome_nome')
    db_ore['turnazione'] = db_ore['turnazione'].fillna('turnista')
    db_ore['classificazione'] = db_ore['classificazione'].fillna('diretto')
    delta = 60
    delta_spezzati = 240

    db_ore['Turno']=None
    db_ore['ingresso_adj']=None
    for i in range(len(db_ore)):
        # suddivisa la logica di correzione ingresso ed imputazione turno.
        # gli indiretti hanno un altro delta altrimenti sarebbero considerati sul turno sbagliato
        # per gli indiretti serve solo per calcolare correttamente il tempo, in quanto il loro impatto si calcola sulla giornata intera
        lim_inf_t1 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t1']['inizio']) - dt.timedelta(minutes=delta)
        lim_sup_t1 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t1']['inizio']) + dt.timedelta(minutes=delta)
        lim_inf_t2 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t2']['inizio']) - dt.timedelta(minutes=delta)
        lim_sup_t2 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t2']['inizio']) + dt.timedelta(minutes=delta)
        lim_inf_t3 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t3']['inizio']) - dt.timedelta(minutes=delta)
        lim_sup_t3 = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t3']['inizio']) + dt.timedelta(minutes=delta)


        lim_inf_t1_s = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t1']['inizio']) - dt.timedelta(minutes=delta_spezzati)
        lim_sup_t1_s = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t1']['inizio']) + dt.timedelta(minutes=delta_spezzati)
        lim_inf_t2_s = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t2']['inizio']) - dt.timedelta(minutes=delta_spezzati)
        lim_sup_t2_s = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t2']['inizio']) + dt.timedelta(minutes=delta_spezzati)
        lim_inf_t3_s = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t3']['inizio']) - dt.timedelta(minutes=delta_spezzati)
        lim_sup_t3_s = dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t3']['inizio']) + dt.timedelta(minutes=delta_spezzati)


        check = db_ore.ingresso.iloc[i]
        if db_ore.turnazione.iloc[i] != 'spezzato':
            if check > lim_inf_t1 and check < lim_sup_t1:
                db_ore['Turno'].iloc[i]='t1'
                db_ore['ingresso_adj'].iloc[i]=dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t1']['inizio'])
            elif check > lim_inf_t2 and check < lim_sup_t2:
                db_ore['Turno'].iloc[i]='t2'
                db_ore['ingresso_adj'].iloc[i]=dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t2']['inizio'])
            else:
                db_ore['Turno'].iloc[i]='t3'
                db_ore['ingresso_adj'].iloc[i]=dt.datetime.combine(db_ore.ingresso.iloc[i].date(), orari_turni['t3']['inizio'])
        
        else:
            if check > lim_inf_t1_s and check < lim_sup_t1_s:
                db_ore['Turno'].iloc[i]='t1'
                db_ore['ingresso_adj'].iloc[i]=check
            elif check > lim_inf_t2_s and check < lim_sup_t2_s:
                db_ore['Turno'].iloc[i]='t2'
                db_ore['ingresso_adj'].iloc[i]=check
            else:
                db_ore['Turno'].iloc[i]='t3'
                db_ore['ingresso_adj'].iloc[i]=check
            
    db_ore['Presenza_act']=[np.round(((db_ore.uscita.iloc[i] - db_ore.ingresso.iloc[i]).seconds)/3600, 1) for i in range(len(db_ore))]
    db_ore['Presenza_adj']=[np.round(((db_ore.uscita.iloc[i] - db_ore.ingresso_adj.iloc[i]).seconds)/3600, 1) for i in range(len(db_ore))]

    if st.toggle('Visualizza dettaglio presenze per turno'):
        'db_ore'
        date_min = db_ore.Data.min()
        db_ore = db_ore[db_ore.Mansione.astype(str) != 'nan']
        db_ore['temp'] = [mans[:3]for mans in db_ore.Mansione ]
        st.write(db_ore[db_ore.Data==date_min].sort_values(by=['temp','Turno','classificazione']))
        db_ore = db_ore.drop(columns='temp')
    
    # aggiustamento ore di presenza
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

    db_ore['reparto'] = [mans[:3] for mans in db_ore.Mansione.astype(str)]
    db_ore_tot = db_ore.copy()
    db_ore = db_ore[db_ore.classificazione == 'diretto']         

    ore_group = db_ore[['Data','reparto','Turno','Presenza']].groupby(by=['Data','reparto','Turno'], as_index=False).sum()
    ore_tot_group = db_ore_tot[['Data','reparto','Turno','Presenza']].groupby(by=['Data','reparto','Turno'], as_index=False).sum()
    #tengo solo la prima data delle due (il minimo), perchè è quella completa (l'ultimo turno della seconda è parziale)
    data_prima = ore_group.Data.min()
    ore_group = ore_group[ore_group.Data == data_prima]
    ore_tot_group= ore_tot_group[ore_tot_group.Data == data_prima]
    ore_tot_group = ore_tot_group.rename(columns={'Presenza':'Ore_totali'})
    
    ore_group = ore_group.merge(ore_tot_group[['reparto','Turno','Ore_totali']], how='left', left_on=['reparto','Turno'], right_on=['reparto','Turno'])
 
    db_fogli['anno'] = [stringa[:4] for stringa in db_fogli.DATA_ORA]
    db_fogli['mese'] = [stringa[4:6] for stringa in db_fogli.DATA_ORA]
    db_fogli['giorno'] = [stringa[6:8] for stringa in db_fogli.DATA_ORA]
    db_fogli['ora'] = [stringa[9:11] for stringa in db_fogli.DATA_ORA]
    db_fogli['minuto'] = [stringa[12:14] for stringa in db_fogli.DATA_ORA]

    db_fogli['anno'] = db_fogli['anno'].astype(int)
    db_fogli['mese'] = db_fogli['mese'].astype(int)
    db_fogli['giorno'] = db_fogli['giorno'].astype(int)
    db_fogli['ora'] = db_fogli['ora'].astype(int)
    db_fogli['minuto'] = db_fogli['minuto'].astype(int)
  
    db_fogli['inizio'] = [dt.datetime(db_fogli.anno.iloc[i], db_fogli.mese.iloc[i], db_fogli.giorno.iloc[i], db_fogli.ora.iloc[i], db_fogli.minuto.iloc[i]) for i in range(len(db_fogli))]
    db_fogli['fine'] = [db_fogli.inizio.iloc[i] + timedelta(hours=db_fogli.DURATA_STEP.iloc[i]) for i in range(len(db_fogli))]

    db_fogli['Data'] = [data.date() for data in db_fogli.DATA_ATTIVITA]
    db_fogli = ut.sdoppia(db_fogli, orari_turni2,'inizio','fine',['COD_MACCHINA','inizio'] )
    db_fogli['durata_calcolata'] = [np.round((db_fogli['fine'].iloc[i] - db_fogli['inizio'].iloc[i]).seconds/3600,5) for i in range(len(db_fogli))]
    db_fogli['appoggio'] = np.where(db_fogli['DURATA_STEP'] != 0, db_fogli['DURATA_STEP'], 1)
    db_fogli['appoggio_calc'] = np.where(db_fogli['durata_calcolata'] != 0, db_fogli['durata_calcolata'], 1)
    db_fogli['ripartizione'] = np.where(db_fogli.check.astype(str) != 'None',db_fogli['appoggio_calc'] / db_fogli['appoggio'], 1)
    db_fogli['pezzi_adj'] = db_fogli['QTA_PRODOTTA'] * db_fogli['ripartizione']
    db_fogli['scarti_adj'] = db_fogli['QTA_SCARTI'] * db_fogli['ripartizione']
    db_fogli['key'] = (db_fogli['COD_MACCHINA'] + db_fogli['COD_COMMESSA']).str.replace(" ","")
    db_fogli = db_fogli.merge(v_tgt.groupby('key').max(), how='left', left_on='key', right_on='key') #facendo groupby-max ho preso il valore + alto per ogni key
    db_fogli['VEL_TIRATURA_PREVISTA'] = db_fogli['VEL_TIRATURA_PREVISTA'].fillna(999999999) #COSì IL RAPPORTO DIVENTA 0
    db_fogli['ton'] = np.where(db_fogli.VEL_TIRATURA_PREVISTA != 0,(db_fogli.pezzi_adj + db_fogli.scarti_adj)*(1/db_fogli.VEL_TIRATURA_PREVISTA),0)
    db_fogli['vel_puntuale'] = db_fogli.ton / (db_fogli.durata_calcolata + 0.0001)
    db_fogli['Data'] = [data.date() for data in db_fogli.DATA_ATTIVITA]
    db_fogli['orario'] = [data[-5:] for data in db_fogli.DATA_ORA.astype(str)]
    db_fogli['ora_']=[dt.datetime.strptime(data_str,'%H.%M').time() for data_str in db_fogli.orario.astype(str)]
    db_fogli['DATA_ATTIVITA'] = [dt.datetime.combine(db_fogli.Data.iloc[i],db_fogli.ora_.iloc[i]) for i in range(len(db_fogli))]
    db_fogli['QTA_PRODOTTA']=db_fogli['pezzi_adj']

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
    # in db_fogli calcolo il tempo operativo netto

    layout_alert=[
     "DATA_ATTIVITA",
     "turno",
     "DES_REPARTO",
     "COD_MACCHINA",
     "DES_CLIENTE",
     "VEL_TIRATURA_PREVISTA",
     "vel_puntuale",
     "pezzi_adj",
     "scarti_adj",
     "durata_calcolata",
     "ton"
    # "COD_COMMESSA",
    # "CAPOCONTO",
     #"DES_ARTICOLO",
     #"NUM_FUSTELLA",
     #"TIPO_ATTIVITA",
     #"COD_DES_ATTIVITA",
     #"RAGG_ATTIVITA",
     #"DURATA_STEP",
     #"QTA_PRODOTTA",
    # "QTA_SCARTI",
    # "DES_OPERATORE",
     #"DES_OPERATORI",
    # "anno","mese",
    # "giorno",
    # "ora",
     #"minuto",
    # "inizio",
     #"fine",
    #"check",
    # "appoggio",
    # "appoggio_calc",
    # "ripartizione",   
     #"key",   
     #"Data",
     #"orario",
     #"ora_",
     ]


    st.info('La tabella sotto mostra le righe con velocità anomala (molto superiore allo standard) dovute a dichiarazione di troppi pezzi in poco tempo')
    st.write(db_fogli[(db_fogli.vel_puntuale > 2) & (db_fogli.pezzi_adj > 100) & (db_fogli.DES_REPARTO != 'ACCO') & db_fogli.VEL_TIRATURA_PREVISTA != 0][layout_alert])

    st.info('Registrazioni con valori di velocità prevista non coerenti o mancanti (999999999) ')
    st.write(db_fogli[(db_fogli.pezzi_adj > 100) & (db_fogli.DES_REPARTO != 'ACCO') & ((db_fogli.VEL_TIRATURA_PREVISTA == 0) |(db_fogli.VEL_TIRATURA_PREVISTA == 999999999)) ][layout_alert])

    #STAMPA

    # FUSTELLA

    # PIEGA INCOLLA

    db_fogli_inco = db_fogli[db_fogli.DES_REPARTO == 'INCO'][['turno','QTA_PRODOTTA','ton']].groupby(by='turno', as_index=False).sum()
    db_ore_inco = ore_group[ore_group.reparto == 'INC'].merge(db_fogli_inco, how='left',left_on='Turno',right_on='turno').drop(columns='turno')
    db_ore_inco = db_ore_inco[:2]
    db_ore_inco['F/mh'] = np.round(db_ore_inco.QTA_PRODOTTA.astype(float) / db_ore_inco.Presenza.astype(float),0)
    db_ore_inco['mh/h_std'] = np.round(db_ore_inco.Presenza.astype(float)/db_ore_inco.ton.astype(float),0)

    tab1, tab2 = st.tabs(['Ultima giornata caricata', 'Andamento'])

    with tab1:
        st.subheader(f'Produttività {data_prima}', divider='grey')
        st.subheader('Stampa', divider='blue')
        
        c1_st, c2_st, c3_st, c4_st = st.columns([3,1,1,1])
        with c1_st:
            with st.expander('Correzione ore turno stampa',icon=":material/edit:"):
                add_stampa = []
                add_t1_s = st.number_input('Ore aggiuntive turno 1', step=0.1)
                add_t2_s = st.number_input('Ore aggiuntive turno 2', step=0.1)
                add_t3_s = st.number_input('Ore aggiuntive turno 3', step=0.1)
                add_stampa.append(add_t1_s)
                add_stampa.append(add_t2_s)
                add_stampa.append(add_t3_s)       

            db_fogli_stam = db_fogli[db_fogli.DES_REPARTO == 'STAM'][['turno','QTA_PRODOTTA','ton']].groupby(by='turno', as_index=False).sum()
            db_ore_stam = ore_group[ore_group.reparto == 'STM'].merge(db_fogli_stam, how='left',left_on='Turno',right_on='turno').drop(columns='turno')
            # correzione con ore aggiunte
            db_ore_stam=db_ore_stam.rename(columns={'Presenza':'Presenza_draft', 'Ore_totali':'Ore_tot_draft'})
            db_ore_stam['Presenza'] = db_ore_stam['Presenza_draft'] + add_stampa
            db_ore_stam['Ore_totali'] = db_ore_stam['Ore_tot_draft'] + add_stampa

            db_ore_stam['F/mh'] = np.round(db_ore_stam.QTA_PRODOTTA.astype(float) / db_ore_stam.Presenza.astype(float),0)
            db_ore_stam['mh/h_std'] = np.round( db_ore_stam.Presenza.astype(float)/db_ore_stam.ton.astype(float),0)

            db_ore_stam
            st.divider()
            st.metric('FOGLI ORA UOMO GIORNATA | indiretti INCLUSI', value='{:0.0f}'.format(db_ore_stam['QTA_PRODOTTA'].sum()/db_ore_stam['Ore_totali'].sum()))
            st.divider()
        with c2_st:
            st.metric('FOGLI ORA UOMO T1', value=db_ore_stam['F/mh'].iloc[0], border=True)
        with c3_st:
            st.metric('FOGLI ORA UOMO T2', value=db_ore_stam['F/mh'].iloc[1], border=True)
        with c4_st:
            st.metric('FOGLI ORA UOMO T3', value=db_ore_stam['F/mh'].iloc[2], border=True)


        st.subheader('Fustella', divider='blue')
        c1_fs, c2_fs, c3_fs, c4_fs = st.columns([3,1,1,1])
        with c1_fs:
            with st.expander('Correzione ore turno fustella',icon=":material/edit:"):
                add_fustella = []
                add_t1_f = st.number_input('Ore aggiuntive turno 1', step=0.1, key='f1')
                add_t2_f = st.number_input('Ore aggiuntive turno 2', step=0.1, key='f2')
                add_t3_f = st.number_input('Ore aggiuntive turno 3', step=0.1, key='f3')
                add_fustella.append(add_t1_f)
                add_fustella.append(add_t2_f)
                add_fustella.append(add_t3_f) 

            db_fogli_fus = db_fogli[db_fogli.DES_REPARTO == 'FUST']
            db_fogli_fus = db_fogli[db_fogli.DES_REPARTO == 'FUST'][['turno','QTA_PRODOTTA','ton']].groupby(by='turno', as_index=False).sum()
            db_ore_fus = ore_group[ore_group.reparto == 'FST'].merge(db_fogli_fus, how='left',left_on='Turno',right_on='turno').drop(columns='turno')
            # correzione con ore aggiunte
            db_ore_fus=db_ore_fus.rename(columns={'Presenza':'Presenza_draft', 'Ore_totali':'Ore_tot_draft'})
            db_ore_fus['Presenza'] = db_ore_fus['Presenza_draft'] + add_fustella
            db_ore_fus['Ore_totali'] = db_ore_fus['Ore_tot_draft'] + add_fustella

            db_ore_fus['F/mh'] = np.round(db_ore_fus.QTA_PRODOTTA.astype(float) / db_ore_fus.Presenza.astype(float),0)
            db_ore_fus['mh/h_std'] = np.round( db_ore_fus.Presenza.astype(float)/db_ore_fus.ton.astype(float),0)

            db_ore_fus
            st.divider()
            st.metric('FOGLI ORA UOMO GIORNATA | indiretti INCLUSI', value='{:0.0f}'.format(db_ore_fus['QTA_PRODOTTA'].sum()/db_ore_fus['Ore_totali'].sum()))
            st.divider()
        with c2_fs:
            st.metric('FOGLI ORA UOMO T1', value=db_ore_fus['F/mh'].iloc[0], border=True)
        with c3_fs:
            st.metric('FOGLI ORA UOMO T2', value=db_ore_fus['F/mh'].iloc[1], border=True)
        with c4_fs:
            st.metric('FOGLI ORA UOMO T3', value=db_ore_fus['F/mh'].iloc[2], border=True)


        st.subheader('Piega incolla', divider='blue')
        c1_in, c2_in, c3_in, c4_in = st.columns([3,1,1,1])
        with c1_in:
            with st.expander('Correzione ore turno piega-incolla',icon=":material/edit:"):
                add_incolla = []
                add_t1_i = st.number_input('Ore aggiuntive turno 1', step=0.1, key='i1')
                add_t2_i = st.number_input('Ore aggiuntive turno 2', step=0.1, key='i2')
                add_incolla.append(add_t1_i)
                add_incolla.append(add_t2_i)

            db_fogli_inco = db_fogli[db_fogli.DES_REPARTO == 'INCO'][['turno','QTA_PRODOTTA','ton']].groupby(by='turno', as_index=False).sum()
            db_ore_inco = ore_group[ore_group.reparto == 'INC'].merge(db_fogli_inco, how='left',left_on='Turno',right_on='turno').drop(columns='turno')
            db_ore_inco = db_ore_inco[:2]
            # correzione con ore aggiunte
            db_ore_inco=db_ore_inco.rename(columns={'Presenza':'Presenza_draft', 'Ore_totali':'Ore_tot_draft'})
            db_ore_inco['Presenza'] = db_ore_inco['Presenza_draft'] + add_incolla
            db_ore_inco['Ore_totali'] = db_ore_inco['Ore_tot_draft'] + add_incolla

            db_ore_inco['F/mh'] = np.round(db_ore_inco.QTA_PRODOTTA.astype(float) / db_ore_inco.Presenza.astype(float),0)
            db_ore_inco['mh/h_std'] = np.round(db_ore_inco.Presenza.astype(float)/db_ore_inco.ton.astype(float),0)
            db_ore_inco
            st.divider()
            st.metric('ORE_uomo / ORE_std GIORNATA | indiretti INCLUSI', value='{:0.2f}'.format(db_ore_inco['Ore_totali'].sum()/db_ore_inco['ton'].sum()))

        with c2_in:
            #st.metric('PEZZI ORA UOMO T1', value=db_ore_inco['F/mh'].iloc[0], border=True)
            st.metric('ORE_uomo / ORE_std T1', value='{:0.2f}'.format(db_ore_inco['Presenza'].iloc[0]/db_ore_inco['ton'].iloc[0]), border=True)
        with c3_in:
            #st.metric('PEZZI ORA UOMO T2', value=db_ore_inco['F/mh'].iloc[1], border=True)
            st.metric('ORE_uomo / ORE_std T2', value='{:0.2f}'.format(db_ore_inco['Presenza'].iloc[1]/db_ore_inco['ton'].iloc[1]), border=True)


        # PRIMO CARICAMENTO SU GITHUB =====================================================
        #pe.upload_file(username, token, db_ore_stam, repository_name, db_path_stampa)
        #pe.upload_file(username, token, db_ore_fus, repository_name, db_path_fustella)
        #pe.upload_file(username, token, db_ore_inco, repository_name, db_path_incolla)

        updated_stam = pe.retrieve_file(username, token, repository_name, db_path_stampa)
        updated_fust = pe.retrieve_file(username, token, repository_name, db_path_fustella)
        updated_inco = pe.retrieve_file(username, token, repository_name, db_path_incolla)

        st.divider()
        if st.button('Aggiorna database', icon=':material/upload:'):

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
            y=updated_inco['mh/h_std']
        ))

        st.subheader('Andamento Stampa')
        #lg_st, gr_st = st.columns([1,7])
        #with lg_st:
         #   st.write('#')
          #  st.write('#')
           # st.image('stampa.png')
       # with gr_st:
        st.plotly_chart(graph_st, key='stampa')
        st.write(updated_stam.drop(columns='Check'))

        st.subheader('Andamento Fustella')
        st.plotly_chart(graph_fu, key='fustella')
        st.write(updated_fust.drop(columns='Check'))

        st.subheader('Andamento Piega-incolla')
        st.plotly_chart(graph_in, key='incolla')
        st.write(updated_inco.drop(columns='Check'))
        
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
        y=updated_inco['mh/h_std']
    ))


    st.subheader('Andamento Stampa')
    st.plotly_chart(graph_st, key='stampa')

    st.subheader('Andamento Fustella')
    st.plotly_chart(graph_fu, key='fustella')

    st.subheader('Andamento Piega-incolla')
    st.plotly_chart(graph_in, key='incolla')
            


# eliminare indiretti nel confronto turni, ma tenerli in un kpi non diviso per turno
