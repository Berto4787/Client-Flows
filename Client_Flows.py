import streamlit as st
import pandas as pd
import numpy as np

st.session_state['ID'] = 0
st.set_page_config(
    layout="wide",
)
##### MARGIN PARAMETERS #####
st.sidebar.markdown("<p style='text-align: center;'font-size:18px;'>IM_SINGLE_POSITION - QCCP</p>", unsafe_allow_html=True)
qccp_margins = pd.DataFrame({'SYMBOL':['Future', 'Call', 'Put'], 'LONG':[1000, 180, 130], 'SHORT':[950, 190, 145]})
qccp_margins = qccp_margins.set_index('SYMBOL')
st.session_state['qccp_margins'] = st.sidebar.data_editor(qccp_margins, disabled=('SYMBOL'))
st.sidebar.markdown("<p style='text-align: center;'font-size:18px;'>ITD THEORETICAL PRICES - MITCH</p>", unsafe_allow_html=True)
theor_prices = pd.DataFrame({'SYMBOL':['Future', 'Call', 'Put'], 'THEORETICAL PRICE':[9500., 5.3, 3.2],
                            'CONTRACT SIZE':[1000, 5, 5]})
theor_prices = theor_prices.set_index('SYMBOL')
st.session_state['theor_prices'] = st.sidebar.data_editor(theor_prices, disabled=('SYMBOL', 'CONTRACT SIZE'))
st.sidebar.markdown("<p style='text-align: center;'font-size:18px;'>EOD PRICES- MITCH OR QCCP REPORTS</p>", unsafe_allow_html=True)
eod_prices = pd.DataFrame({'SYMBOL':['Future', 'Call', 'Put'], 'EOD PRICE T':[9650., 5.5, 3.1],
                          'EOD PRICE T-1':[9300., 4.1, 2.5]})
eod_prices = eod_prices.set_index('SYMBOL')
st.session_state['eod_prices'] = st.sidebar.data_editor(eod_prices, disabled=('SYMBOL'))
st.sidebar.markdown("<p style='text-align: center;'font-size:18px;'>BROKER PARAMETERS - B/O</p>", unsafe_allow_html=True)
st.session_state['mm_buffer'] = st.sidebar.number_input(label='MM Buffer', min_value=0.,max_value=1., value=0.25, step=0.01, format='%.2f', help='MM = max(LONG, SHORT) * (1+ MM Buffer). Note that theoretical price will be added for options')
st.session_state['im_buffer'] = st.sidebar.number_input(label='IM Buffer', min_value=st.session_state['mm_buffer'],max_value=1.,value=st.session_state['mm_buffer'], step=0.01, format='%.2f', help='IM = max(LONG, SHORT) * (1+ IM Buffer). Note that theoretical price will be added for options')
st.sidebar.markdown("<p style='text-align: center;'font-size:18px;'>IM AND MM - COMPUTED BY B/O & SENT TO F/O</p>", unsafe_allow_html=True)
fit_margins = pd.DataFrame(st.session_state['qccp_margins'].max(axis=1))
fit_margins.columns = ['MM']
fit_margins = fit_margins.assign(**{'MM':np.multiply(fit_margins.MM, 1 + st.session_state['mm_buffer']), 'IM':np.multiply(fit_margins.MM, 1 + st.session_state['im_buffer'])})
fit_margins = fit_margins.assign(**{'MM':np.where(fit_margins.index=='Future', fit_margins.MM, np.add(fit_margins.MM, st.session_state['theor_prices']['THEORETICAL PRICE'])), 
                                    'IM':np.where(fit_margins.index=='Future', fit_margins.IM, np.add(fit_margins.IM, st.session_state['theor_prices']['THEORETICAL PRICE']))})
