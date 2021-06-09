# %%
import urllib
import json
import pandas as pd
import numpy as np
import plotly.express as px

# DB: 0010636, 삼성: 0010633, 현대: 0010634, KB: 0010635, 메리츠: 0010626
# (SI003) A11: 현예금, A12: 유가증권, A14: 대출채권, A15: 부동산, A21: 고정자산, A22: 기타자산, A3: 특별계정자산
AUTH = '7774090942ede970746a7cd9b2e10577'

# %%
def get_stats(service: str, params: dict = {}) -> pd.DataFrame:
    if service == 'companySearch':
        params['partDiv'] = 'I'
    elif service == 'statisticsListSearch':
        params['lrgDiv'] = 'I'
    params['lang'] = 'kr'
    params['auth'] = AUTH
    tmp = []
    for k, v in params.items():
        tmp.append(k + "=" + v)
    query = '&'.join(tmp)
    url = f'http://fisis.fss.or.kr/openapi/{service}.json?{query}'
    res = urllib.request.urlopen(url)
    data = json.loads(res.read())
    df = pd.DataFrame(data['result']['list'])
    return df

# %%
company = pd.DataFrame(get_stats('companySearch'))
rpt_list = pd.DataFrame(get_stats('statisticsListSearch'))

# %%
params = {}
params['term'] = 'Q'
params['startBaseMm'] = '201001'
params['endBaseMm'] = '202012'
params['financeCd'] = '0010636'
params['listNo'] = 'SI003'
fin_pos = get_stats('statisticsInfoSearch', params)

asset = fin_pos \
        .query('base_month == "202012"') \
        .query('account_cd in ["A11", "A12", "A14", "A15", "A21", "A22", "A3"]') \
        .astype({'a': float, 'b': float}) \
        .assign(classification = lambda x: x.account_nm.str.replace('[(|)| |ㆍ]', '', regex=True)) \
        .assign(a = lambda x: np.round(x.a/1e12,1)) \
        .rename(columns={'a': 'amount'})

px.pie(asset, values='amount', names='classification')