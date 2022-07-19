import pandas as pd
import numpy as np
from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
import matplotlib.pyplot as plt
import streamlit as st
from selenium.webdriver.firefox.options import Options
import os

st.title('WCISS Speedtest')
select_page = st.selectbox('Select Website', options=['Start page', 'Search page', 'Upload page'])

if select_page == 'Start page':
    page = 'https://wciss.wintershalldea.net/'
elif select_page == 'Search page':
    page = 'https://wciss.wintershalldea.net/Search'
elif select_page == 'Upload page':
    page = 'https://wciss.wintershalldea.net/Upload'

test_number = st.number_input('Number of performance tests', min_value=1, max_value=200, value=100)

press = st.button('Run')

if press:
    #service = EdgeService(executable_path=EdgeChromiumDriverManager().install())
    os.system('sbase install geckodriver')
    os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

    performance_data = np.ones((test_number+1, 3)).astype(object)

    for i in range(test_number+1):
        #driver = webdriver.Edge(service=service)
        opts = Options()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)
        driver.get(page)

        navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
        responseStart = driver.execute_script("return window.performance.timing.responseStart")
        domComplete = driver.execute_script("return window.performance.timing.domComplete")

        backendPerformance_calc = responseStart - navigationStart
        frontendPerformance_calc = domComplete - responseStart

        print(i)
        print("Back End: %s" % backendPerformance_calc)
        print("Front End: %s" % frontendPerformance_calc)

        performance_data[i] = [i, backendPerformance_calc, frontendPerformance_calc]

        driver.close()

    print(performance_data)

    x = np.array(performance_data[:, 0]).astype(float)
    y = np.array(performance_data[:, 1]).astype(float)
    z = np.array(performance_data[:, 2]).astype(float)

    coefs_back = np.polyfit(x, y, 0)
    coefs_front = np.polyfit(x, z, 0)
    fit_back = np.polyval(coefs_back, x)
    fit_front = np.polyval(coefs_front, x)

    print('Average Backend Performance: ' + str(coefs_back))
    print('Average Frontend Performance: ' + str(coefs_front))

    df = pd.DataFrame(performance_data, columns=['Test Number', 'Backend Performance', 'Frontend Performance'])

    fig, ax = plt.subplots()
    ax.plot(performance_data[:, 0], performance_data[:, 1], label='Backend Performance', color='b', marker='o')
    ax.plot(performance_data[:, 0], performance_data[:, 2], label='Frontend Performance', color='r', marker='o')
    ax.plot(x, fit_back, color='b', label=str(coefs_back)[1:len(str(coefs_back))-1])
    ax.plot(x, fit_front, color='r', label=str(coefs_front)[1:len(str(coefs_front))-1])
    plt.xlim((0, test_number))
    plt.xlabel('number of tests')
    plt.ylabel('response time in ms')
    ax.legend()
    st.pyplot(fig)

    st.table(df)
