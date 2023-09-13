import pandas as pd
import numpy as np
import warnings
from PyAstronomy.pyasl.asl import decimalYear
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from openpyxl import Workbook

warnings.simplefilter("ignore")


def long_date_to_decimal_date(x):
    array = []  # define an empty array in which the data will be stored
    for i in range(0, len(x)):  # initialize the for loop to run the length of our dataset (x)
        j = x[i]  # assign j: grab the i'th value from our dataset (x)
        decy = decimalYear(j)  # The heavy lifting is done via this Py-astronomy package
        decy = float(decy)  # change to a float - this may be required for appending data to the array
        array.append(decy)  # append it all together into a useful column of data
    return array  # return the new data


def cbl_chi2_goodnessoffit(data, error):
    # See example here: http://maxwell.ucsc.edu/~drip/133/ch4.pdf
    weighted_mean_numerator = sum(data / (error**2))
    weighted_mean_denom = sum(1/ (error**2))
    # EXPECTED = WEIGHTED MEAN
    expected = weighted_mean_numerator / weighted_mean_denom

    # VARIANCE
    var = np.var(data)

    step1 = (data - expected)**2
    step2 = step1 / var
    chi2 = sum(step2)
    chi2_red = (chi2 / (len(data)-1))
    chi2_red = round(chi2_red, 2)


    return chi2_red



"""
UPDATE:
May 2, 2023
Need to update the script since JT wants to show the entire history of data and the Chi2 value. Will add this in a new 
function with today's date. 

Date Not Recorded: See Github
This next iteration of the blank correction function was initiated after a conversation with Margaret, Cathy, and Jenny, 
as well as after TW3435 to resolve multiple issues with the initial script. 
1. We really need to deal directly with the pretreatment Process list, rather than assuming the same pretreatment 
for any given material, because for example, Wood treated with AAA and not cellulose is prone to manual error, which 
this entire excercise is meant to avoid. 
2. It would be helpful for Jenny Cathy and Margaret if the blanks that were used were deposited into the Blank Values 
Used Table, so it looks like it always did before. 
3. I need to slightly reformat the .txt file writing to suit what Jenny and Cathy look for, which is a more itemized list
of certain types of metadata (see binder)
"""


def blank_corr_050223(input_name, date_bound_input, num_list):
    # READ IN DATA EXCEL FILE OUTPUT FROM RLIMS
    #HY TW____.xlsx should now include the columns "Correction Category", "Size", and "MCC Correction Method"
    df = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\TW{}.xlsx'.format(input_name)).dropna(
        subset='Job::Sample Type From Sample Table').reset_index(drop=True)  # grab the file that has been exported from RLIMS, thanks to Valerie's new button.

    # READ IN HISTORICAL DATA FILE FROM RLIMS
    #HY TW____standards.xlsx should now include "Correction Category", "Size", and "MCC Correction Method"
    stds_hist = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\TW{}standards.xlsx'.format(input_name)).dropna(subset='Date Run').reset_index(drop=True)  # Read in the standards associated with it.
    stds_hist = stds_hist.dropna(subset='Ratio to standard').reset_index(drop=True)

    #HY Also reading in the Excel spreadsheet containing all the MCC correction categories in case more are added in
    # the future
    MCC_corr_methods = pd.read_excel("LOCATION OF EXCEL SHEET")
    MCC_corr_methods = MCC_corr_categories["MCC Correction Method"]


    """
    HY: Script shouldn't need this anymore since we are moving away from pre-treatments
    
        # READ IN R NUMBER REFERENCE
        refs = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\Pretreatment_reference2.xlsx', skiprows=6)  # Grab a small file I made that associates samples types to R numbers for correction
    
        # READ IN THIS WHEEL'S PRETREATMENTS
        pretreats = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\TW{}_PreTreatments.xlsx'.format(input_name))  # Grab a small file I made that associates samples types to R numbers for correction
    
        # MERGE PRETREATMENTS AND DATA:
        df = pd.merge(df, pretreats, on='Job')
        df.to_excel(r'I:\C14Data\C14_blank_corrections_dev\Refscheckwooo.xlsx', sheet_name='Sheet_name_1')
        
        
    """

    """
    This next block of code searches the standards extracted from the database, and find the MCC related to each of the items on my "Pretreatment_reference" excel sheet
    It will find an MCC for all types of standards, even if those are not used on the wheel. This MCC will be referred to later when we add it onto the samples.
    
    HY: This block of code is being changed to find the MCC from the correction category and MCC_corr_method
    
    """
    # CONVERT STANDARDS DATE FORMAT
    x = stds_hist['Date Run']
    stds_hist['Date Run'] = long_date_to_decimal_date(x)  # This line converts the dates to "Decimal Date" so that I can find only dates that are 0.5 years max before most recent date

    # SET DATE BOUNDARIES
    date_bound = max(stds_hist['Date Run']) - float(date_bound_input)

    # INDEX ONLY TO ABOVE THE STDS BOUNDARY, REMOVE QUALITY FLAGS, FIND LARGE SAMPLES, AND NO BACKGROUNDS
    stds_hist = stds_hist.loc[(stds_hist['Date Run'] > date_bound)]  # Index: find ONLY dates that are more recent than 1/2 year
    stds_hist = stds_hist.loc[(stds_hist['Quality Flag'] == '...')]  # Index: drop everything that contains a quality flag
    """
    HY: Need to change this line to accomodate small vs normal sized samples, not just normal size
    # stds_hist = stds_hist.loc[(stds_hist['wtgraph'] > 0.3)]  # Drop everything that is smaller than 0.3 mg.
    """

    stds_hist = stds_hist.loc[(stds_hist['Ratio to standard'] < 0.1)]  # Drop all blanks that are clearly WAY too high