st.session_state['fit_margins'] = fit_margins
st.sidebar.dataframe(st.session_state['fit_margins'])
st.sidebar.markdown("<p style='text-align: center;'font-size:18px;'>CLIENT  COLLATERAL - B/O & F/O</p>", unsafe_allow_html=True)
sod_collateral = pd.DataFrame({'CLIENT': ['Client 1', 'Client 2', 'Client 3'],
                              'COLLATERAL': [2000000, 2000000, 2000000]},
                            index= np.arange(3))
sod_collateral = sod_collateral.set_index('CLIENT')
st.session_state['sod_collateral'] = st.sidebar.data_editor(sod_collateral, disabled=('CLIENT'))

st.session_state['calc_type'] = st.selectbox('TYPE OF CALCULATION', options=['ItD', 'EoD'], index=0)
##### SoD OPEN POSITION #####
st.markdown("<p style='text-align: center; font-size: 22px; font-weight: bold;'>SoD OPEN POSITION</p>", unsafe_allow_html=True)
prev_day_pos = pd.DataFrame({'SYMBOL': ['Future', 'Call', 'Put', 'Future', 'Call', 'Put', 'Future', 'Call', 'Put'],
                              'CLIENT': ['Client 1', 'Client 1', 'Client 1', 'Client 2', 'Client 2', 'Client 2', 'Client 3', 'Client 3', 'Client 3'],
                              'QUANTITY': [0., 0., 0., 0., 0., 0., 0., 0., 0.]},
                            index= np.arange(9))

with st.expander('Click to input SoD client portfolios'):
    st.session_state['prev_day_pos'] = st.data_editor(prev_day_pos, 
                                                      disabled=('SYMBOL', 'CLIENT'),
                                                     use_container_width=True, hide_index=True)
    st.text_area("",
                 """ Clients' net position at SoD. To be mantained by B/O system and disseminated to F/O at SoD.
                         - Quantity: Positive amount indicates long net position whereas negative indices short net position.
                    """, disabled=True)

