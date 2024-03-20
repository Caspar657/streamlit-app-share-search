import streamlit as st
import numpy as np 
import pandas as pd 
from datetime import datetime
import base64
import pytrends

st.title('AFFINITY Share of Search Calculator')

startDate = st.date_input("Start Date", min_value=datetime(2004,1,1))
endDate = st.date_input("End Date", min_value=datetime(2004,1,1))


#text input
user_input = st.text_input("Enter search terms separated by a comma")


#country dropdown
country = st.selectbox("Select country", ("Worldwide", "Australia", "United Kingdom"))


#state/region dropdown
if country == "Australia":
    state = st.selectbox("Select state / region", ("Whole country", "NSW", "ACT", "QLD", "VIC", "SA", "WA", "TAS"))
elif country == "United Kingdom":
    state = st.selectbox("Select state/region", ("Whole country", "England", "Northern Ireland", "Scotland", "Wales"))
else:
    state = ""


#defining country dict
country_dict = {"Australia" :"AU",
                "United Kingdom": "GB",
                "Worldwide": ""}


#defining dict to construct geo code query
state_dict = {"Whole country": "",
            "NSW": "-NSW",
            "ACT": "-ACT",
            "QLD": "-QLD",
            "VIC": "-VIC",
            "SA": "-SA",
            "WA": "-WA",
            "TAS": "-TAS",
            "England": "-ENG",
            "Northern Ireland": "-NIR",
            "Scotland": "-SCT",
            "Wales": "-WLS",
            "": ""}


button = st.button(label='Fetch Share of Search')

keyword_list = user_input.split(", ")

# function defined
def share_of_search(kw_list, start_date, end_date, geography):

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
        
        def retrieve_search_trends(kw_list, start_date, end_date):

        #query Google Trends

            def pytrends_query(kw_list, start_date, end_date):
                from pytrends.request import TrendReq
                mytrend = TrendReq(hl='en-US', tz=360)
                mytrend.build_payload(kw_list, cat=0, timeframe=start_date + " " + end_date, geo=geography, gprop='')
                
                df = mytrend.interest_over_time()
                if 'isPartial' in df.columns:
                    df = df.drop(columns = 'isPartial') #remove extra column
                else:
                    pass
                
                return df
                
            def iterate_over_max(kw_list, start_date, end_date):
                # check that variables passed in correctly and get dataframe for first 5 keywords
                if isinstance(kw_list, list):
                    df = pytrends_query(kw_list[:5], start_date, end_date)
                else:
                    raise Exception('kw_list myst be a list.')
                
                # get max value and keyword for the first five terms
                max_col_name = df.max().idxmax() #gets column name of maximum value in Dataframe
                
                # checking that keyword list is complete. If not, loop continues
                while set(kw_list) != set(df.columns):
                    for keyword in kw_list:
                        if keyword in df.columns:
                            pass
                        else:
                            max_test_list = [max_col_name, keyword]
                            df2 = pytrends_query(max_test_list, start_date, end_date)
                            # if the next keyword maximum value is smaller than the current index, then add the column with those values to the dataframe
                            if df2.max()[0] >= df2.max()[1]: 
                                df[keyword] = df2[keyword]
                            # if the next keyword is larger, then update the max column name and break to start the loop again
                            else: 
                                max_col_name = keyword
                                new_max_keyword = kw_list[:4].append(max_col_name)
                                df = pytrends_query(new_max_keyword, start_date, end_date)
                                break

                return df

            df = iterate_over_max(kw_list, start_date, end_date)

            return df


        df = retrieve_search_trends(kw_list, start_date, end_date)
        if 'isPartial' in df.columns:
            df = df.drop(columns = 'isPartial') #remove extra column
        else:
        	pass
        
        #apply transformations to data
        rolling_df = calculate_rolling(df)
        total_df = add_total(rolling_df)
        share_search_df = share_search(total_df)

        return share_search_df


# getting geo code
country_geo = country_dict[country]
state_geo = state_dict[state]

geography = country_geo + state_geo


# button press
if button:
    sDate = startDate.strftime("%Y-%m-%d")
    eDate = endDate.strftime("%Y-%m-%d")
    df_1 = share_of_search(keyword_list, sDate, eDate, geography)
    st.line_chart(data=df_1)
    st.write(df_1)
else:
    pass


download = st.button('Download CSV File')
if download:
    keyword_list = user_input.split(", ")
    sDate = startDate.strftime("%Y-%m-%d")
    eDate = endDate.strftime("%Y-%m-%d")
    df_1 = share_of_search(keyword_list, sDate, eDate, geography)
    csv = df_1.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings
    linko= f'<a href="data:file/csv;base64,{b64}" download="Share_of_search.csv">Download csv file</a>'
    st.markdown(linko, unsafe_allow_html=True)

