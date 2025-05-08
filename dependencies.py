import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import toml
from google.auth.transport.requests import Request
from google.oauth2 import service_account




def getloginandpasswords():
  scopes = ["https://www.googleapis.com/auth/spreadsheets"]
  service_account_info = st.secrets["gcp_service_account"]
  creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
  client = gspread.authorize(creds)
  sheet_id_login_password= st.secrets["idkey"]
  sheet_name_login_password= st.secrets["namekey"]
  workbook = client.open_by_key(sheet_id_login_password)

  url = f"https://docs.google.com/spreadsheets/d/{sheet_id_login_password}/gviz/tq?tqx=out:csv&sheet={sheet_name_login_password}"

  dados_lgn = pd.read_csv(url, decimal='.')
  return dados_lgn