##### ORDER FORM #####
with st.container():
  buff, col, buff2 = st.columns([1,2,1])
  col.markdown("<p style='text-align: center; font-size: 22px; font-weight: bold;'>ORDER/TRADE SUBMISSION</p>", unsafe_allow_html=True)
  with col.expander('Click to open form'):
    st.session_state['new_client']  = st.selectbox('Client ID', options=['Client 1', 'Client 2', 'Client 3'], index=0)
    st.session_state['new_instrument'] = st.selectbox('Symbol', options=st.session_state['qccp_margins'].index, index=0)
    st.session_state['new_quantity'] = st.number_input(label='Quantity', min_value=1, value=1)
    st.session_state['new_price'] = st.number_input(label='Price' ,min_value=0., step=0.001, value=st.session_state['theor_prices'].loc[st.session_state['new_instrument']]['THEORETICAL PRICE'], format='%.3f')
    st.session_state['new_side']  = st.selectbox('Side', options=['Buy', 'Sell'], index=0)
    st.session_state['new_type']  = st.selectbox('Side', options=['Order', 'Trade'], index=0)
    submit_button = st.button(label='Submit')

  if submit_button:
    st.session_state['ID'] += 1
    new_pos = pd.DataFrame({'CLIENT': st.session_state['new_client'], 
                            'SYMBOL': st.session_state['new_instrument'],
                            'QUANTITY': st.session_state['new_quantity'],
                            'PRICE': st.session_state['new_price'],
                            'SIDE': st.session_state['new_side']},
                          index = [st.session_state['ID']])

    if st.session_state['new_type'] == 'Order':
      new_pos = new_pos.assign(**{'INITIAL MARGIN': np.where((st.session_state['new_instrument']!='Future') & (st.session_state['new_side']=='Buy'), 0.,
                                                             st.session_state['new_quantity'] * st.session_state['fit_margins'].loc[st.session_state['new_instrument']]['IM'])})
      new_pos = new_pos.assign(**{'PENDING PREMIUM': np.where(st.session_state['new_instrument']=='Future', 0.,
                                                              np.where(st.session_state['new_side'] == 'Buy', -1, 1) * st.session_state['new_quantity'] * st.session_state['new_price'] * st.session_state['theor_prices'].loc[st.session_state['new_instrument']]['CONTRACT SIZE'])})
      new_pos = new_pos.assign(**{'CURRENT BUYING POWER':st.session_state['client_bp'].loc[st.session_state['new_client']]['BUYING POWER'],
                                  'TOTAL REQUIREMENT': np.absolute(np.minimum(np.add(np.multiply(-1, new_pos['INITIAL MARGIN']), new_pos['PENDING PREMIUM']), 0))})
      new_pos = new_pos.assign(**{'STATUS': np.where(new_pos['CURRENT BUYING POWER'] > new_pos['TOTAL REQUIREMENT'], 'ACCEPTED', 'REJECTED')})
        
      if 'orders' not in st.session_state.keys():
        st.session_state['orders'] = new_pos
      else:
        st.session_state['orders'] = pd.concat([st.session_state['orders'], new_pos], axis=0, ignore_index= True)
    elif st.session_state['new_type'] == 'Trade':
        if st.session_state['calc_type'] == 'EoD':
            new_pos = new_pos.assign(**{'EOD PRICE T': st.session_state['eod_prices'].loc[st.session_state['new_instrument']]['EOD PRICE T']})
            new_pos = new_pos.assign(**{'RVM': np.where(st.session_state['new_instrument']!='Future', 0.,
                                                        np.where(st.session_state['new_side'] == 'Buy', 1, -1) * st.session_state['new_quantity'] * st.session_state['theor_prices'].loc[st.session_state['new_instrument']]['CONTRACT SIZE'] * (st.session_state['eod_prices'].loc[st.session_state['new_instrument']]['EOD PRICE T']-st.session_state['new_price']))})

        elif st.session_state['calc_type'] == 'ItD':
            new_pos = new_pos.assign(**{'THEORETICAL PRICE': st.session_state['theor_prices'].loc[st.session_state['new_instrument']]['THEORETICAL PRICE']})
            new_pos = new_pos.assign(**{'CVM': np.where(st.session_state['new_instrument']!='Future', 0.,
                                                        np.where(st.session_state['new_side'] == 'Buy', 1, -1) * st.session_state['new_quantity'] * st.session_state['theor_prices'].loc[st.session_state['new_instrument']]['CONTRACT SIZE'] * (st.session_state['theor_prices'].loc[st.session_state['new_instrument']]['THEORETICAL PRICE']-st.session_state['new_price']))})

        new_pos = new_pos.assign(**{'PENDING PREMIUM': np.where(st.session_state['new_instrument']=='Future', 0.,
                                                                np.where(st.session_state['new_side'] == 'Buy', -1, 1) * st.session_state['new_quantity'] * st.session_state['new_price'] * st.session_state['theor_prices'].loc[st.session_state['new_instrument']]['CONTRACT SIZE'])})

        if 'trades' not in st.session_state.keys():                               
            st.session_state['trades'] = new_pos
        else:
            st.session_state['trades'] = pd.concat([st.session_state['trades'], new_pos], axis=0, ignore_index= True)
        st.session_state['day_trades'] = st.session_state['trades'].assign(**{'QUANTITY': np.where(st.session_state['trades']['SIDE']=='Buy',
                                                                                                   st.session_state['trades']['QUANTITY'],
                                                                                                   np.multiply( st.session_state['trades']['QUANTITY'], -1))})
        if st.session_state['calc_type'] == 'EoD':
            st.session_state['day_trades'] = st.session_state['day_trades'].pivot_table(index=['CLIENT', 'SYMBOL'],
                                                                                        values=['QUANTITY', 'PENDING PREMIUM', 'RVM'],
                                                                                        aggfunc='sum')
        elif st.session_state['calc_type'] == 'ItD':
            st.session_state['day_trades'] = st.session_state['day_trades'].pivot_table(index=['CLIENT', 'SYMBOL'],
                                                                                        values=['QUANTITY', 'PENDING PREMIUM', 'CVM'],
                                                                                        aggfunc='sum')
        st.session_state['day_trades'] = st.session_state['day_trades'].reset_index()

