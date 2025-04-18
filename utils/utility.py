import pandas as pd
import streamlit as st
import numpy as np
import datetime as dt
from io import BytesIO
import xlsxwriter

@st.cache_data
def upload(path, foglio=None):
    df = pd.read_excel(path, sheet_name=foglio)
    return df

def overlap(start1, end1, start2, end2):
    # prese due attività caratterizzate ognuna da inizio e fine, la funzione restituisce la durata della loro sovrapposizione
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)

    if overlap_end > overlap_start:
        overlap = (overlap_end - overlap_start).seconds

    else:
        overlap = 0
    return overlap/3600

def pausa(df, inizio, fine, col_pausa, pause):
        
        for i in range(len(df)):
            start = dt.datetime(df[inizio].iloc[i].year, 
                                    df[inizio].iloc[i].month, 
                                    df[inizio].iloc[i].day, 
                                    df[inizio].iloc[i].hour, 
                                    df[inizio].iloc[i].minute, 
                                    df[inizio].iloc[i].second)
            
            end = dt.datetime(df[fine].iloc[i].year, 
                                df[fine].iloc[i].month, 
                                df[fine].iloc[i].day, 
                                df[fine].iloc[i].hour, 
                                df[fine].iloc[i].minute, 
                                df[fine].iloc[i].second)

            # Check pause del giorno 1
            pausa_1t1_start_inizio = dt.datetime.combine(start.date(), pause['1t1']['inizio'])
            pausa_1t1_start_fine = dt.datetime.combine(start.date(), pause['1t1']['fine'])
            over1 = overlap(start,end,pausa_1t1_start_inizio,pausa_1t1_start_fine)
            pausa_2t1_start_inizio = dt.datetime.combine(start.date(), pause['2t1']['inizio'])
            pausa_2t1_start_fine = dt.datetime.combine(start.date(), pause['2t1']['fine'])
            over2 = overlap(start,end,pausa_2t1_start_inizio,pausa_2t1_start_fine)
            pausa_3t1_start_inizio = dt.datetime.combine(start.date(), pause['3t1']['inizio'])
            pausa_3t1_start_fine = dt.datetime.combine(start.date(), pause['3t1']['fine'])
            over3 = overlap(start,end,pausa_3t1_start_inizio,pausa_3t1_start_fine)

            pausa_1t2_start_inizio = dt.datetime.combine(start.date(), pause['1t2']['inizio'])
            pausa_1t2_start_fine = dt.datetime.combine(start.date(), pause['1t2']['fine'])
            over4 = overlap(start,end, pausa_1t2_start_inizio, pausa_1t2_start_fine)
            pausa_2t2_start_inizio = dt.datetime.combine(start.date(), pause['2t2']['inizio'])
            pausa_2t2_start_fine = dt.datetime.combine(start.date(), pause['2t2']['fine'])
            over5 = overlap(start,end, pausa_2t2_start_inizio, pausa_2t2_start_fine)
            pausa_3t2_start_inizio = dt.datetime.combine(start.date(), pause['3t2']['inizio'])      
            pausa_3t2_start_fine = dt.datetime.combine(start.date(), pause['3t2']['fine'])
            over6 = overlap(start,end, pausa_3t2_start_inizio, pausa_3t2_start_fine)

            pausa_1t3_start_inizio = dt.datetime.combine(start.date(), pause['1t3']['inizio'])
            pausa_1t3_start_fine = dt.datetime.combine(start.date(), pause['1t3']['fine'])
            over7 = overlap(start, end, pausa_1t3_start_inizio, pausa_1t3_start_fine)
            pausa_2t3_start_inizio = dt.datetime.combine(start.date(), pause['2t3']['inizio'])
            pausa_2t3_start_fine = dt.datetime.combine(start.date(), pause['2t3']['fine'])
            over8 = overlap(start, end, pausa_2t3_start_inizio, pausa_2t3_start_fine)
            pausa_3t3_start_inizio = dt.datetime.combine(start.date(), pause['3t3']['inizio'])
            pausa_3t3_start_fine = dt.datetime.combine(start.date(), pause['3t3']['fine'])
            over9 = overlap(start, end, pausa_3t3_start_inizio, pausa_3t3_start_fine)


            # Check pause del giorno 2
            if start.date() != end.date():
                pausa_1t1_end_inizio = dt.datetime.combine(end.date(), pause['1t1']['inizio'])
                pausa_1t1_end_fine = dt.datetime.combine(end.date(), pause['1t1']['fine'])
                over10 = overlap(start,end, pausa_1t1_end_inizio, pausa_1t1_end_fine)
                pausa_2t1_end_inizio = dt.datetime.combine(end.date(), pause['2t1']['inizio'])
                pausa_2t1_end_fine = dt.datetime.combine(end.date(), pause['2t1']['fine'])
                over11 = overlap(start,end, pausa_2t1_end_inizio, pausa_2t1_end_fine)
                pausa_3t1_end_inizio = dt.datetime.combine(end.date(), pause['3t1']['inizio'])
                pausa_3t1_end_fine = dt.datetime.combine(end.date(), pause['3t1']['fine'])
                over12 = overlap(start,end, pausa_3t1_end_inizio, pausa_3t1_end_fine)

                pausa_1t2_end_inizio = dt.datetime.combine(end.date(), pause['1t2']['inizio'])
                pausa_1t2_end_fine = dt.datetime.combine(end.date(), pause['1t2']['fine'])
                over5 = overlap(start, end, pausa_1t2_end_inizio, pausa_1t2_end_fine)
                pausa_2t2_end_inizio = dt.datetime.combine(end.date(), pause['2t2']['inizio'])
                pausa_2t2_end_fine = dt.datetime.combine(end.date(), pause['2t2']['fine'])
                over5 = overlap(start, end, pausa_2t2_end_inizio, pausa_2t2_end_fine)
                pausa_3t2_end_inizio = dt.datetime.combine(end.date(), pause['3t2']['inizio'])
                pausa_3t2_end_fine = dt.datetime.combine(end.date(), pause['3t2']['fine'])
                over5 = overlap(start, end, pausa_3t2_end_inizio, pausa_3t2_end_fine)

                pausa_1t3_end_inizio = dt.datetime.combine(end.date(), pause['1t3']['inizio'])
                pausa_1t3_end_fine = dt.datetime.combine(end.date(), pause['1t3']['fine'])
                over6 = overlap(start, end, pausa_1t3_end_inizio, pausa_1t3_end_fine)
                pausa_2t3_end_inizio = dt.datetime.combine(end.date(), pause['2t3']['inizio'])
                pausa_2t3_end_fine = dt.datetime.combine(end.date(), pause['2t3']['fine'])
                over6 = overlap(start, end, pausa_2t3_end_inizio, pausa_2t3_end_fine)
                pausa_3t3_end_inizio = dt.datetime.combine(end.date(), pause['3t3']['inizio'])
                pausa_3t3_end_fine = dt.datetime.combine(end.date(), pause['3t3']['fine'])
                over6 = overlap(start, end, pausa_3t3_end_inizio, pausa_3t3_end_fine)

            else:
                over10=0
                over11=0
                over12=0
                over13=0
                over14=0
                over15=0
                over16=0
                over17=0
                over18=0

            over_tot = (over1 + over2 + over3 + over4 + over5 + over6 + over7 + over8 + over9 + over10 + over11 + over12 + over13 + over14 + over15 + over16 + over17 + over18)
            df[col_pausa].iloc[i] = over_tot

