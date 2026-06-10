import re
import pandas as pd
import nltk
from pandas import *

response='https://www.transit.dot.gov/sites/fta.dot.gov/files/2020-10/2019%20Facility%20Inventory.xlsx'
response
df=pd.read_excel(response)
df

al=df[['Agency Name','Year Built','Condition Assessment Date','Notes']]
Notes_only=al[al.Notes.notnull()]
Notes_only
#Notes_only #6474 facilities have associated notes

#Useful Life Using Regex Tokenization

Notes_year=Notes_only[Notes_only['Notes'].str.contains('[0-9]{4}')] #497 have rows that are probably years
Notes_year
Year_Note=re.findall('\S[0-9]{4}',Notes_only['Notes'][1])
comparison=Notes_year['Year Built'] - Notes_year['[0-9]{4}']
Notes_only['Notes']