"""
HY: need to change this so that it filters based on correction category

    df = df.loc[(df['Category In Calculation'] != 'Background Test')]  # Drop all background tests from the sample data
    df = df.loc[(df['Category In Calculation'] != 'Background Organic')]  # Drop all background organics from the sample data
    df = df.loc[(df['Category In Calculation'] != 'Background Inorganic')]  # Drop all background organics from the sample data
    df = df.loc[(df['Category In Calculation'] != 'Background Air')]  # Drop all background organics from the sample data
    
"""
    df = df.loc[(df['correction_category'] != 'Background')]


    # THIS BLOCK REMOVES ANY STANDARDS YOU DON"T WANT
    for i in range(len(num_list)):
        x = num_list[i]
        x = int(x)

        stds_hist = stds_hist.loc[(stds_hist['TP'] != x)]

    """
    This next block of code will search through all the R numbers in my pretreatment reference file.
    It will calculate the MCC and 1-sigms std of all acceptable standards and attach that MCC to that R number. Later,
    this number will be matched to unknowns with the same pretreatment process, and the MCC tacked onto the unknowns.
    
    HY: This whole section needs to be changed. Instead of looking at all R numbers in pre-treatment reference, it will
    be looking for all samples with "Primary OxI", the right MCC_corr_method, and the right size (maybe?)
    

    mcc_array = []
    mcc_1sigma_array = []
    stringarray = []
    stds_dataframe = pd.DataFrame({})

    # ITERATE THROUGH PRETREATMENT_REFERENCE2
    for i in range(0, len(refs)):
        # GRAB FIRST FOR OF PRETREATMENT REFERENCE LIST
        ref_row = refs.iloc[i]  # grab the first row of Pretreatment Reference list

        # GRAB THE R NUMBER AS A VARIABLE
        this_R = (ref_row['R number to correct from'])

        # SEARCH HISTORICAL STANDARDS FOR THIS R#
        current_standards = stds_hist.loc[(stds_hist['R_number'] == this_R)]

        # CALCULATE AVERAGE MCC (RTS)
        mcc = np.average(current_standards[
                             'Ratio to standard'])  # Calculate the average RTS of these specific standards in this sub-loop, and its standard deviation

        # CALCULATE STDDEV (RTS)
        # add ddof = 1 to match EXCEL STDEV formula
        mcc_1sigma = np.std(current_standards['Ratio to standard'], ddof=1)

        # APPEND THESE TO AN ARRAY
        mcc_array.append(
            mcc)  # tack these values onto an array, which we can add to the reference dataframe in a few lines
        mcc_1sigma_array.append(mcc_1sigma)

        # now I need to add the tilda's to tell which standards were used in each case
        strings = ""
        TPs = current_standards['TP'].reset_index(drop=True)
        for m in range(len(TPs)):
            q_o = TPs[m]
            strings = strings + str(int(q_o)) + str("\u007e")
        stringarray.append(strings)

    refs['MCC'] = mcc_array
    refs['MCC_1sigma'] = mcc_1sigma_array
    refs['Stds_used'] = stringarray
    refs = refs.drop_duplicates(subset='R number to correct from')
    refs = refs.rename(columns={"Pre-treatment Type": "Process Name"})
    refs.to_excel(f'I:\C14Data\C14_blank_corrections_dev\PythonOutput\TW{input_name}_Refscheck.xlsx')
    df.to_excel(f'I:\C14Data\C14_blank_corrections_dev\PythonOutput\TW{input_name}_testair.xlsx')
    results = pd.merge(df, refs, on='Process Name')
    results.to_excel(r'I:\C14Data\C14_blank_corrections_dev\results_test.xlsx')

    df_condensed = results[['TP', 'MCC', 'MCC_1sigma', 'Stds_used']]

    df_condensed = df_condensed.rename(columns={'MCC': 'rts_bl_av',
                                                'MCC_1sigma': 'rts_bl_av_error',
                                                'Standards used': 'TPs Blanks'})

    results.to_csv(r'I:\C14Data\C14_blank_corrections_dev\PythonOutput\TW{}_results.csv'.format(input_name))
    df_condensed.to_csv(r'I:/C14Data/C14_blank_corrections_dev/RLIMS_import/TW{}_reimport.csv'.format(input_name))

"""

    mcc_array = []
    mcc_1sigma_array = []
    stringarray = []
    stds_dataframe = pd.DataFrame({})

    for method in MCC_corr_methods:

        # SEARCH HISTORICAL STANDARDS FOR THIS METHOD
        current_standards = stds_hist.loc[(stds_hist['MCC Correction Method'] == method)]

        # CALCULATE AVERAGE MCC (RTS) AND STDDEV FOR THIS METHOD
        mcc = np.average(current_standards['Ratio to standard'])
        mcc_1sigma = np.std(current_standards['Ratio to standard'])

        # APPEND THESE TO AN ARRAY
        mcc_array.append(
            mcc)  # tack these values onto an array, which we can add to the reference dataframe in a few lines
        mcc_1sigma_array.append(mcc_1sigma)

        # Need to record TWs and TPs of standards used
        strings = ""
        TW_strings = ""

        for m in range(len(TPs)):
            q_o = TPs[m]
            tw = TWs[m]
            strings = strings + str(int(q_o)) + str("\u007e")
            TW_strings = TW_strings + str(int(tw)) + str("\u007e")
        stringarray.append(strings)
        TWarray.append(TW_strings)

    selected_refs = MCC_corr_methods
    selected_refs["MCC"] = mcc_array
    selected_refs['MCC_1sigma'] = mcc_1sigma_array
    selected_refs['Stds_used'] = stringarray
    selected_refs['TW_blank'] = TWarray
    selected_refs.to_excel(f'I:\C14Data\C14_blank_corrections_dev\PythonOutput\TW{input_name}_Refscheck.xlsx')

    # results = pd.merge(df, refs, on='Category in Calculation')
    # results.to_excel(r'I:\C14Data\C14_blank_corrections_dev\results_test.xlsx')

    df_condensed = df[['TP', 'MCC', 'MCC_1sigma', 'tp_stds_used', 'tw_stds_used']]

    df_condensed = df_condensed.rename(columns={'MCC': 'rts_bl_av',
                                                'MCC_1sigma': 'rts_bl_av_error',
                                                'TP_used': 'TP_blanks',
                                                'TW_used': 'TW_blanks'})


    df.to_csv(f'I:\C14Data\C14_blank_corrections_dev\PythonOutput\TW{input_name}_results.csv')
    df_condensed.to_csv(r'I:/C14Data/C14_blank_corrections_dev/RLIMS_import/TW{}_reimport.csv'.format(input_name))


    #HY Need Valerie to make some changes to the script regarding columns and column names
    # Also need Valerie to include TWs in RLIMS import script

# blank_corr_050223(3481,0.5,'')
# blank_corr_050223(3472,1,'')





















"""
The next function will create the secondaries plots that we're interested in...
The script that Valerie created exports data from RLIMS into the I: drive f"TW{}standards.xlsx" 
This data INCLUDES the wheel of interest
"""