##### CVM/RVM CALCULATION SoD POSITION #####
st.session_state['prev_day_pos_calc'] = st.session_state['prev_day_pos'].set_index('SYMBOL').join(st.session_state['eod_prices'], how='left')
st.session_state['prev_day_pos_calc'] = st.session_state['prev_day_pos_calc'].join(st.session_state['theor_prices'], how='left')
st.session_state['prev_day_pos_calc'] = st.session_state['prev_day_pos_calc'].reset_index()

if st.session_state['calc_type'] == 'EoD':
    st.session_state['prev_day_pos_calc'] = st.session_state['prev_day_pos_calc'][['SYMBOL', 'CLIENT', 'QUANTITY', 'EOD PRICE T-1', 'EOD PRICE T', 'CONTRACT SIZE']]
    
elif st.session_state['calc_type'] == 'ItD':
    st.session_state['prev_day_pos_calc'] = st.session_state['prev_day_pos_calc'][['SYMBOL', 'CLIENT', 'QUANTITY', 'EOD PRICE T-1', 'THEORETICAL PRICE', 'CONTRACT SIZE']]

st.session_state['prev_day_pos_calc'] = st.session_state['prev_day_pos_calc'][st.session_state['prev_day_pos_calc']['QUANTITY'] !=0]
if st.session_state['calc_type'] == 'EoD':
    st.dataframe(st.session_state['prev_day_pos_calc'])
    st.session_state['prev_day_pos_calc'] =st.session_state['prev_day_pos_calc'].assign(**{'RVM': np.where(st.session_state['prev_day_pos_calc'].SYMBOL!='Future', 0.,
                                                                                                           np.multiply(np.multiply(st.session_state['prev_day_pos_calc'].QUANTITY,
                                                                                                                       st.session_state['prev_day_pos_calc']['CONTRACT SIZE']),
                                                                                                           np.subtract(st.session_state['prev_day_pos_calc']['EOD PRICE T'],st.session_state['prev_day_pos_calc']['EOD PRICE T-1']))),
                                                                                           'PENDING PREMIUM': 0.})
elif st.session_state['calc_type'] == 'ItD':
    st.session_state['prev_day_pos_calc'] =st.session_state['prev_day_pos_calc'].assign(**{'CVM': np.where(st.session_state['prev_day_pos_calc'].SYMBOL!='Future', 0.,
                                                                                                           np.multiply(np.multiply(st.session_state['prev_day_pos_calc'].QUANTITY,
                                                                                                                                   st.session_state['prev_day_pos_calc']['CONTRACT SIZE']),
                                                                                                                       np.subtract(st.session_state['prev_day_pos_calc']['THEORETICAL PRICE'],st.session_state['prev_day_pos_calc']['EOD PRICE T-1']))),
                                                                                           'PENDING PREMIUM': 0.})

if st.session_state['calc_type'] == 'EoD':
    st.markdown("<p style='text-align: center; font-size: 22px; font-weight: bold;'>REALIZED VARIATION MARGIN - BREAK DOWN</p>", unsafe_allow_html=True)
elif st.session_state['calc_type'] == 'ItD':
    st.markdown("<p style='text-align: center; font-size: 22px; font-weight: bold;'>CONTINGENT VARIATION MARGIN & PENDING PREMIUM - BREAK DOWN</p>", unsafe_allow_html=True)
