import streamlit as st
import pandas as pd
import altair as al

st.set_page_config(
    page_title='Case Study',
    layout = 'wide',
    initial_sidebar_state = 'expanded'
)


full_data = pd.read_csv('case_sample_data.csv')

#plt.rcParams['text.color'] = 'white'
#plt.style.use('dark_background')
#sb.set_theme()

with st.sidebar:

    st.title('Cohort Analysis')

    vendor_slct = st.selectbox('Select vendor cohort', ['Creative mobile technologies', 'Verifone'] )



col_dash = st.columns((1.5, 4.5, 2), gap='medium')

if vendor_slct == 'Creative mobile technologies':
    staged_data = full_data[full_data['vendor_id'] == 1]

else:
    staged_data = full_data[full_data['vendor_id'] == 2] 

staged_nozr = staged_data[staged_data['total_amount'] != 0]
staged_nozr = staged_nozr.sort_values(by='total_amount')
stage_nozr = staged_nozr.reset_index()

with col_dash[0]:
    st.markdown("### Metrics")
    st.metric(label='Average total fare for 2018', value=round(staged_nozr['total_amount'].mean(), 2))
    st.metric(label='Standard deviation of total fare for 2018', value=round(staged_nozr['total_amount'].std(), 2))

    st.markdown('### Top paying rate types on average')
    
    rates = stage_nozr[['total_amount', 'rate_code']].groupby('rate_code').mean()
    rates['total_amount'] = round(rates['total_amount'])
    rates = rates.sort_values(by='total_amount', ascending=False)
    rates = rates.rename(index={
        1: 'Standard rate',
        2: 'JFK',
        3: 'Newark',
        4: 'Nassau/Westchester',
        5: 'Negotiated fare',
        6: 'Group ride'
    })

    st.dataframe(rates,
                 column_config={
                     'total_amount': st.column_config.ProgressColumn(
                         'Average total amount',
                         format="%f",
                         min_value=0,
                         max_value=67
                     )
                 })



with col_dash[1]:

    st.markdown('### Cumulative graphs')

    staged_nozr['total_cumu_sum'] = staged_nozr['total_amount'].cumsum()
    staged_nozr['total_cumu_perc'] = round(100*staged_nozr['total_cumu_sum']/staged_nozr['total_amount'].sum(),2)
    
    plot1 = al.Chart(staged_nozr.sort_values(by='total_amount')).mark_line().encode(
        al.X('total_amount').title('Total Amount paid'),
        al.Y('total_cumu_perc').title('Cumulative Percentage')).properties(width=700)


    st.altair_chart(plot1)


    plot2 = al.Chart(staged_nozr).mark_bar().encode(
        al.X('total_amount').title('Total Amount Paid'),
        al.Y('count()').title('Frequency')).properties(width=700)

    st.altair_chart(plot2)


with col_dash[2]:
    code = '''
        SELECT *
        FROM `bigquery-public-data.new_york_taxi_trips.tlc_green_trips_2018` TABLESAMPLE SYSTEM (20 PERCENT)
        WHERE rand() < 0.005
    '''
    with st.expander('Further information', expanded=True):
        st.write('''
                 - Missing data has been removed from the sample prior to exploratory data analysis
                 - The dataset used is a sample of the 2018 NYC taxi database. SQL query command
                can be found below.
                 ''')
        st.code(code, language='sql')
        