def plot_seconds_thiswheel_new(input_name, minimum_tw):
    aa = []
    aaa = []
    a = []
    b = []
    c = []
    d = []
    e = []
    f = []
    g = []
    h = []
    z = []
    p = []
    k = []
    l = []


    # READ in the standards/the last 1 year of data that was exported from RLIMS
    stds_hist = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\TW{}standards.xlsx'.format(input_name)).dropna(subset='Date Run').reset_index(drop=True)
    stds_hist = stds_hist.dropna(subset='Ratio to standard').reset_index(drop=True)
    stds_hist = stds_hist.loc[(stds_hist['Quality Flag'] == '...')]  # Index: drop everything that contains a quality flag
    stds_hist = stds_hist[['Category Field', 'Ratio to standard','Ratio to standard error','delta13C_IRMS','delta13C_IRMS_Error','delta13C_AMS','delta13C_AMS_Error','R_number','TW','wtgraph','Description from Sample']]

    twmin = int(min(stds_hist['TW']))
    twmax = int(max(stds_hist['TW']))

    # FILTER TO FIND ONLY SECONDARY STANDARDS IN HISTORICAL DATA
    stds_hist = stds_hist.loc[stds_hist['Category Field'].isin(['RRL-UNSt-LG', 'RRL-UNSt-SM','RRL-UNSt-LG', 'RRL-UNSt-TY','RRL-CBOr-LG','RRL-GB-LG'])]
    print(minimum_tw)
    stds_hist = stds_hist.loc[stds_hist['TW'] > int(minimum_tw)]
    # CREATE A LIST OF UNIQUE R NUMBERS
    names = np.unique(stds_hist['R_number'])

    # GRAB SECONDARIES FROM THIS WHEEL ONLY
    this_wheel_list = stds_hist.loc[stds_hist['TW'] == int(input_name)].drop_duplicates(subset='R_number')
    this_wheel_list_r = this_wheel_list['R_number'].reset_index(drop=True)
    this_wheel_desc = this_wheel_list['Description from Sample'].reset_index(drop=True)

    # ITERATE THROUGH THE LIST OF R NUMBERS FROM THIS WHEEL
    for i in range(0, len(this_wheel_list_r)):
        descrip = this_wheel_desc[i]
        """
        DEAL W 14C FIRST
        """
        # INDEX HISTORICAL DATABASE TO FIND ONLY R NUMBERS FROM THIS ITERATION
        this_one = stds_hist.loc[stds_hist['R_number'] == this_wheel_list_r[i]]

        # BREAK INTO LARGE AND SMALL
        small = this_one.loc[this_one['wtgraph'] <= 0.3]
        large = this_one.loc[this_one['wtgraph'] >= 0.3]

        # CHI2s
        if len(small) > 2:
            res_small = cbl_chi2_goodnessoffit(small['Ratio to standard'], small['Ratio to standard error'])
        else:
            res_small = ''

        if len(large) > 2:
            res_large = cbl_chi2_goodnessoffit(large['Ratio to standard'], large['Ratio to standard error'])
        else:
            res_large = ''

        small_mean_rts = np.nanmean(small['Ratio to standard'])
        small_std_rts = np.nanstd(small['Ratio to standard'])
        large_mean_rts = np.nanmean(large['Ratio to standard'])
        large_std_rts = np.nanstd(large['Ratio to standard'])

        aa.append(this_wheel_list_r[i])
        aaa.append(descrip)
        a.append(small_mean_rts)
        b.append(small_std_rts)
        c.append(large_mean_rts)
        d.append(large_std_rts)


        # make the figure
        fig1 = plt.figure(constrained_layout=True, figsize=(10, 8))
        fig1.suptitle(f'{descrip}_{this_wheel_list_r[i]}: TW{minimum_tw} to TW{twmax}')
        spec2 = gridspec.GridSpec(ncols=2, nrows=2, figure=fig1)
        f1_ax1 = fig1.add_subplot(spec2[0, 0])
        f1_ax2 = fig1.add_subplot(spec2[0, 1])
        f1_ax3 = fig1.add_subplot(spec2[1, 0])
        f1_ax4 = fig1.add_subplot(spec2[1, 1])

        f1_ax1.set_ylabel("14C: Ratio to OX1")
        f1_ax3.set_ylabel("delta13C_In_Calculation")

        f1_ax3.set_xlabel("Wheel #")
        f1_ax4.set_xlabel("Wheel #")



        # plot the data
        # plot large and small 14C data
        f1_ax1.errorbar(large['TW'], large['Ratio to standard'], large['Ratio to standard error'], fmt='o', capsize=3, color='black')
        f1_ax2.errorbar(small['TW'], small['Ratio to standard'], small['Ratio to standard error'], fmt='o', capsize=3, color='black')

        f1_ax1.axhline(large_mean_rts, color='black')
        f1_ax2.axhline(small_mean_rts, color='black')

        f1_ax1.set_title(f"Large (>.3 mg); Chi2 = {res_large}")
        f1_ax2.set_title(f"Small (<.3 mg); Chi2 = {res_small}")

        """
        NOW 13C IRMS: Restart from the first line of the loop above
        """
        # INDEX HISTORICAL DATABASE TO FIND ONLY R NUMBERS FROM THIS ITERATION
        this_one_13C_IRMS = stds_hist.loc[stds_hist['R_number'] == this_wheel_list_r[i]]

        # DROP ANY ROW THAT IS MISSING 13C DATA
        this_one_13C_IRMS = this_one_13C_IRMS.dropna()

        # grab the description for the plot title.
        # descrip = this_one_13C_IRMS['Description from Sample'].reset_index(drop=True)
        # descrip = descrip[0]

        # BREAK INTO LARGE AND SMALL
        small = this_one_13C_IRMS.loc[this_one_13C_IRMS['wtgraph'] <= 0.3]
        large = this_one_13C_IRMS.loc[this_one_13C_IRMS['wtgraph'] >= 0.3]

        # IF THERES MORE THAN 1, PLOT THE LARGE 13Cs
        lar_length = len(large)
        if lar_length > 2:

            large_res_IRMS = cbl_chi2_goodnessoffit(large['delta13C_IRMS'], large['delta13C_IRMS_Error'])
            large_mean_13_IRMS = np.nanmean(large['delta13C_IRMS'])
            large_std_13_IRMS = np.nanstd(large['delta13C_IRMS'])
            g.append(large_mean_13_IRMS)
            h.append(large_std_13_IRMS)

            # plot large and small 13C IRMS data
            f1_ax3.errorbar(large['TW'], large['delta13C_IRMS'], large['delta13C_IRMS_Error'], color='blue', label='IRMS', marker='D')
            f1_ax3.axhline(large_mean_13_IRMS, color='blue')


        else:
            print('No 13C values to record: Please manually check database')
            large_res_IRMS = ''

        # IF THERES MORE THAN 1, PLOT THE SMALL 13C's
        sm_length = len(small)
        if sm_length > 2:

            small_res_IRMS = cbl_chi2_goodnessoffit(small['delta13C_IRMS'], small['delta13C_IRMS_Error'])
            small_mean_13_IRMS = np.nanmean(small['delta13C_IRMS'])
            small_std_13_IRMS = np.nanstd(small['delta13C_IRMS'])
            e.append(small_mean_13_IRMS)
            f.append(small_std_13_IRMS)

            # plot large and small 13C IRMS data
            f1_ax4.errorbar(small['TW'], small['delta13C_IRMS'], small['delta13C_IRMS_Error'], color='blue', marker='D')
            f1_ax4.axhline(small_mean_13_IRMS, color='blue')


        else:
            print('No 13C values to record: Please manually check database')
            small_res_IRMS = ''

        """
        NOW 13C AMS
        """
        # INDEX HISTORICAL DATABASE TO FIND ONLY R NUMBERS FROM THIS ITERATION
        this_one_13C_AMS = stds_hist.loc[stds_hist['R_number'] == this_wheel_list_r[i]]

        # DROP ANY ROW THAT IS MISSING 13C DATA
        this_one_13C_AMS = this_one_13C_AMS.dropna()

        # grab the description for the plot title.
        # descrip = this_one_13C_AMS['Description from Sample'].reset_index(drop=True)
        # descrip = descrip[0]

        # BREAK INTO LARGE AND SMALL
        small = this_one_13C_AMS.loc[this_one_13C_AMS['wtgraph'] <= 0.3]
        large = this_one_13C_AMS.loc[this_one_13C_AMS['wtgraph'] >= 0.3]


        lar_length = len(large)

        if lar_length > 2:

            large_res_AMS = cbl_chi2_goodnessoffit(large['delta13C_AMS'], large['delta13C_AMS_Error'])
            large_mean_13_AMS = np.nanmean(large['delta13C_AMS'])
            large_std_13_AMS = np.nanstd(large['delta13C_AMS'])
            k.append(large_mean_13_AMS)
            l.append(large_std_13_AMS)

            # plot large and small 13C AMS Data
            f1_ax3.scatter(large['TW'], large['delta13C_AMS'], color='black', label='AMS')
            f1_ax3.axhline(large_mean_13_AMS, color='black')
            f1_ax3.legend()

        else:
            print('No 13C values to record: Please manually check database')
            large_res_AMS = ''

        sm_length = len(small)

        if sm_length > 2:
            small_res_AMS = cbl_chi2_goodnessoffit(small['delta13C_AMS'], small['delta13C_AMS_Error'])

            small_mean_13_AMS = np.nanmean(small['delta13C_AMS'])
            small_std_13_AMS = np.nanstd(small['delta13C_AMS'])

            z.append(small_mean_13_AMS)
            p.append(small_std_13_AMS)

            # plot large and small 13C AMS Data
            f1_ax4.errorbar(small['TW'], small['delta13C_AMS'], small['delta13C_AMS_Error'], color='black')
            f1_ax4.axhline(small_mean_13_AMS, color='black')
            f1_ax3.legend()

        else:
            print('No 13C values to record: Please manually check database')
            small_res_AMS = ''

        f1_ax3.set_title(f"Chi2: AMS = {large_res_AMS}; IRMS = {small_res_IRMS}")
        f1_ax4.set_title(f"Chi2: AMS = {small_res_AMS}; IRMS = {small_res_IRMS}")
        newname = this_wheel_list_r[i].replace("/", "_")
        newdesk = descrip.replace(":", "")
        plt.savefig(f'I:/C14Data/C14_blank_corrections_dev/Quality_Assurance/Plots/TW{input_name}+{newdesk}.png')


