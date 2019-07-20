
from fastai.tabular import *
from flask import Flask, request
import requests
import os.path


path = ''

export_file_url = 'https://www.dropbox.com/s/zrdwbwj6q73hil5/nyc_construction_export.pkl?dl=1'
export_file_name = 'nyc_construction_export.pkl'


def down_load_file(filename, url):
    """
    Download an URL to a file
    """
    with open(filename, 'wb') as fout:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        # Write response data to file
        for block in response.iter_content(4096):
            fout.write(block)
            
def download_if_not_exists(filename, url):
    """
    Download a URL to a file if the file
    does not exist already.
    Returns
    -------
    True if the file was downloaded,
    False if it already existed
    """
    if not os.path.exists(filename):
        down_load_file(filename, url)
        return True
    return False

download_if_not_exists(export_file_name, export_file_url)

learn = load_learner(path, export_file_name)



app = Flask(__name__)

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        
        Project_Phase_Name = request.form.get('Project_Phase_Name')
        
        Project_Type = request.form.get('Project_Type')
        
        Actual_Start_Date = request.form.get('Actual_Start_Date')
        
        Project_Phase_Planned_End_Date = request.form.get('Project_Phase_Planned_End_Date')
        
        Project_Budget_Amount = request.form.get('Project_Budget_Amount')
        
        Final_Estimate_of_Actual_Costs_Through_End_of_Phase_Amount = request.form.get('Final_Estimate_of_Actual_Costs_Through_End_of_Phase_Amount')
        
        Total_Phase_Actual_Spending_Amount = request.form.get('Total_Phase_Actual_Spending_Amount')
        
        Borough = request.form.get('Borough')
        
        
        
        
        inf_df = pd.DataFrame(columns=['Project_Type','Project_Phase_Name', 'Project_Phase_Actual_Start_Date', 
                                       'Project_Phase_Planned_End_Date', 'Project_Budget_Amount', 
                                       'Final_Estimate_of_Actual_Costs_Through_End_of_Phase_Amount',
                                       'Total_Phase_Actual_Spending_Amount', 'Borough'])
        inf_df.loc[0] = [Project_Type, Project_Phase_Name, Actual_Start_Date, Project_Phase_Planned_End_Date,
                         Project_Budget_Amount, Final_Estimate_of_Actual_Costs_Through_End_of_Phase_Amount, 
                         Total_Phase_Actual_Spending_Amount, Borough]
        
        
        
        inf_df['Project_Phase_Actual_Start_Date'] =  pd.to_datetime(inf_df['Project_Phase_Actual_Start_Date'])
        inf_df['Project_Phase_Planned_End_Date'] =  pd.to_datetime(inf_df['Project_Phase_Planned_End_Date'])
        inf_df['Project_Budget_Amount'] =  inf_df['Project_Budget_Amount'].astype(float)
        inf_df['Final_Estimate_of_Actual_Costs_Through_End_of_Phase_Amount'] =  inf_df['Final_Estimate_of_Actual_Costs_Through_End_of_Phase_Amount'].astype(float)
        inf_df['Total_Phase_Actual_Spending_Amount'] = inf_df['Total_Phase_Actual_Spending_Amount'].astype(float)
        inf_df['Phase_Planned_Duration'] = inf_df['Project_Phase_Planned_End_Date']-inf_df['Project_Phase_Actual_Start_Date']
        inf_df['Phase_Planned_Duration_Days'] = (inf_df['Project_Phase_Planned_End_Date']-inf_df['Project_Phase_Actual_Start_Date']) / pd.to_timedelta(1, unit='D')
        add_datepart(inf_df, 'Project_Phase_Actual_Start_Date')
        
        inf_row = inf_df.iloc[0]
        
        pred = learn.predict(inf_row)
        
    
        
        return '''<h3>The input Project Type is: {}</h3>
                    <h3>The input Project Phase Name is: {}</h3>
                    <h3>The input Project Phase Actual Start Date is: {}</h3>
                    <h3>The input Project Phase Planned End Date is: {}</h3>
                    <h3>The input Project Budget Amount is: {}</h3>
                    <h3>The input Final Estimate of Actual Costs Through End of Phase Amount is: {}</h3>
                    <h3>The input Total Phase Actual Spending Amount is: {}</h3>
                    <h3>The input Borough is: {}</h3>
                    <h1>The project is predicted to be: {}</h1>'''.format(Project_Type, 
                                                                                        Project_Phase_Name, 
                                                                                        Actual_Start_Date,
                                                                                       Project_Phase_Planned_End_Date,
                                                                             Project_Budget_Amount,
                                                                             Final_Estimate_of_Actual_Costs_Through_End_of_Phase_Amount,
                                                                                           Total_Phase_Actual_Spending_Amount,
                                                                                           Borough,
                                                                          pred
                                                                             )


    return '''<form method="POST">
                  <h1>Predicting whether a construction project will be on time</h1>
                  
                  Select Project Type: <select name="Project_Type">
                  <option value="SCA CIP">SCA CIP</option>
                  <option value="SCA CIP RESOA">SCA CIP RESOA</option>
                  <option value="SCA Capacity">SCA Capacity</option>
                  <option value="SCA Emergency Lighti">SCA Emergency Lighti</option>
                  <option value="3K">3K</option>
                  <option value="SCA Lease Site Impro">SCA Lease Site Impro</option>
                  <option value="PRE-K">PRE-K</option>
                  </select><br>
                  
                  Select Project Phase Name: <select name="Project_Phase_Name">
                  <option value="Design">Design</option>
                  <option value="Scope">Scope</option>
                  <option value="CM, F&E">CM, F&E</option>
                  <option value="Construction">Construction</option>
                  <option value="CM">CM</option>
                  </select><br>
                  
                  Project Phase Actual Start Date: <input type="date" name="Actual_Start_Date" required="required"><br>
                  
                  Project Phase Planned End Date: <input type="date" name="Project_Phase_Planned_End_Date" required="required"><br>
                  
                  Project Budget Amount: <input type="number" name="Project_Budget_Amount" step=0.01 min=0 required="required"><br>
                  
                  Final Estimate of Actual Costs Through End of Phase Amount: <input type="number" name="Final_Estimate_of_Actual_Costs_Through_End_of_Phase_Amount" step=0.01 min=0 required="required"><br>
                  
                  Total Phase Actual Spending Amount: <input type = "number" name="Total_Phase_Actual_Spending_Amount" step=0.01 min=0 required="required"><br>
                  
                  Select Borough: <select name="Borough">
                  <option value="Manhattan">Manhattan</option>
                  <option value="Staten Island">Staten Island</option>
                  <option value="Bronx">Bronx</option>
                  <option value="Brooklyn">Brooklyn</option>
                  <option value="Queens">Queens</option>
                  </select><br>
                  
                  <input type="submit" value="Submit"><br>
              </form>'''



#if __name__ == '__main__':
#    app.run(port=5000, debug=False)