with st.expander('Click to see break down'):
    if st.session_state['prev_day_pos_calc'].shape[0]:
        if st.session_state['calc_type'] == 'EoD':
            st.markdown("<p style='text-align: center;'font-size:18px;'>SoD OPEN POSITION - RVM CALCULATION </p>", unsafe_allow_html=True)
            st.dataframe(st.session_state['prev_day_pos_calc'], use_container_width=True, hide_index=True)
            st.text_area("",
                         """ Realized Variation Margin (RVM) should be computed EoD by B/O system to MtM futures positons carried forward from previous days to EoD official settlement price.
                         RVM = Quantity * Contract Size * (EoD Price T - EoD Price T-1)""", disabled=True)
        elif st.session_state['calc_type'] == 'ItD':        
            st.markdown("<p style='text-align: center;'font-size:18px;'>SoD OPEN POSITION - CVM CALCULATION </p>", unsafe_allow_html=True) 
            st.dataframe(st.session_state['prev_day_pos_calc'], use_container_width=True, hide_index=True)
            st.text_area("",""" Contingen Variation Margin (CVM) should be computed ItD by F/O system for futures positons carried forward from previous days as a component of Buying Power computation.
                         CVM = Quantity * Contract Size * (ItD Theoretical Price - EoD Price T-1)""", disabled=True)

    if 'trades' in st.session_state.keys():
        if st.session_state['calc_type'] == 'EoD':
            st.markdown("<p style='text-align: center;'font-size:18px;'>EXECUTED TRADES - RVM CALCULATION</p>", unsafe_allow_html=True)
            st.dataframe(st.session_state['trades'], use_container_width=True, hide_index=True)
            st.text_area("",
                         """ Realized Variation Margin (RVM) should be computed EoD by B/O system to MtM each trade on futures to EoD official settlement price.
                         RVM = Quantity * Contract Size * (EoD Price T - Execution Price)""", disabled=True)
            
        elif st.session_state['calc_type'] == 'ItD':
            st.markdown("<p style='text-align: center;'font-size:18px;'>EXECUTED TRADES - CVM CALCULATION</p>", unsafe_allow_html=True)
            st.dataframe(st.session_state['trades'], use_container_width=True, hide_index=True)
            st.text_area("",
                         """ Contingen Variation Margin (CVM) should be computed ItD by F/O system for each trade on futures as a component of Buying Power computation.
                         CVM = Quantity * Contract Size * (ItD Theoretical Price - Execution Price)""", 
                         disabled=True)
       
if 'day_trades' in st.session_state.keys():
    if st.session_state['calc_type'] == 'EoD':
        prev_day_subset = st.session_state['prev_day_pos_calc'][['CLIENT', 'SYMBOL', 'RVM', 'PENDING PREMIUM', 'QUANTITY']]
        st.session_state['open_pos'] = pd.concat([prev_day_subset, st.session_state['day_trades']], ignore_index=True)
        st.session_state['open_pos'] = st.session_state['open_pos'].pivot_table(index=['CLIENT', 'SYMBOL'], 
                                                                                      values=['QUANTITY', 'PENDING PREMIUM', 'RVM'], 
                                                                                      aggfunc='sum')
    elif st.session_state['calc_type'] == 'ItD':
        prev_day_subset = st.session_state['prev_day_pos_calc'][['CLIENT', 'SYMBOL', 'CVM', 'PENDING PREMIUM', 'QUANTITY']]
        st.session_state['open_pos'] = pd.concat([prev_day_subset, st.session_state['day_trades']], ignore_index=True)
        st.session_state['open_pos'] = st.session_state['open_pos'].pivot_table(index=['CLIENT', 'SYMBOL'], 
                                                                                      values=['QUANTITY', 'PENDING PREMIUM', 'CVM'], 
                                                                                      aggfunc='sum')
    st.session_state['open_pos'] =st.session_state['open_pos'].reset_index()
else:
    if st.session_state['calc_type'] == 'EoD':
        st.session_state['open_pos'] = st.session_state['prev_day_pos_calc'][['CLIENT', 'SYMBOL', 'RVM', 'PENDING PREMIUM', 'QUANTITY']]
    elif st.session_state['calc_type'] == 'ItD':
        st.session_state['open_pos'] = st.session_state['prev_day_pos_calc'][['CLIENT', 'SYMBOL', 'CVM', 'PENDING PREMIUM', 'QUANTITY']]