# plot_seconds_thiswheel_new(3462, 3400)

    #             # grab the description for the plot title.
    #             descrip = this_one['Description from Sample'].reset_index(drop=True)
    #             descrip = descrip[0]
    #
    #             # filter by size.
    #             smalls = this_one.loc[this_one['wtgraph'] <= 0.3]
    #             x = int(len(smalls))
    #
    #             large = this_one.loc[this_one['wtgraph'] >= 0.3]
    #
    #             small_mean_rts = np.nanmean(smalls['Ratio to standard'])
    #             small_std_rts = np.nanstd(smalls['Ratio to standard'])
    #             large_mean_rts = np.nanmean(large['Ratio to standard'])
    #             large_std_rts = np.nanstd(large['Ratio to standard'])
    # print(this_wheel_list)


    # # FIND THE MIN AND MAX TW NUMBER
    # twmin = int(min(stds_hist['TW']))
    # twmax = int(max(stds_hist['TW']))



# plot_seconds_thiswheel_new(3465)


    # # GRAB SECONDARIES FROM THIS WHEEL ONLY
    # this_wheel_list = stds_hist.loc[stds_hist['TW'] == int(input_name)]
    # this_wheel_list = this_wheel_list['R_number'].reset_index(drop=True)
    #
    # # ITERATE THROUGH THE LIST OF R NUMBERS FROM THIS WHEEL
    # for i in range(0, len(this_wheel_list)):
    #     for j in range(0, len(names)):
    #         if this_wheel_list[i] == names[j]:
    #
    #             # grab the first standard type.
    #             this_one = stds_hist.loc[stds_hist['R_number'] == this_wheel_list[i]]
    #
    #             # grab the description for the plot title.
    #             descrip = this_one['Description from Sample'].reset_index(drop=True)
    #             descrip = descrip[0]
    #
    #             # filter by size.
    #             smalls = this_one.loc[this_one['wtgraph'] <= 0.3]
    #             x = int(len(smalls))
    #
    #             large = this_one.loc[this_one['wtgraph'] >= 0.3]
    #
    #             small_mean_rts = np.nanmean(smalls['Ratio to standard'])
    #             small_std_rts = np.nanstd(smalls['Ratio to standard'])
    #             large_mean_rts = np.nanmean(large['Ratio to standard'])
    #             large_std_rts = np.nanstd(large['Ratio to standard'])
    #
    #