def quota_turno(df, inizio, fine, col_turno, turni, turno):
        for i in range(len(df)):

            start = dt.datetime(df[inizio].iloc[i].year, 
                                    df[inizio].iloc[i].month, 
                                    df[inizio].iloc[i].day, 
                                    df[inizio].iloc[i].hour, 
                                    df[inizio].iloc[i].minute, 
                                    df[inizio].iloc[i].second)
            
            end = dt.datetime(df[fine].iloc[i].year, 
                                df[fine].iloc[i].month, 
                                df[fine].iloc[i].day, 
                                df[fine].iloc[i].hour, 
                                df[fine].iloc[i].minute, 
                                df[fine].iloc[i].second)
            
                 
            if (turno=='t3') & (start.time() >= dt.time(0,0)) & (start.time() < dt.time(21,0)):   
                 t_start = dt.datetime.combine((start - dt.timedelta(days=1)).date(), turni[turno]['inizio']) # tolgo un giorno all'inizio del turno
            else:
                t_start = dt.datetime.combine(start.date(), turni[turno]['inizio'])

                 
            if (turno=='t3') & (start.time() <= dt.time(23,59,59)) & (start.time() > dt.time(21,0)):
                 t_fine = dt.datetime.combine((end + dt.timedelta(days=1)).date(), turni[turno]['fine'])
            else:
                 t_fine = dt.datetime.combine(end.date(), turni[turno]['fine'])
                 

            over = overlap(start,end,t_start,t_fine)

            df[col_turno].iloc[i] = over

