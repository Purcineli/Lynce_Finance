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
from LYNCE import verificar_login
st.set_page_config(layout="wide")
st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )
if 'username' in st.session_state:
  st.write(f"Bem-vindo, {st.session_state.name}!")

st.write('07/05/2025 - Lançamento da primeira versão')