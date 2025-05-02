import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st




def getloginandpasswords():

  scopes = ["https://www.googleapis.com/auth/spreadsheets"]
  creds = Credentials.from_service_account_file(r"C:\Users\alepu\OneDrive\Área de Trabalho\Python_projects\CONTROLE_FINANCEIRO\credentials.json", scopes=scopes)
  #D:\Python_projects\CONTROLE_FINANCEIRO
  client = gspread.authorize(creds)
  sheet_id_login_password= st.secrets["idkey"]
  sheet_name_login_password= st.secrets["namekey"]
  workbook = client.open_by_key(sheet_id_login_password)

  url = f"https://docs.google.com/spreadsheets/d/{sheet_id_login_password}/gviz/tq?tqx=out:csv&sheet={sheet_name_login_password}"

  dados_lgn = pd.read_csv(url, decimal='.')
  return dados_lgn

'''lgnpass = getloginandpasswords()
username = 'APURCINELI'
password = 'TESTE123'
x = lgnpass[lgnpass['LOGIN']==username].index[0]
z = lgnpass['SENHA'][x]
#print(z)
try:
    if lgnpass[lgnpass['LOGIN']==username].index[0] >= 0:
        user = lgnpass[lgnpass['LOGIN']==username].index[0]
        print(user)
        if password == lgnpass['SENHA'][user]:
            print(True)
except:
    print(False)'''
