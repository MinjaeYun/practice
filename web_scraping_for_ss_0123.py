# -*- coding: utf-8 -*-
"""
# **Web Scraping for Social Sciences**
Minjae Yun

[Text book](https://jakevdp.github.io/PythonDataScienceHandbook/)

---


## Final Goals
*   Obtain and read url page 
*   Clean and stack information into a dataframe 
*   Repeat the same tasks
*   Trials & errors


---


  Lecture 1 : Setting Up and Basics (1/15)
##  Lecture 2 : Basic Web Scraping (1/23)
  Lecture 3 : Advanced Web Scraping </br>


---
"""

# !pip install [package name] 
# !pip install selenium
from selenium.webdriver import Firefox, FirefoxProfile
# from selenium.webdriver.common.action_chains import ActionChains # put several actions into one code
# from selenium.webdriver.support import expected_conditions as EC # conditionally run a code
# from selenium.webdriver.support.wait import WebDriverWait # letting the program wait
# from selenium.webdriver.common.by import By # specify what kind of syntax we use from the web page
import os 
import requests 
from bs4 import BeautifulSoup
import pandas as pd
import re

"""## 1. Selenium for navigating through the page
* Introduction [link](https://selenium-python.readthedocs.io/installation.html)
* Make sure downloading a machine driver first (above link)
"""

# set up the directory so that the program can know where to pull out the browser
root_directory = "C:\\downloads"
driver = Firefox(executable_path=root_directory+'/geckodriver')

# navigate through page
driver.get("http://securities.stanford.edu/filings.html")
go = driver.find_element_by_xpath('//*[@id="records"]/table/tbody/tr[1]/td[1]')

i = 0
while i < 21:
    xpath = '//*[@id="records"]/table/tbody/tr['+str(i)+']/td[1]'
    go = driver.find_element_by_xpath(xpath)
    go.click()
    i+=1

# get the content
html = driver.page_source
b = BeautifulSoup(html, 'lxml')

# get to the next page
# 1) mannually click the page 
go = driver.find_element_by_xpath('//*[@id="records"]/div[2]/ul/li[3]/a')
go.click()
'//*[@id="records"]/div[2]/ul/li[2]/a'
'//*[@id="records"]/div[2]/ul/li[4]/a'
# 2) we can iterate the link again
i=2
while i < 10:
    link = "http://securities.stanford.edu/filings.html?page="+str(i)
    driver.get(link)

"""## 2. Requests 
* First step: get the url page and each section
"""

url = "http://securities.stanford.edu/filings-case.html?id=100120"
soup = requests.get(url) 
# or soup=requests.get("http://securities.stanford.edu/filings-case.html?id=100120")
b = BeautifulSoup(soup.text, 'lxml') 
# assign 5 sections into 5 different objects
summary = b.findAll("section", {"id":"summary"})
company = b.findAll("section", {"id":"company"})
fic = b.findAll("section", {"id":"fic"})
ref = b.findAll("section", {"id":"ref"})
other = b.findAll("section",{"id":"other"})

# tables are easily pulled by pandas package but this is not recommended in this web page
tab = pd.read_html(url)
print(tab[0])

# 1) summary: a plain text 
summary=summary[0].text

# better to individually define functions when repetition is expected
def sortInfo(L):
    Output=L
    # assign empty lists for titles and actual contents
    Output_t = []
    Output_c = []
    Output_t = [re.findall(".*(?=: )",x)[0] for x in Output] # everything before ": "
    Output_c = [re.findall("(?<=: ).*",x)[0] for x in Output] # everything after ": "
    Output = pd.DataFrame(Output_c).transpose()
    # cleaning titles to work in Stata
    Output_t = [x.lower() for x in Output_t]  
    Output_t = [x.replace(" ","_") for x in Output_t] 
    Output_t = [x.replace("#","num") for x in Output_t] 
    Output.columns=Output_t
    return Output
def getInfo(bs4Result): # get individual info from bs4 element
    Output = []
    Output = [x.text for x in bs4Result] # convert the individual info into a list
    Output = "\n".join(Output) 
    Output = Output.split("\n")
    Output = [x for x in Output if x!='']
    Output = sortInfo(Output) # we defined sortInfo function above
    return Output

# recab list operator
a = [1,2,3,4]
a = [1+x for x in a]
print(a)

# 2) company: 
c_tit = company[0].findAll("p",{"class":"lead"})
c_content = company[0].findAll("div",{"class":"row-fluid"})
c = [] 
for j in range(len(c_tit)):
    c.append(c_content[j].text)
c = "\n".join(c).split("\n")
# "\n".join(LIST) joins elements in LIST
# STRING.split("\n") splits elements in STRING 
c = [x for x in c if x != ''] # get rid of empty information
c = sortInfo(c)

# 3) first identified complaint
fic_info = fic[0].findAll("div",{'class':'row-fluid'})
fic_info = getInfo(fic_info) 
# change the column names to separte from reference
cols = list(fic_info.columns)
cols = ["fic_"+x for x in cols]
fic_info.columns = cols
pltf_name = fic[0].findAll("ol",{'class':'styled'})
pltf_name = pltf_name[0].text
pltf_name = [x for x in pltf_name.split("\n") if x !='']

# 4) reference
ref_info = ref[0].findAll("div",{'class':'row-fluid'})
ref_info = getInfo(ref_info)
# change the column names to separte from fic
cols = list(ref_info.columns)
cols = ["ref_"+x for x in cols]
ref_info.columns = cols
pltf_name = ref[0].findAll("ol",{'class':'styled'})
pltf_name = pltf_name[0].text
pltf_name = [x for x in pltf_name.split("\n") if x !='']

# convert collected information into a dataframe
df = pd.DataFrame() 
df = pd.concat([df,c], axis=1, ignore_index=True) # company information
df =pd.concat([df,fic_info],axis=1, ignore_index=True) # fic information
df =pd.concat([df,ref_info],axis=1, ignore_index=True) # reference information
df.columns = list(c.columns) + list(fic_info.columns) + list(ref_info.columns) # fix column names

"""## 3. Iteration
* for/while loops work sequentially
* Indentation matters
"""

for i in range(10):
    print(i)

print(list(range(10)))

i=0
while i < 10:
    print(i)
    i+=1
    #or equivalently i=i+1

# why do we use while loop? 
i=200
while i % 2 == 0:
    print(i)
    i=i/2

for j in range(10): # something we get to tentatively determine in the case of for loop
    number = 200/2**j
    if number % 2 == 0:
        print(number)