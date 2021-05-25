import streamlit as st
import numpy as np 
import pandas as pd 
from datetime import datetime

st.title('AFFINITY Share of Search Calculator')

startDate = st.date_input("Start Date", min_value=datetime(2004,1,1))
endDate = st.date_input("End Date", min_value=datetime(2004,1,1))

user_input = st.text_input("Enter up to 5 search terms separated by a comma")

button = st.button(label='Fetch Share of Search')

keyword_list = user_input.split(", ")

# function defined
def share_of_search(kw_list, start_date, end_date):

        def calculate_rolling_yearly(df): #calculate 12 month rolling average of search index
            columns = list(df) #create list of column names
            for column in columns:
                col_name = str(column) + '_rolling'
                df[col_name] = df.rolling(window=12)[column].mean()
            df = df.drop(columns = columns)
            return df 

        def calculate_rolling_quarterly(df): #calculate 12 month rolling average of search index
            columns = list(df) #create list of column names
            for column in columns:
                col_name = str(column) + '_rolling'
                df[col_name] = df.rolling(window=3)[column].mean()
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
        df = df.drop(columns = 'isPartial') #remove extra column

        # need to insert steps to calculate more than 5 keywords
        # step 1: select first five elements of list
        # step 2: pull Google Trends data for 5
        # step 3: Find column name of the highest value (which will be 100)
        # step 4: select next 4 elements of the list and add highest value
        # step 5: pull Google Trends data
        # step 6: if highest value column name is not first high value, rerun first pull with highest value.
        # step 7: repeat until all values are checked 
        
        #apply transformations to data. First determine date range to check that rollling average done correctly
        if (end_date - start_date >= datetime.timedelta(days=1825)):
            rolling_df = calculate_rolling_yearly(df)
        elif (end_date - start_date <= datetime.timedelta(days=1825)):
            rolling_df = calculate_rolling_quarterly(df)
        else:
            raise Exception('A date error occured.')
        
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

