import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import plotly.express as px
import numpy as np
import math
from LYNCE import verificar_login
from TRADUTOR import traaducaoapp
from shared_components import create_sidebar_navigation
from dateutil.relativedelta import relativedelta
import openai
import io
import time


st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown('Você precisa fazer <a href="https://lyncefinanceiro.streamlit.app/" target="_self">login</a> primeiro.', unsafe_allow_html=True)
    st.stop()



# Create sidebar navigation and get translated texts
textos, _ = create_sidebar_navigation()

# Welcome section
bemvido, x, language = st.columns([0.3,0.5,0.2], vertical_alignment='bottom')

with bemvido:
  st.write(f"{textos['BEMVINDO']} {st.session_state.name}!")

sheeitid = st.session_state.id
sheetname = st.session_state.arquivo

def lerdados(sheet_id_login_password,sheet_name_login_password):

  scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive'
]
  service_account_info = st.secrets["gcp_service_account"]
  creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
  client = gspread.authorize(creds)


  workbook = client.open_by_key(sheet_id_login_password)
  
  
  url = f"https://docs.google.com/spreadsheets/d/{sheet_id_login_password}/gviz/tq?tqx=out:csv&sheet={sheet_name_login_password}"

  dados_records = pd.read_csv(url, decimal='.', index_col=False)

  return dados_records,workbook



lançamentos, workbook = lerdados(sheeitid, sheetname)
sheet = workbook.get_worksheet(0)
hoje = pd.to_datetime(date.today()) 
lançamentos = sheet.get_all_values()
lançamentos_CONTAS = pd.DataFrame(lançamentos[1:], columns=lançamentos[0])
lançamentos_CONTAS = lançamentos_CONTAS.set_index('ID')
lançamentos_CONTAS = lançamentos_CONTAS[lançamentos_CONTAS["ANALISE"]!="ANALÍTICA"]
lançamentos_CONTAS = lançamentos_CONTAS[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]

#CARTÕES#
lancamento_cartao = workbook.get_worksheet(1)
tabela_lancamentos_cartao = lancamento_cartao.get_all_values()
tabela_lancamentos_cartao = pd.DataFrame(tabela_lancamentos_cartao[1:], columns=tabela_lancamentos_cartao[0])
tabela_lancamentos_cartao = tabela_lancamentos_cartao.set_index('ID')
tabela_lancamentos_cartao.index = tabela_lancamentos_cartao.index.astype(int)
tabela_lancamentos_cartao = tabela_lancamentos_cartao[tabela_lancamentos_cartao["ANALISE"]!="ANALÍTICA"]
tabela_lancamentos_cartao = tabela_lancamentos_cartao[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]




lançamentos = pd.concat([lançamentos_CONTAS, tabela_lancamentos_cartao], axis=0)

lançamentos = lançamentos.reset_index()
lançamentos = lançamentos[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]


sheetia = workbook.get_worksheet(6)
iainfo = sheetia.get_all_values()
iainfo = pd.DataFrame(iainfo[1:], columns=iainfo[0])
st.title("💰 Personal Finance AI Insights")
st.subheader("📑 Your Finance Table")
st.dataframe(lançamentos)
openai.api_key = st.secrets["OPENAI_API_KEY"]

iainfouser = iainfo.iat[0,0]
iainfothread = iainfo.iat[0,1]
iainfolast = iainfo.iat[0,2]
iainfoassistantid = iainfo.iat[0,3]



st.write(f'Last analysis in {iainfolast}')
if st.button("📊 Analyze with OpenAI"):
  with st.spinner("Uploading and analyzing..."):
            # ➕ Convert dataframe to CSV
        csv_buffer = io.StringIO()
        lançamentos.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode()

        #st.write(iainfouser)
        if iainfothread == "":
          thread = openai.beta.threads.create()
          thread_id = thread.id
          sheetia.update_acell('B2', thread_id)  # Save thread ID to Google Sheets
        else:
          thread_id = iainfothread

        file = openai.files.create(
        file=csv_bytes,
        purpose='assistants'
    )
        
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content="Here is my personal finances revenues and expenses. There are data from differente dates and years. The data use portuguese language, so be aware that 'DESPESAS' are expenses and 'RECEITAS' are incomes. Please analyze ALL the dataset carefully, think about the trending in expenses and incomes during all period and please provide your best insights and advices for current situation. If you are going to show values, please keep using the plus values for incomes and negative values for expenses",
            attachments=[
                {
                    "file_id": file.id,
                    "tools": [{"type": "code_interpreter"}]
                }
            ]
        )
        
        run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=iainfoassistantid  # Use your pre-saved assistant ID
    )

        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                st.error(f"Run {run_status.status}")
                break
            time.sleep(1)

        messages = openai.beta.threads.messages.list(
        thread_id=thread_id
    )

        # Get the last message (assistant response)
        response_text = messages.data[0].content[0].text.value

        st.subheader("🔍 AI Insights")
        st.markdown(response_text)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheetia.update_acell('C2', now)

st.subheader("💬 Continue the Conversation")

# Input for user questions
user_question = st.text_input("Type your question about your finances...")

if st.button("Send Question"):
    if iainfothread == "":
        st.warning("⚠️ No analysis found. Please run the analysis first.")
    else:
        with st.spinner("Waiting for AI response..."):

            # Send user's message to the thread
            openai.beta.threads.messages.create(
                thread_id=iainfothread,
                role="user",
                content=f'Please analyse the whole dataset and {user_question}'
            )

            # Run the assistant
            run = openai.beta.threads.runs.create(
                thread_id=iainfothread,
                assistant_id=iainfoassistantid
            )

            # Wait for completion
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=iainfothread,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    st.error(f"Run {run_status.status}")
                    break
                time.sleep(1)

            # Retrieve assistant's reply
            messages = openai.beta.threads.messages.list(
                thread_id=iainfothread
            )

            reply = messages.data[0].content[0].text.value

            st.subheader("🤖 Assistant's Reply")
            st.markdown(reply)


        