if 'open_pos' in st.session_state.keys():
    st.session_state['open_pos'] = st.session_state['open_pos'].set_index('SYMBOL')
    st.session_state['open_pos'] = st.session_state['open_pos'].join(st.session_state['fit_margins'][['MM']], how='left')
    st.session_state['open_pos'] = st.session_state['open_pos'].reset_index()
    st.session_state['open_pos'] = st.session_state['open_pos'].assign(**{'MAINTENANCE MARGIN': np.abs(np.where((st.session_state['open_pos']['SYMBOL']!='Future') & (st.session_state['open_pos']['QUANTITY']>0), 0.,
                                                                                                                 np.multiply(st.session_state['open_pos']['QUANTITY'], st.session_state['open_pos']['MM'])))})
    if st.session_state['calc_type'] == 'EoD':
        st.session_state['open_pos'] = st.session_state['open_pos'].assign(**{'TOTAL REQUIREMENT': st.session_state['open_pos']['MAINTENANCE MARGIN']})
    elif st.session_state['calc_type'] == 'ItD':   
        st.session_state['open_pos'] = st.session_state['open_pos'].assign(**{'TOTAL REQUIREMENT':np.abs(np.subtract(np.add(np.minimum(st.session_state['open_pos'].CVM, 0), st.session_state['open_pos']['PENDING PREMIUM']),
                                                                                                                     st.session_state['open_pos']['MAINTENANCE MARGIN']))})
        
    st.session_state['open_pos'] = st.session_state['open_pos'].drop(columns=['MM'])
##### OUTSTANDING ORDERS #####
if 'orders' in st.session_state.keys():
    st.markdown("<p style='text-align: center; font-size: 22px; font-weight: bold;'>OUTSTANDING ORDERS</p>", unsafe_allow_html=True)
    with st.expander('Click to display outstanding orders'):
        st.dataframe(st.session_state['orders'], use_container_width=True, hide_index=True)