#
# def plot_seconds_thiswheel_old(input_name):
#     aa = []
#     aaa = []
#     a = []
#     b = []
#     c = []
#     d = []
#     e = []
#     f = []
#     g = []
#     h = []
#     z = []
#     p = []
#     k = []
#     l = []
#
#     # READ in the standards/the last 1 year of data that was exported from RLIMS
#     stds_hist = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\TW{}standards.xlsx'.format(input_name)).dropna(subset='Date Run').reset_index(drop=True)
#     stds_hist = stds_hist.dropna(subset='Ratio to standard').reset_index(drop=True)
#     stds_hist = stds_hist.loc[(stds_hist['Quality Flag'] == '...')]  # Index: drop everything that contains a quality flag
#     # find only categories that are our Large and Small standards.
#     stds_hist = stds_hist.loc[stds_hist['Category Field'].isin(['RRL-UNSt-LG', 'RRL-UNSt-SM'])]
#     names = np.unique(stds_hist['R_number'])
#     twmin = int(min(stds_hist['TW']))
#     twmax = int(max(stds_hist['TW']))
#
#     # have a look - what the secondaries in this wheel only?
#     this_wheel_list = stds_hist.loc[stds_hist['TW'] == int(input_name)]
#     this_wheel_list = this_wheel_list['R_number'].reset_index(drop=True)
#
#     # focus on ONLY the stds that are in the wheel of interest
#     for i in range(0, len(this_wheel_list)):
#         for j in range(0, len(names)):
#             if this_wheel_list[i] == names[j]:
#
#                 # grab the first standard type.
#                 this_one = stds_hist.loc[stds_hist['R_number'] == this_wheel_list[i]]
#
#                 # grab the description for the plot title.
#                 descrip = this_one['Description from Sample'].reset_index(drop=True)
#                 descrip = descrip[0]
#
#                 # filter by size.
#                 smalls = this_one.loc[this_one['wtgraph'] <= 0.3]
#                 x = int(len(smalls))
#
#                 large = this_one.loc[this_one['wtgraph'] >= 0.3]
#
#                 small_mean_rts = np.nanmean(smalls['Ratio to standard'])
#                 small_std_rts = np.nanstd(smalls['Ratio to standard'])
#                 large_mean_rts = np.nanmean(large['Ratio to standard'])
#                 large_std_rts = np.nanstd(large['Ratio to standard'])
#
#                 try:
#                     # get rid of any missing data for the 13C values.
#                     smalls13C_IRMS = smalls.dropna(subset='delta13C_IRMS').reset_index(drop=True)
#                     large13C_IRMS = large.dropna(subset='delta13C_IRMS').reset_index(drop=True)
#                     smalls13C_AMS = smalls.dropna(subset='delta13C_AMS').reset_index(drop=True)
#                     large13C_AMS = large.dropna(subset='delta13C_AMS').reset_index(drop=True)
#
#                     small_mean_13_IRMS = np.nanmean(smalls['delta13C_IRMS'])
#                     small_std_13_IRMS = np.nanstd(smalls['delta13C_IRMS'])
#                     large_mean_13_IRMS = np.nanmean(large['delta13C_IRMS'])
#                     large_std_13_IRMS = np.nanstd(large['delta13C_IRMS'])
#
#                     small_mean_13_AMS = np.nanmean(smalls['delta13C_AMS'])
#                     small_std_13_AMS = np.nanstd(smalls['delta13C_AMS'])
#                     large_mean_13_AMS = np.nanmean(large['delta13C_AMS'])
#                     large_std_13_AMS = np.nanstd(large['delta13C_AMS'])
#
#                     aa.append(this_wheel_list[i])
#                     aaa.append(descrip)
#                     a.append(small_mean_rts)
#                     b.append(small_std_rts)
#                     c.append(large_mean_rts)
#                     d.append(large_std_rts)
#
#                     e.append(small_mean_13_AMS)
#                     f.append(small_std_13_AMS)
#                     g.append(large_mean_13_AMS)
#                     h.append(large_std_13_AMS)
#
#                     z.append(small_mean_13_IRMS)
#                     p.append(small_std_13_IRMS)
#                     k.append(large_mean_13_IRMS)
#                     l.append(large_std_13_IRMS)
#                 except ZeroDivisionError:
#                     dummyvar = 0
#
#                 # make the figure
#                 fig1 = plt.figure(constrained_layout=True, figsize=(10, 8))
#                 fig1.suptitle(f'{descrip}_{this_wheel_list[i]}: TW{twmin} to TW{twmax}')
#                 spec2 = gridspec.GridSpec(ncols=2, nrows=2, figure=fig1)
#                 f1_ax1 = fig1.add_subplot(spec2[0, 0])
#                 f1_ax2 = fig1.add_subplot(spec2[0, 1])
#                 f1_ax3 = fig1.add_subplot(spec2[1, 0])
#                 f1_ax4 = fig1.add_subplot(spec2[1, 1])
#
#                 f1_ax1.set_ylabel("14C: Ratio to OX1")
#                 f1_ax3.set_ylabel("delta13C_In_Calculation")
#
#                 f1_ax3.set_xlabel("Wheel #")
#                 f1_ax4.set_xlabel("Wheel #")
#
#                 f1_ax1.set_title("Large (>.3 mg)")
#                 f1_ax2.set_title("Small (<.3 mg)")
#
#                 # plot the data
#                 # plot large and small 14C data
#                 f1_ax1.errorbar(large['TW'], large['Ratio to standard'], large['Ratio to standard error'], fmt='o',
#                                 capsize=3, color='black')
#                 f1_ax2.errorbar(smalls['TW'], smalls['Ratio to standard'], smalls['Ratio to standard error'], fmt='o',
#                                 capsize=3, color='black')
#                 f1_ax1.axhline(large_mean_rts, color='black')
#                 f1_ax2.axhline(small_mean_rts, color='black')
#
#                 # plot large and small 13C IRMS data
#                 f1_ax3.scatter(large13C_IRMS['TW'], large13C_IRMS['delta13C_IRMS'], color='blue', label='IRMS',
#                                marker='D')
#                 f1_ax4.scatter(smalls13C_IRMS['TW'], smalls13C_IRMS['delta13C_IRMS'], color='blue', marker='D')
#                 f1_ax3.axhline(large_mean_13_IRMS, color='blue')
#                 f1_ax4.axhline(small_mean_13_IRMS, color='blue')
#                 # f1_ax3.legend()
#
#                 # plot large and small 13C AMS Data
#                 f1_ax3.scatter(large13C_AMS['TW'], large13C_AMS['delta13C_AMS'], color='black', label='AMS')
#                 f1_ax4.scatter(smalls13C_AMS['TW'], smalls13C_AMS['delta13C_AMS'], color='black')
#                 f1_ax3.axhline(large_mean_13_AMS, color='black')
#                 f1_ax4.axhline(small_mean_13_AMS, color='black')
#                 f1_ax3.legend()
#
#                 # add the 1-sigma
#                 try:
#                     f1_ax1.fill_between(large['TW'], (large_mean_rts + large_std_rts), (large_mean_rts - large_std_rts),
#                                         alpha=0.3, color='brown')
#                     f1_ax3.fill_between(large13C_IRMS['TW'], (large_mean_13_IRMS + large_std_13_IRMS),
#                                         (large_mean_13_IRMS - large_std_13_IRMS), alpha=0.3, color='blue')
#                     f1_ax3.fill_between(large13C_AMS['TW'], (large_mean_13_AMS + large_std_13_AMS),
#                                         (large_mean_13_IRMS - large_std_13_AMS), alpha=0.3, color='brown')
#                     f1_ax2.fill_between(smalls['TW'], (small_mean_rts + large_std_rts),
#                                         (small_mean_rts - large_std_rts), alpha=0.3, color='brown')
#                     f1_ax4.fill_between(smalls13C_IRMS['TW'], (small_mean_13_IRMS + small_std_13_IRMS),
#                                         (small_mean_13_IRMS - small_std_13_IRMS), alpha=0.3, color='blue')
#                     f1_ax4.fill_between(smalls13C_AMS['TW'], (small_mean_13_AMS + small_std_13_AMS),
#                                         (small_mean_13_IRMS - small_std_13_AMS), alpha=0.3, color='brown')
#                 except IndexError:
#                     dummyvar = 0
#
#                 newname = this_wheel_list[i].replace("/", "_")
#                 newdesk = descrip.replace(":", "")
#                 plt.savefig(
#                     f'I:/C14Data/C14_blank_corrections_dev/Quality_Assurance/Plots/TW{input_name}+{newdesk}+{newname}.png')
#     #
#     # save these data to a table
#     results = pd.DataFrame({"R_number": aa,
#                             "Description": aaa,
#                             "Large RTS Mean": c,
#                             "Large RTS std": d,
#                             "Large AMS 13C Mean": g,
#                             "Large AMS 13C std": h,
#                             "Large IRMS 13C Mean": k,
#                             "Large IRMS 13C std": l,
#
#                             "Small RTS Mean": a,
#                             "Small RTS std": b,
#                             "Smalls AMS 13C Mean": e,
#                             "Smalls AMS 13C std": f,
#                             "Smalls IRMS 13C Mean": z,
#                             "Smalls IRMS 13C std": p,
#                             })
#     results.to_excel(
#         f'I:/C14Data/C14_blank_corrections_dev/Quality_Assurance/Data/TW{input_name}_ONLY_standards_summary.xlsx')
#
#
#
#



