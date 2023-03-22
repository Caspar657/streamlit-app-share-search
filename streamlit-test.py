import streamlit as st
import numpy as np 
import pandas as pd 
from datetime import datetime
import base64

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

        def calculate_rolling(df): #calculate 6 month rolling average of search index
            columns = list(df) #create list of column names
            for column in columns:
                col_name = str(column) + '_rolling'
                df[col_name] = df.rolling(window=6)[column].mean()
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
                #adding request headers to bypass Google
                request_args = {"authority": "trends.google.com",
                    "method": "GET",
                    "path": "/trends/api/autocomplete/rupert?hl=en-US&tz=-660",
                    "scheme": "https",
                    "accept": "application/json, text/plain, */*",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "cookie": "OGPC=19033657-1:19033886-1:19033941-1:; SEARCH_SAMESITE=CgQI3ZcB; OTZ=6940735_12_12_133440_16_395520; NID=511=k8bZtTtj3MLjSlrtSuErN5sXHLLCrzRh8ww1AW413sUGhFzgrtscuMmVfAH-NTIlwuI6KX11uK5G0GqmfcjJEkRt65aKknhyO8T3A8bBNb9N12BCjcoDPcdXbVQc3Yo_n4Pd3aAdgk3MV2OPBXIpjzui5auH-lBi9HBgdXBQCEUkK3Z_RtmZQVcz69jb0pCZ4-3W0OhnzCMyUPogEcq8Jazzq0ULoqTg2KlR31lcP7Br2gtnrPA-m7dNeKorUcjfIF9PwNIrB8hhwb8sOglpWVqPZJnfEavVJ7cgp0SLvDB46JHgk5lQO7P4Z6r1WKJKz37jmPw9-IY8ADHzXRyP8yG1; S=billing-ui-v3=JiJd58DXAy-29bylAEET7qUfAfds9_nH:billing-ui-v3-efe=JiJd58DXAy-29bylAEET7qUfAfds9_nH; SID=UgjnaG0JIOZXWjL4EUjpVEk7L4z3OtD9pZAnG7lv0at7kWAIxKvmqVA-ESY9ApGDwJUjkw.; __Secure-1PSID=UgjnaG0JIOZXWjL4EUjpVEk7L4z3OtD9pZAnG7lv0at7kWAIbLwZDOcy8q_K-yyMaLiMHw.; __Secure-3PSID=UgjnaG0JIOZXWjL4EUjpVEk7L4z3OtD9pZAnG7lv0at7kWAIN2uljmpTUHedN6O4u8UxCQ.; HSID=Abb0FHJ9Rc-fZ2I1U; SSID=AgF4urAnjOE7YPMoi; APISID=vUS0443UOwyKTulF/A-OLsCVykRhDa6HLA; SAPISID=22BPlBATZGbzOkMy/ANxbkj4Gf55CI6GVx; __Secure-1PAPISID=22BPlBATZGbzOkMy/ANxbkj4Gf55CI6GVx; __Secure-3PAPISID=22BPlBATZGbzOkMy/ANxbkj4Gf55CI6GVx; AEC=ARSKqsJ4tRzLHjth73H72eKw_ZyffGFlORW8ZDfCgR8Akochwb7wQlAkt6U; 1P_JAR=2023-03-22-02; SIDCC=AFvIBn-J7TGd0Au_NGsYrsuFNJE5KA4rd9q8JB4U36-FmoKIqEJ9mfCddwXamiSMJwxQ1zLaZKM; __Secure-1PSIDCC=AFvIBn8EmRXfV0BxmxpbrtknrU8-iur5ZgRyyM9Q_9cXR1OMNBSmC8Mc-CR2JjHZoUMinW_hnwI; __Secure-3PSIDCC=AFvIBn9r4E_WoRGpF8hJkdboQlzy25O64lfC2mqVA5gq8KXLh5NvhH2JDYPX9OTFrjG3UT1De7o",
                    "referer": "https://trends.google.com/trends/explore?q=Trump&date=now%201-d&geo=AU&hl=en",
                    "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                    "sec-ch-ua-arch": "arm",
                    "sec-ch-ua-bitness": "64",
                    "sec-ch-ua-full-version": "106.0.5249.119",
                    "sec-ch-ua-full-version-list": '"Chromium";v="106.0.5249.119", "Google Chrome";v="106.0.5249.119", "Not;A=Brand";v="99.0.0.0"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "macOS",
                    "sec-ch-ua-platform-version": "12.5.1",
                    "sec-ch-ua-wow64": "?0",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                    "x-client-data": "CI62yQEIprbJAQjBtskBCKmdygEIgPzKAQiSocsBCPyqzAEI5JfNAQ=="
                    }
                pytrends = TrendReq(hl='en-US', tz = 600, request_args = request_args)
                pytrends.build_payload(kw_list, cat=0, timeframe=start_date + " " + end_date, geo=geography, gprop='')
                
                df = pytrends.interest_over_time()
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