##### CLIENT-BROKER & BROKER-CCP OPEN POSITION - BREAK DOWN #####
st.markdown("<p style='text-align: center; font-size: 22px; font-weight: bold;'>CLIENT-BROKER & BROKER-CCP OPEN POSITION - BREAK DOWN</p>", unsafe_allow_html=True)
with st.expander('Click to see break down'):
    with st.container():
        cli, ccp = st.columns([1,1])
        if st.session_state['open_pos'].shape[0]:
            if st.session_state['calc_type'] == 'EoD':
                cli.markdown("<p style='text-align: center;'font-size:18px;'>BROKER - CLIENT OPEN POSITION</p>", unsafe_allow_html=True)
                cli.dataframe(st.session_state['open_pos'][['CLIENT', 'SYMBOL', 'QUANTITY', 'RVM', 'PENDING PREMIUM', 'MAINTENANCE MARGIN', 'TOTAL REQUIREMENT']], use_container_width=True, hide_index=True)
                st.markdown("<p style='text-align: center;'font-size:18px;'>CM - CCP OPEN POSITION</p>", unsafe_allow_html=True)
                st.session_state['open_pos_ccp'] = st.session_state['open_pos'].pivot_table(index=['SYMBOL'],
                                                                                            values= ['QUANTITY', 'RVM', 'PENDING PREMIUM'],
                                                                                            aggfunc ='sum')
                st.session_state['open_pos_ccp'] = st.session_state['open_pos_ccp'].reset_index()
                st.session_state['open_pos_ccp'] =  st.session_state['open_pos_ccp'].set_index('SYMBOL').join(st.session_state['theor_prices'][['CONTRACT SIZE']], how='left')
                st.session_state['open_pos_ccp'] =  st.session_state['open_pos_ccp'].join(st.session_state['eod_prices'][['EOD PRICE T']], how='left')
                st.session_state['open_pos_ccp'] = st.session_state['open_pos_ccp'].reset_index()
                st.session_state['open_pos_ccp'] = st.session_state['open_pos_ccp'].assign(**{'CLEARING ACCOUNT': 'OSA',
                                                                                              'NLV': np.where( st.session_state['open_pos_ccp']['SYMBOL']!='Future',
                                                                                                              np.multiply(st.session_state['open_pos_ccp']['QUANTITY'],
                                                                                                                          np.multiply(st.session_state['open_pos_ccp']['EOD PRICE T'],
                                                                                                                                      st.session_state['open_pos_ccp']['CONTRACT SIZE'])), 0.)
                                                                                             })
                ccp.dataframe(st.session_state['open_pos_ccp'][['CLEARING ACCOUNT', 'SYMBOL', 'QUANTITY', 'EOD PRICE T', 'CONTRACT SIZE', 'RVM', 'NLV', 'PENDING PREMIUM']],
                              use_container_width=True, hide_index=True)
            elif st.session_state['calc_type'] == 'ItD':
                cli.markdown("<p style='text-align: center;'font-size:18px;'>CLIENTS OPEN POSITION</p>", unsafe_allow_html=True)
                cli.dataframe(st.session_state['open_pos'][['CLIENT', 'SYMBOL', 'QUANTITY', 'CVM', 'PENDING PREMIUM', 'MAINTENANCE MARGIN', 'TOTAL REQUIREMENT']], use_container_width=True, hide_index=True)
                ccp.markdown("<p style='text-align: center;'font-size:18px;'>CM - CCP OPEN POSITION</p>", unsafe_allow_html=True)
                st.session_state['open_pos_ccp'] = st.session_state['open_pos'].pivot_table(index=['SYMBOL'],
                                                                                            values= ['QUANTITY', 'CVM', 'PENDING PREMIUM'],
                                                                                            aggfunc ='sum')
                st.session_state['open_pos_ccp'] = st.session_state['open_pos_ccp'].reset_index()
                st.session_state['open_pos_ccp'] =  st.session_state['open_pos_ccp'].set_index('SYMBOL').join(st.session_state['theor_prices'], how='left')
                st.session_state['open_pos_ccp'] = st.session_state['open_pos_ccp'].reset_index()
                st.session_state['open_pos_ccp'] = st.session_state['open_pos_ccp'].assign(**{'CLEARING ACCOUNT': 'OSA',
                                                                                              'NLV': np.where( st.session_state['open_pos_ccp']['SYMBOL']!='Future',
                                                                                                              np.multiply(st.session_state['open_pos_ccp']['QUANTITY'],
                                                                                                                          np.multiply(st.session_state['open_pos_ccp']['THEORETICAL PRICE'],
                                                                                                                                      st.session_state['open_pos_ccp']['CONTRACT SIZE'])), 0.)
                                                                                             })
                ccp.dataframe(st.session_state['open_pos_ccp'][['CLEARING ACCOUNT', 'SYMBOL', 'QUANTITY', 'THEORETICAL PRICE', 'CONTRACT SIZE', 'CVM', 'NLV', 'PENDING PREMIUM']],
                              use_container_width=True, hide_index=True)