#
# def blank_corr_022323(input_name, date_bound_input, num_list):
#     # ask the user to input the TW# of the current wheel.
#     # input_name = input("What is the TW of this wheel?")
#
#     # read in all the excel files I'll need and drop empty lines
#     df = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\TW{}.xlsx'.format(input_name)).dropna(
#         subset='Job::Sample Type From Sample Table').reset_index(
#         drop=True)  # grab the file that has been exported from RLIMS, thanks to Valerie's new button.
#     stds_hist = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\TW{}standards.xlsx'.format(input_name)).dropna(
#         subset='Date Run').reset_index(drop=True)  # Read in the standards associated with it.
#     refs = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\Pretreatment_reference.xlsx').dropna(
#         subset='R number to correct from')  # Grab a small file I made that associates samples types to R numbers for correction
#
#     sample_type_list = np.unique(df['Job::Sample Type From Sample Table'])  # saving this list to write to a file later
#
#     """
#     Lets write a summary template file which will be pasted into RLIMS
#     """
#     f = open(r'I:/C14Data/C14_blank_corrections_dev/PythonOutput/TW{}_summary.txt'.format(input_name), 'w')
#     """
#     Lets check how the OX-1's performed.
#     """
#     primary_standards = df.loc[
#         df['Job::Sample Type From Sample Table'] == 'Oxalic']  # grab all the ROWS where the AMS category is XCAMS
#     prim_std_average = np.average(primary_standards['Ratio to standard'])
#     prim_std_1sigma = np.std(primary_standards['Ratio to standard'])
#     prim_std_13average = np.average(primary_standards['delta13C_AMS'])
#     prim_std_13_1sigma = np.std(primary_standards['delta13C_AMS'])
#     rounding_decimal = 3  # Note: if the rounding decimal is around 3, but the result comes out to 1.0, this is because it has rounded up from 0.99999 or so, for example.
#
#     # Do any of the OX-1's deviate from their IRMS number?
#     # Compare 13C AMS to 13C IRMS
#     arr1 = []  # initialize a few empty arrays for later use
#     arr2 = []
#     C13_threshold = 5
#     for i in range(0, len(primary_standards)):
#         row = primary_standards.iloc[i]  # access the first row
#         ams = row['delta13C_AMS']
#         ams_err = row['delta13C_AMS_Error']
#         irms = row['delta13C_IRMS']
#         irms_error = row['delta13C_IRMS_Error']
#         delta = abs(ams - irms)
#
#         if delta >= C13_threshold:
#             arr1.append(delta)
#             arr2.append(row['TP'])
#
#     result = pd.DataFrame({"TP": arr2, "Absolute value, (AMS - IRMS 13C)": arr1})
#
#     print(("The types of Oxalic I's in this wheel are {} ".format(
#         np.unique(primary_standards['Description from Sample']))), file=f)
#     print(("The average RTS of the Primary Standards in this wheel is {} \u00B1 {}".format(
#         round(prim_std_average, rounding_decimal), round(prim_std_1sigma, rounding_decimal))), file=f)
#     print(("The average OX-1 13C values in this wheel is {} \u00B1 {}".format(
#         round(prim_std_13average, rounding_decimal), round(prim_std_13_1sigma, rounding_decimal))), file=f)
#     print()
#
#     if len(result) > 0:
#         print((
#             "The following standards are outside the selected range of {}\u2030 difference between IRMS and AMS 13C".format(
#                 C13_threshold)), file=f)
#         print((result), file=f)
#     else:
#         print(("No OX-1's 13C values deviate from IRMS 13C values more than {}\u2030 ".format(C13_threshold)), file=f)
#         print()
#     # </editor-fold>
#
#     # <editor-fold desc="Break up wheel based on different types of graphite">
#
#     """
#     This next block of code searches the standards extracted from the database, and find the MCC related to each of the items on my "Pretreatment_reference" excel sheet
#     It will find an MCC for all types of standards, even if those are not used on the wheel. This MCC will be referred to later when we add it onto the samples.
#
#     """
#     x = stds_hist['Date Run']
#     stds_hist['Date Run'] = long_date_to_decimal_date(
#         x)  # This line converts the dates to "Decimal Date" so that I can find only dates that are 0.5 years max before most recent date
#     # date_bound_input = input("How far back do you want the standards to go? Type 0.5 for 1/2 year, and 1 for 1 year")
#     date_bound = max(stds_hist['Date Run']) - float(date_bound_input)
#     stds_hist = stds_hist.loc[
#         (stds_hist['Date Run'] > date_bound)]  # Index: find ONLY dates that are more recent than 1/2 year
#
#     stds_hist = stds_hist.loc[
#         (stds_hist['Quality Flag'] == '...')]  # Index: drop everything that contains a quality flag
#     stds_hist = stds_hist.loc[(stds_hist['wtgraph'] > 0.3)]  # Drop everything that is smaller than 0.3 mg.
#     stds_hist = stds_hist.loc[(stds_hist['Ratio to standard'] < 0.1)]  # Drop all blanks that are clearly WAY too high
#     stds_hist = stds_hist.loc[(stds_hist['Category In Calculation'] != 'Background Test')]  # Drop all background tests
#     # decide if there are any standards we want to avoid
#
#     # #yn = input("Are there any standards you specifically want to exclude? (y/n)")
#     # if yn == 'y':
#     #     n = int(input("Enter the number of standards you will exclude: "))
#     #     print("\n")
#     #     num_list = list(int(num) for num in input("Enter the TP numbers, each separated by space ").strip().split())[:n]
#     #     print("User list: ", num_list)
#     print(f" I want to exclude {num_list}")
#     print(len(stds_hist))
#     for i in range(len(num_list)):
#         x = num_list[i]
#         x = int(x)
#
#         stds_hist = stds_hist.loc[(stds_hist['TP'] != x)]
#     print(len(stds_hist))
#     """
#     This next block of code will search through all the R numbers in my pretreatment reference file.
#     It will calculate the MCC and 1-sigms std of all acceptable standards and attach that MCC to that R number. Later,
#     this number will be matched to unknowns with the same pretreatment process, and the MCC tacked onto the unknowns.
#     """
#
#     mcc_array = []
#     mcc_1sigma_array = []
#     stringarray = []
#     stds_dataframe = pd.DataFrame({})
#     for i in range(0, len(refs[
#                               'Sample Type From Sample Table'])):  # run through the list of "Sample Type from Sample Table" in the Pretreatement Reference list
#         ref_row = refs.iloc[i]  # grab the first row of Pretreatment Reference list
#         this_R = (
#             ref_row['R number to correct from'])  # find the R number associated with that blank correction reference
#         current_standards = stds_hist.loc[(stds_hist[
#                                                'R_number'] == this_R)]  # find all standards that match the current R number I'm interetsed in from the reference table
#         stds_dataframe = pd.concat([stds_dataframe, current_standards])
#         mcc = np.average(current_standards[
#                              'Ratio to standard'])  # Calculate the average RTS of these specific standards in this sub-loop, and its standard deviation
#         mcc_1sigma = np.std(current_standards['Ratio to standard'])
#         mcc_array.append(
#             mcc)  # tack these values onto an array, which we can add to the reference dataframe in a few lines
#         mcc_1sigma_array.append(mcc_1sigma)
#
#         # now I need to add the tilda's to tell which standards were used in each case
#         strings = ""
#         TPs = current_standards['TP'].reset_index(drop=True)
#         for m in range(len(TPs)):
#             q_o = TPs[m]
#             strings = strings + str(int(q_o)) + str("\u007e")
#         stringarray.append(strings)
#
#     refs['MCC'] = mcc_array
#     refs['MCC_1sigma'] = mcc_1sigma_array
#     refs['Stds_used'] = stringarray
#     # refs.to_excel(r'C:/Users/clewis/IdeaProjects/GNS/Blank_Corrections/Output_results/Refscheck.xlsx'.format(input_name), sheet_name='Sheet_name_1')
#     """
#     This set of nested loops will iterate through each row of wheel's data, and find the samples type. Then, it will iterate
#     through the pretreatment reference list. When it finds a sample type that matches, it takes the calculated MCC and associated
#     data and tacks it onto that wheel's data for re-uploading into RLIMS. If no matches are found (OX-1's, sucrose, kapuni), it
#     inserts -999.
#     """
#
#     mcc_arr2 = []
#     mcc_1sigma2 = []
#     r_arr = []
#     pretreatment = []
#     stds_used = []
#     not_found = []
#
#     df = df.loc[(df['Description from Sample'] != 'Kapuni CO2 cylinder')]  # remove the Kapuni and the sucrose
#     df = df.loc[(df['Description from Sample'] != 'ANU Sucrose - IAEA C6')]
#     df = df.loc[(df['Category In Calculation'] != 'Background Test')]
#     df = df.loc[(df['Category In Calculation'] != 'Background Inorganic')]
#     df = df.loc[(df['Category In Calculation'] != 'Background Organic')]
#     df = df.loc[(df['Job::Sample Type From Sample Table'] != 'other organic material')]
#
#     for k in range(0, len(df)):
#         data_row = df.iloc[k]  # grab the first row of data
#         sample_type = str(data_row['Job::Sample Type From Sample Table'])
#         flag = 0
#         for q in range(0, len(refs)):
#             ref_row = refs.iloc[q]  # run through the references to find the right MCC
#             standard_type = str(ref_row['Sample Type From Sample Table'])
#             # print(standard_type)
#
#             if sample_type == standard_type:  # when the sample type matches the standard type,
#                 # print('I found a match: {}'.format(sample_type))
#                 mcc_arr2.append(ref_row['MCC'])
#                 mcc_1sigma2.append(ref_row['MCC_1sigma'])
#                 r_arr.append(ref_row['R number to correct from'])
#                 pretreatment.append(ref_row['Pre-treatment Type'])
#                 stds_used.append(ref_row['Stds_used'])
#                 flag = 1  # tells the computer if a match was found
#
#         if flag == 0:  # if a match was not found, check if it was used for primary standards, or tuning, then fill with -999
#             if sample_type == 'Oxalic':
#                 mcc_arr2.append(-999)
#                 mcc_1sigma2.append(-999)
#                 r_arr.append(-999)
#                 pretreatment.append(-999)
#                 stds_used.append(-999)
#             else:
#                 not_found.append(sample_type)
#                 mcc_arr2.append(-999)
#                 mcc_1sigma2.append(-999)
#                 r_arr.append(-999)
#                 pretreatment.append(-999)
#                 stds_used.append(-999)
#
#     if len(not_found) > 0:
#         print((f"Sample with type {not_found} could not be matched with a corresponding R number for correction."
#                f"Please add these sample types with corresponding R number in Pretreatment_reference.xlsx and re-run the script"),
#               file=f)
#
#     df['MCC'] = mcc_arr2
#     df['MCC_1sigma'] = mcc_1sigma2
#     df['R numbers used for blank correction'] = r_arr
#     df['Pretreatment type'] = pretreatment
#     df['Standards used'] = stds_used
#
#     stds_dataframe = stds_dataframe.drop_duplicates(subset='TP', keep='first')
#
#     df_condensed = df[['TP', 'MCC', 'MCC_1sigma', 'Standards used']]
#     df_condensed = df_condensed.rename(columns={'MCC': 'rts_bl_av',
#                                                 'MCC_1sigma': 'rts_bl_av_error',
#                                                 'Standards used': 'TPs Blanks'})
#
#     # refs.to_csv(r'I:/C14Data/C14_blank_corrections_dev/MCC_output/TW{}_MCC.csv'.format(input_name))
#     # stds_dataframe.to_csv(r'I:/C14Data/C14_blank_corrections_dev/MCC_details/TW{}_MCCdetails.csv'.format(input_name))
#     # df.to_csv(r'I:/C14Data/C14_blank_corrections_dev/Output_Results/TW{}_results.csv'.format(input_name))
#     df_condensed.to_csv(r'I:/C14Data/C14_blank_corrections_dev/RLIMS_import/TW{}_reimport.csv'.format(input_name))
#
#     with pd.ExcelWriter(
#             r'I:/C14Data/C14_blank_corrections_dev/PythonOutput/TW{}_results.xlsx'.format(input_name)) as writer:
#
#         # use to_excel function and specify the sheet_name and index
#         # to store the dataframe in specified sheet
#         refs.to_excel(writer, sheet_name="Current MCCs", index=False)
#         stds_dataframe.to_excel(writer, sheet_name="Current MCC Details", index=False)
#         df.to_excel(writer, sheet_name="TW{}_results".format(input_name), index=False)
#

