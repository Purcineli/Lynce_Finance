import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta

import plotly.express as px
import numpy as np
import math
from main import verificar_login
st.set_page_config(layout="wide")
if 'username' in st.session_state:
  st.write(f"Bem-vindo, {st.session_state.name}!")

st.write('07/05/2025 - Lançamento da primeira versão')