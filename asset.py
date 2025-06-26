import pandas as pd 
import sqlite3

df = pd.read_csv('개발행위허가정보_20250515_전국.csv', encoding='cp949',  on_bad_lines='skip')

conn = sqlite3.connect("developer.db")

df.to_sql("my_table", conn, if_exists="replace", index=False)

conn.close()

print(df.head())