def sdoppia(df, turnazione, start, end, sort):
    df['check']=None
    df_append = pd.DataFrame(columns=df.columns)

    for i in range(len(df)):
        reparto = df['DES_REPARTO'].iloc[i]
        turni = turnazione[reparto]
        #st.write(turni['t1'])
        #st.stop()
        inizio = df[start].iloc[i]
        fine = df[end].iloc[i]
        if (inizio < dt.datetime.combine(inizio.date(), turni['t1']['inizio'])) & (fine > dt.datetime.combine(inizio.date(), turni['t1']['inizio'])):
            df['check'].iloc[i]='t3-t1'
            df_append.loc[len(df_append)]=df.iloc[i]
            df[end].iloc[i] = dt.datetime.combine(fine.date(), turni['t1']['inizio'])
            df_append[start].loc[len(df_append)-1]=dt.datetime.combine(inizio.date(), turni['t1']['inizio'])

        if (inizio < dt.datetime.combine(inizio.date(), turni['t2']['inizio'])) & (fine > dt.datetime.combine(inizio.date(), turni['t2']['inizio'])):
            df['check'].iloc[i]='t1-t2'
            df_append.loc[len(df_append)]=df.iloc[i]
            df[end].iloc[i] = dt.datetime.combine(fine.date(), turni['t2']['inizio'])
            df_append[start].loc[len(df_append)-1]=dt.datetime.combine(inizio.date(), turni['t2']['inizio'])

        if (inizio < dt.datetime.combine(inizio.date(), turni['t3']['inizio'])) & (fine > dt.datetime.combine(inizio.date(), turni['t3']['inizio'])):
            df['check'].iloc[i]='t2-t3'
            df_append.loc[len(df_append)]=df.iloc[i]
            df[end].iloc[i] = dt.datetime.combine(fine.date(), turni['t3']['inizio'])
            df_append[start].loc[len(df_append)-1]=dt.datetime.combine(inizio.date(), turni['t3']['inizio'])

    df = pd.concat([df,df_append])
    #df = df.sort_values(by='Prima dosata FULL', ascending=True)
    df = df.sort_values(by=sort, ascending=True)
    df = df.reset_index(drop=True)
    return df

def cal_upload(path, import_config):
    frames=[]
    for rep in import_config.keys():
        df = pd.read_excel(path, sheet_name=import_config[rep]['name'])
        df = df[df.columns[:import_config[rep]['colonne']]]
        df['Giorno'] = df['Giorno'].ffill()
        df['Data'] = df['Data'].ffill()
        df_work = df[import_config[rep]['col_select']].copy()
        df_work = df_work.melt(id_vars=['Giorno','Data','Turno'])
        df_work['variable'] = [stringa[:4] for stringa in df_work.variable]
        df_work['reparto'] = rep
        df_work['ttd'] = None
        for i in range(len(df_work)):
            turno = df_work.Turno.iloc[i]
            pian = df_work.value.iloc[i]
            #if pian == 'SI':
            #    df_work['ttd'].iloc[i] = import_config[rep]['durata'][turno]
            #else:
            #    df_work['ttd'].iloc[i] = 0
            df_work['ttd'].iloc[i] = pian # 31/01/2025 modifica introdotta per prendere direttamente le ore pianificate del turno (il venerdì ce ne sono solo 4)
        frames.append(df_work)
    
    output = pd.concat(frames)
    output = output.reset_index(drop=True)
    output['Turno'] = [stringa.replace("T","") for stringa in output.Turno]
    output['Data'] = [data.date() for data in output.Data]
    output['key'] = output['Data'].astype(str)+ output.Turno
    #output['key'] = output['Data'].astype(str) + output['variable'] +'-'+ output.Turno
    return output

def scarica_excel(df, filename):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()

    st.download_button(
        label="Download Excel workbook",
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.ms-excel"
    )