# """
# The next function will create the secondaries plots that we're interested in...
#
# The script that Valerie created exports data from RLIMS into the I: drive f"TW{}standards.xlsx"
#
# This data INCLUDES the wheel of interest
#
#
# """
#
#
# def plot_seconds_all(input_name):
#     aa = []
#     aaa = []
#     a = []
#     b = []
#     c = []
#     d = []
#     e = []
#     f = []
#     g = []
#     h = []
#     z = []
#     p = []
#     k = []
#     l = []
#
#     # READ in the standards/the last 1 year of data that was exported from RLIMS
#     stds_hist = pd.read_excel(r'I:\C14Data\C14_blank_corrections_dev\TW{}standards.xlsx'.format(input_name)).dropna(
#         subset='Date Run').reset_index(drop=True)
#     stds_hist = stds_hist.loc[
#         (stds_hist['Quality Flag'] == '...')]  # Index: drop everything that contains a quality flag
#     # find only categories that are our Large and Small standards.
#     stds_hist = stds_hist.loc[stds_hist['Category Field'].isin(['RRL-UNSt-LG', 'RRL-UNSt-SM'])]
#     names = np.unique(stds_hist['R_number'])
#     twmin = int(min(stds_hist['TW']))
#     twmax = int(max(stds_hist['TW']))
#
#     # have a look - what the secondaries in this wheel only?
#     # focus on ONLY the stds that are in the wheel of interest
#     for i in range(0, len(names)):
#         # grab the first standard type.
#         this_one = stds_hist.loc[stds_hist['R_number'] == names[i]]
#
#         # grab the description for the plot title.
#         descrip = this_one['Description from Sample'].reset_index(drop=True)
#         descrip = descrip[0]
#
#         # filter by size.
#         smalls = this_one.loc[this_one['wtgraph'] <= 0.3]
#         x = int(len(smalls))
#
#         large = this_one.loc[this_one['wtgraph'] >= 0.3]
#
#         small_mean_rts = np.nanmean(smalls['Ratio to standard'])
#         small_std_rts = np.nanstd(smalls['Ratio to standard'])
#         large_mean_rts = np.nanmean(large['Ratio to standard'])
#         large_std_rts = np.nanstd(large['Ratio to standard'])
#
#         # get rid of any missing data for the 13C values.
#         smalls13C_IRMS = smalls.dropna(subset='delta13C_IRMS').reset_index(drop=True)
#         large13C_IRMS = large.dropna(subset='delta13C_IRMS').reset_index(drop=True)
#         smalls13C_AMS = smalls.dropna(subset='delta13C_AMS').reset_index(drop=True)
#         large13C_AMS = large.dropna(subset='delta13C_AMS').reset_index(drop=True)
#
#         small_mean_13_IRMS = np.nanmean(smalls['delta13C_IRMS'])
#         small_std_13_IRMS = np.nanstd(smalls['delta13C_IRMS'])
#         large_mean_13_IRMS = np.nanmean(large['delta13C_IRMS'])
#         large_std_13_IRMS = np.nanstd(large['delta13C_IRMS'])
#
#         small_mean_13_AMS = np.nanmean(smalls['delta13C_AMS'])
#         small_std_13_AMS = np.nanstd(smalls['delta13C_AMS'])
#         large_mean_13_AMS = np.nanmean(large['delta13C_AMS'])
#         large_std_13_AMS = np.nanstd(large['delta13C_AMS'])
#
#         aa.append(names[i])
#         aaa.append(descrip)
#         a.append(small_mean_rts)
#         b.append(small_std_rts)
#         c.append(large_mean_rts)
#         d.append(large_std_rts)
#
#         e.append(small_mean_13_AMS)
#         f.append(small_std_13_AMS)
#         g.append(large_mean_13_AMS)
#         h.append(large_std_13_AMS)
#
#         z.append(small_mean_13_IRMS)
#         p.append(small_std_13_IRMS)
#         k.append(large_mean_13_IRMS)
#         l.append(large_std_13_IRMS)
#
#         # make the figure
#         fig1 = plt.figure(constrained_layout=True, figsize=(10, 8))
#         fig1.suptitle(f'{descrip}_{names[i]}: TW{twmin} to TW{twmax}')
#         spec2 = gridspec.GridSpec(ncols=2, nrows=2, figure=fig1)
#         f1_ax1 = fig1.add_subplot(spec2[0, 0])
#         f1_ax2 = fig1.add_subplot(spec2[0, 1])
#         f1_ax3 = fig1.add_subplot(spec2[1, 0])
#         f1_ax4 = fig1.add_subplot(spec2[1, 1])
#
#         f1_ax1.set_ylabel("14C: Ratio to OX1")
#         f1_ax3.set_ylabel("delta13C_In_Calculation")
#
#         f1_ax3.set_xlabel("Wheel #")
#         f1_ax4.set_xlabel("Wheel #")
#
#         f1_ax1.set_title("Large (>.3 mg)")
#         f1_ax2.set_title("Small (<.3 mg)")
#
#         # plot the data
#         # plot large and small 14C data
#         f1_ax1.errorbar(large['TW'], large['Ratio to standard'], large['Ratio to standard error'], fmt='o', capsize=3,
#                         color='black')
#         f1_ax2.errorbar(smalls['TW'], smalls['Ratio to standard'], smalls['Ratio to standard error'], fmt='o',
#                         capsize=3, color='black')
#         f1_ax1.axhline(large_mean_rts, color='black')
#         f1_ax2.axhline(small_mean_rts, color='black')
#
#         # plot large and small 13C IRMS data
#         f1_ax3.scatter(large13C_IRMS['TW'], large13C_IRMS['delta13C_IRMS'], color='blue', label='IRMS', marker='D')
#         f1_ax4.scatter(smalls13C_IRMS['TW'], smalls13C_IRMS['delta13C_IRMS'], color='blue', marker='D')
#         f1_ax3.axhline(large_mean_13_IRMS, color='blue')
#         f1_ax4.axhline(small_mean_13_IRMS, color='blue')
#         # f1_ax3.legend()
#
#         # plot large and small 13C AMS Data
#         f1_ax3.scatter(large13C_AMS['TW'], large13C_AMS['delta13C_AMS'], color='black', label='AMS')
#         f1_ax4.scatter(smalls13C_AMS['TW'], smalls13C_AMS['delta13C_AMS'], color='black')
#         f1_ax3.axhline(large_mean_13_AMS, color='black')
#         f1_ax4.axhline(small_mean_13_AMS, color='black')
#         f1_ax3.legend()
#
#         # add the 1-sigma
#         try:
#             f1_ax1.fill_between(large['TW'], (large_mean_rts + large_std_rts), (large_mean_rts - large_std_rts),
#                                 alpha=0.3, color='brown')
#             f1_ax3.fill_between(large13C_IRMS['TW'], (large_mean_13_IRMS + large_std_13_IRMS),
#                                 (large_mean_13_IRMS - large_std_13_IRMS), alpha=0.3, color='blue')
#             f1_ax3.fill_between(large13C_AMS['TW'], (large_mean_13_AMS + large_std_13_AMS),
#                                 (large_mean_13_IRMS - large_std_13_AMS), alpha=0.3, color='brown')
#             f1_ax2.fill_between(smalls['TW'], (small_mean_rts + large_std_rts), (small_mean_rts - large_std_rts),
#                                 alpha=0.3, color='brown')
#             f1_ax4.fill_between(smalls13C_IRMS['TW'], (small_mean_13_IRMS + small_std_13_IRMS),
#                                 (small_mean_13_IRMS - small_std_13_IRMS), alpha=0.3, color='blue')
#             f1_ax4.fill_between(smalls13C_AMS['TW'], (small_mean_13_AMS + small_std_13_AMS),
#                                 (small_mean_13_IRMS - small_std_13_AMS), alpha=0.3, color='brown')
#         except IndexError:
#             dummyvar = 0
#
#         newname = names[i].replace("/", "_")
#         newdesk = descrip.replace(":", "")
#         plt.savefig(
#             f'I:/C14Data/C14_blank_corrections_dev/Quality_Assurance/Plots/TW{input_name}+{newdesk}+{newname}.png')
#     #
#     # save these data to a table
#     results = pd.DataFrame({"R_number": aa,
#                             "Description": aaa,
#                             "Large RTS Mean": c,
#                             "Large RTS std": d,
#                             "Large AMS 13C Mean": g,
#                             "Large AMS 13C std": h,
#                             "Large IRMS 13C Mean": k,
#                             "Large IRMS 13C std": l,
#
#                             "Small RTS Mean": a,
#                             "Small RTS std": b,
#                             "Smalls AMS 13C Mean": e,
#                             "Smalls AMS 13C std": f,
#                             "Smalls IRMS 13C Mean": z,
#                             "Smalls IRMS 13C std": p,
#                             })
#     results.to_excel(
#         f'I:/C14Data/C14_blank_corrections_dev/Quality_Assurance/Data/TW{twmin}_to_TW{twmax}_standards_summary.xlsx')
#
# # # x = plot_seconds_thiswheel(3461)
# # x = plot_seconds_all(3461)
