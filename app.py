import os, random, sys, time
from urllib.parse import urlparse
from selenium import webdriver
import time
import pandas as pd
import numpy as np
import streamlit as st

st.title('TJT Project')

df1 = pd.DataFrame(pd.read_excel('TJT_datasets.xlsx'))
df = pd.DataFrame(index=[0], columns=df1.columns)
jobid = st.text_input("Enter Job ID:")
if st.button('Proceed'):

    st.title('Job Description')
    try:
        for i in range(len(df1)):
            if int(jobid) == df1['JID'][i]:
                for j in range(8):
                    df[df1.columns[j]][0] = df1[df1.columns[j]][i]
    except:
        pass
    st.dataframe(df)


    def text_process(mess):
        """
        Takes in a string of text, then performs the following:
        1. Remove all punctuation
        2. Remove all stopwords
        3. Returns a list of the cleaned text
        """
        # Check characters to see if they are in punctuation
        nopunc = [char for char in mess if char not in string.punctuation]

        # Join the characters again to form the string.
        nopunc = ''.join(nopunc)

        # Now just remove any stopwords
        return [word for word in nopunc.split() if word.lower() not in stopwords.words('english')]

#    corpus=[' '.join(text_process(df['Jdesc'][0].split('skills')[1:]))]
 #   corpus

    #st.dataframe(df['Jdesc'][0])
    step2a_df = pd.DataFrame(index=[0],columns=['Company Name', 'Job Location', 'Headquarter', 'Company Details', 'Job Title', 'Roles', 'Skills', 'PHM'])
    #st.dataframe(step2a_df)

    for i in df:
        if 'company' in i:
            step2a_df['Company Name'][0] = df[i][0]
        if 'location' in i:
            step2a_df['Job Location'][0] = df[i][0]
        if 'role' in i or 'function' in i:
            step2a_df['Roles'][0] = df[i][0]
        if 'position' in i or 'title' in i:
            step2a_df['Job Title'][0] = df[i][0]
        if 'skills' in i or 'keywords' in i:
            step2a_df['Skills'][0] = df[i][0]
        #if 'desc' in i or 'description' in i:
            #step2a_df['Skills'][0] = df[i][0]
    
    #Web Scraping
    browser = webdriver.Chrome('driver/chromedriver.exe')
    browser.get('https://www.linkedin.com/uas/login')
    file = open('config.txt')
    lines = file.readlines()
    username = lines[0]
    password = lines[1]
    elementID = browser.find_element_by_id('username')
    elementID.send_keys(username)
    elementID = browser.find_element_by_id('password')
    elementID.send_keys(password)
    elementID.submit()

    company_name = df['Jcompany'][0]
    fullLink = 'https://www.linkedin.com/search/results/companies/?keywords='+company_name
    browser.get(fullLink)
    element = browser.find_element_by_link_text(company_name)
    element.click()
    time.sleep(5)
    browser.execute_script("window.scrollTo(0, 500)")
    element = browser.find_element_by_link_text("See all")
    element.click()
    time.sleep(5)
    browser.execute_script("window.scrollTo(0, 100)")
    try:
        company_details = browser.find_element_by_class_name('break-words').text
        st.title("Company Details")
        st.write(company_details)
        step2a_df['Company Details']= company_details
        company_headquarters = browser.find_element_by_class_name('mb3').find_element_by_class_name('overflow-hidden').find_element_by_xpath('(//dd[5])').text
        st.title("Company Headquarters")
        st.write(company_headquarters)
        step2a_df['Headquarter']=company_headquarters
    except:
        pass

    PHM = pd.DataFrame(pd.read_csv('PHM.csv'))
    for i in range(len(PHM['Interviewee'])):
        if PHM['Interviewee'][i] == step2a_df['Job Title'][0]:
            step2a_df['PHM'][0]=PHM['Hiring Manager'][i]

    st.title('Job Details')
    st.dataframe(step2a_df)

    def check_empty(data):
        if data == '':
            return ''
        else:
            return str(data) + '%2C'
    PHM = step2a_df['PHM'][0]
    location = step2a_df['Job Location'][0]
    domain = step2a_df['Roles'][0]
    temp_url = check_empty(PHM) + check_empty(location) + check_empty(domain)
    fullLink = browser.current_url[:-6] + '/people/?keywords=' +  temp_url[:-3]
    browser.get(fullLink)

    PHM_df = pd.DataFrame(index=[i for i in range(10)],columns=['Employee Name', 'Job Title', 'Job Location', 'About'])
    #st.title("Sample Dataframe")
    #st.dataframe(PHM_df)
    current_url = browser.current_url
    for i in range(1,14):
        try:
            if i > 12:
                browser.execute_script("window.scrollTo(0, 1500)")
                time.sleep(3)
            browser.find_element_by_class_name('org-people-profiles-module__profile-list').find_element_by_xpath('(//li[@class="org-people-profiles-module__profile-item"]['+str(i)+'])').find_element_by_class_name('org-people-profile-card__profile-info').click()
            time.sleep(3)
            PHM_df['Employee Name'][i-1] = browser.find_element_by_class_name('pv-top-card--list').find_element_by_tag_name('li').text
            PHM_df['Job Title'][i-1] = browser.find_element_by_class_name('ph5').find_element_by_class_name('mt2').find_element_by_class_name('mt1').text
            loc = browser.find_element_by_class_name('pv-top-card--list-bullet').find_element_by_tag_name('li').text
            if "connection" in loc:
                PHM_df['Job Location'][i-1] = np.nan
            else:
                PHM_df['Job Location'][i-1] = loc
            PHM_df['About'][i-1] = browser.find_element_by_class_name('pv-about__summary-text').text
        except:
            pass
        browser.get(current_url)

    st.title("Potential Hiring Managers Details")
    st.dataframe(PHM_df)

    PHM_df=PHM_df.dropna(how='all')
    PHM_df = PHM_df.reset_index(drop=True)
    scores_df = pd.DataFrame({'scores':[0] * len(PHM_df)})


    for i in range(len(PHM_df)):
        #Scoring based on About Section
        if str(np.nan) in str(PHM_df['About'][i]):
            scores_df['scores'][i] = 1
        elif 'hiring' or 'hire' or 'recruiting' or 'recruitment' in str(PHM_df['About'][i]):
            scores_df['scores'][i] = 3
        else:
            scores_df['scores'][i] = 2

        #Scoring based on Location
        if str(np.nan) in str(PHM_df['Job Location'][i]):
            scores_df['scores'][i] += 1
        elif 'chennai' in str(PHM_df['Job Location'][i]).lower(): #take chennai from dataframe on employee use split(',')[0] to take only chennai
            scores_df['scores'][i] += 3
        else:
            scores_df['scores'][i] += 2

        #Scoring based on domain
        if str(np.nan) in str(PHM_df['Job Title'][i]):
            scores_df['scores'][i] += 1
        elif 'Product Management' in str(PHM_df['Job Title'][i]): #take prodcut management from dataframe on employee
            scores_df['scores'][i] += 3
        else:
            scores_df['scores'][i] += 2

    #st.dataframe(scores_df)

    #Top 3 PHM's
    top3 = scores_df.index.values[:3]
    top3_df = pd.DataFrame(columns=['Employee Name', 'Job Title', 'Job Location', 'About'])
    for i in range(len(top3)):
        top3_df  = top3_df.append(PHM_df.iloc[top3[i]])
    top3_df = top3_df.reset_index(drop=True)
    st.title('Top 3 Potential Hiring Manager')
    st.dataframe(top3_df)