##### CLIENT-BROKER & BROKER-CCP OPEN POSITION - BREAK DOWN #####
st.markdown("<p style='text-align: center; font-size: 22px; font-weight: bold;'>CLIENT-BROKER & BROKER-CCP MARGIN REQUIREMENTS</p>", unsafe_allow_html=True)
with st.expander('Click to see break down'):
    with st.container():
        cli, ccp = st.columns([1,1])
        st.session_state['client_margin_req'] = st.session_state['sod_collateral']
        if st.session_state['open_pos'].shape[0]:
            cli.markdown("<p style='text-align: center;'font-size:18px;'>BROKER - CLIENT OPEN POSITION</p>", unsafe_allow_html=True)
            open_pos_req = st.session_state['open_pos'].pivot_table(index=['CLIENT'], values=['TOTAL REQUIREMENT'],
                                                                    aggfunc='sum')
            st.session_state['client_margin_req'] = st.session_state['client_margin_req'].join(open_pos_req, how='left')
            st.session_state['client_margin_req'] = st.session_state['client_margin_req'].rename(columns={'TOTAL REQUIREMENT': 'OPEN POSITION REQ'})
        else:
            st.session_state['client_margin_req'] = st.session_state['client_margin_req'].assign(**{'OPEN POSITION REQ': 0.})
        if 'orders' in st.session_state.keys():
            accepted_orders = st.session_state['orders'][st.session_state['orders'].STATUS=='ACCEPTED']
            if accepted_orders.shape[0]:
                accepted_orders = accepted_orders.pivot_table(index=['CLIENT'], values=['TOTAL REQUIREMENT'],
                                                              aggfunc='sum')
                st.session_state['client_margin_req'] = st.session_state['client_margin_req'].join(accepted_orders, how='left')
                st.session_state['client_margin_req'] = st.session_state['client_margin_req'].rename(columns={'TOTAL REQUIREMENT': 'OUTSTANDING ORDERS REQ'})
            else:
                st.session_state['client_margin_req'] = st.session_state['client_margin_req'].assign(**{'OUTSTANDING ORDERS REQ': 0.})
        else:
            st.session_state['client_margin_req'] = st.session_state['client_margin_req'].assign(**{'OUTSTANDING ORDERS REQ': 0.})
        cli.dataframe(st.session_state['client_margin_req'],use_container_width=True, hide_index=False)
            
##### CLIENTS BUYING POWER CALCULATION #####
st.session_state['client_bp'] = st.session_state['sod_collateral']
if st.session_state['open_pos'].shape[0]:
    open_pos_req = st.session_state['open_pos'].pivot_table(index=['CLIENT'], values=['TOTAL REQUIREMENT'],
                                                            aggfunc='sum')
    st.session_state['client_bp'] = st.session_state['client_bp'].join(open_pos_req, how='left')
    st.session_state['client_bp'] = st.session_state['client_bp'].rename(columns={'TOTAL REQUIREMENT': 'OPEN POSITION REQ'})
else:
    st.session_state['client_bp'] = st.session_state['client_bp'].assign(**{'OPEN POSITION REQ': 0.})
if 'orders' in st.session_state.keys():
    accepted_orders = st.session_state['orders'][st.session_state['orders'].STATUS=='ACCEPTED']
    if accepted_orders.shape[0]:
        accepted_orders = accepted_orders.pivot_table(index=['CLIENT'], values=['TOTAL REQUIREMENT'],
                                                      aggfunc='sum')
        st.session_state['client_bp'] = st.session_state['client_bp'].join(accepted_orders, how='left')
        st.session_state['client_bp'] = st.session_state['client_bp'].rename(columns={'TOTAL REQUIREMENT': 'OUTSTANDING ORDERS REQ'})
    else:
        st.session_state['client_bp'] = st.session_state['client_bp'].assign(**{'OUTSTANDING ORDERS REQ': 0.})
else:
    st.session_state['client_bp'] = st.session_state['client_bp'].assign(**{'OUTSTANDING ORDERS REQ': 0.})

st.session_state['client_bp'] = st.session_state['client_bp'].fillna(0)
st.session_state['client_bp'] = st.session_state['client_bp'].assign(**{'BUYING POWER': np.maximum(np.subtract(st.session_state['client_bp'].COLLATERAL, 
                                                                                                               np.add(st.session_state['client_bp']['OPEN POSITION REQ'],
                                                                                                                      st.session_state['client_bp']['OUTSTANDING ORDERS REQ'])), 0)})
st.markdown("<p style='text-align: center;'font-size:18px;'>CLIENT BUYING POWER - COMPUTED BY F/O & SENT TO B/O</p>", unsafe_allow_html=True)
st.dataframe(st.session_state['client_bp'],use_container_width=True)
