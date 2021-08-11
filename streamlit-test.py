import streamlit as st
import numpy as np 
import pandas as pd 
from datetime import datetime
import base64

st.title('AFFINITY Share of Search Calculator')

startDate = st.date_input("Start Date", min_value=datetime(2004,1,1))
endDate = st.date_input("End Date", min_value=datetime(2004,1,1))

user_input = st.text_input("Enter up to 5 search terms separated by a comma")

button = st.button(label='Fetch Share of Search')

keyword_list = user_input.split(", ")

# function defined
def share_of_search(kw_list, start_date, end_date):

        def calculate_rolling(df): #calculate 12 month rolling average of search index
            columns = list(df) #create list of column names
            for column in columns:
                col_name = str(column) + '_rolling'
                df[col_name] = df.rolling(window=12)[column].mean()
            df = df.drop(columns = columns)
            return df 

        def add_total(df): #add all columns together to get the rolling total
            df['rolling_total'] = df.sum(axis=1)
            return df

        def share_search(df): #divide each search term by the total to get the % share of search
            columns = list(df)
            columns.remove('rolling_total')
            for column in columns:
                col_name = str(column) + '_SOS'
                df[col_name] = df[column] / df.rolling_total
            df = df.drop(columns = columns)
            df = df.drop(columns = ['rolling_total'])
            return df
        
        #query Google Trends
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='en-US', tz = 600)
        pytrends.build_payload(kw_list, cat=0, timeframe=start_date + " " + end_date, geo='AU', gprop='')

        df = pytrends.interest_over_time()
        if 'isPartial' in df.columns:
            df = df.drop(columns = 'isPartial') #remove extra column
        else:
        	pass
        
        #apply transformations to data
        rolling_df = calculate_rolling(df)
        total_df = add_total(rolling_df)
        share_search_df = share_search(total_df)

        return share_search_df

# button press
if button:
    sDate = startDate.strftime("%Y-%m-%d")
    eDate = endDate.strftime("%Y-%m-%d")
    df_1 = share_of_search(keyword_list, sDate, eDate)
    st.line_chart(data=df_1)
    st.write(df_1)
else:
    pass

download = st.button('Download CSV File')
if download:
    sDate = startDate.strftime("%Y-%m-%d")
    eDate = endDate.strftime("%Y-%m-%d")
    df_1 = share_of_search(keyword_list, sDate, eDate)
    csv = df_1.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings
    linko= f'<a href="data:file/csv;base64,{b64}" download="Share_of_search.csv">Download csv file</a>'
    st.markdown(linko, unsafe_allow_html=True)

