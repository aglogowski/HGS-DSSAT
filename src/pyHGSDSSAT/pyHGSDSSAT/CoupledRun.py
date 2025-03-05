import os
import subprocess as sp
import pickle as pkl
import pandas as pd
from time import sleep

def Create_HGS_Model_Batch_File(coupled_mod_dir,coupled_mod_hgs_dir):
    """Create a batch file to run a single HGS model

    Parameters:
    coupled_mod_dir (str): path of coupled model directory
    coupled_mod_hgs _dir (str): path of HGS subdirectory in coupled model directory

    Returns:

   """
    controller_path = os.path.join(coupled_mod_dir,'HGS_Controller.bat')
    with open(controller_path,'w') as file:
        file.write('cd hgs\ngrok > out_g.txt\nphgs > out_h.txt\nhsplot\ncd ..'.format(coupled_mod_hgs_dir))
    out_path = os.path.join(coupled_mod_hgs_dir,'out.txt')
    with open(out_path,'w') as file:
        file.write('')


def Run_Coupled_Model_HGS_Day(day,grok_file_stem,coupled_mod_hgs_dir):
    """Launch a single day HGS model

    Parameters:
    day (int): days after start of simulation
    grok_file_stem (str): standalone hgs grok file name minus file extension
    coupled_mod_hgs _dir (str): path of HGS subdirectory in coupled model directory

    Returns:

   """
    grok_name = grok_file_stem + 'day{}'.format(day)
    # First, update batch.pfx to identify correct grok file for this day
    print('Updating batch.pfx')
    batch_pfx_path = os.path.join(coupled_mod_hgs_dir,'batch.pfx')
    with open(batch_pfx_path,'w') as file:
        file.write(grok_name)
    # Then run Controller
    print('Launch HGS')
    sp.run(['HGS_Controller.bat'])



### Functions involved in updating models

def Build_ET_Time_Value_Table(mapping_pkl_path,rz_node_order_file_path,coupled_mod_hgs_dir,coupled_mod_dssat_dir):
    """Build the ET Time Value table for a single day, to bring DSSAT evaporation outputs into HGS

    Parameters:
    mapping_pkl_path (str): path to pickle file containing mapping information
    rz_node_order_file_path (str): path to file containing the order of HGS nodes in the root zone
    coupled_mod_hgs_dir (str): path to coupled model HGS subdirectory
    coupled_mod_dssat_dir (str): path to coupled model DSSAT subdirectory
        
            
    Returns:

   """
    # Load node list
    with open(rz_node_order_file_path,'r') as file:
        lines = file.readlines()
    nodes = [int(x.strip()) for x in lines]
    # Load mapping pickle
    with open(mapping_pkl_path,'rb') as file:
        map_dict = pkl.load(file)
    # Blank list for vals
    vals = []
    # Iterate through nodes
    for node in nodes:
        # Get DSSAT location information
        dssat_model,sheet,area_stat = map_dict[node]
        # Get surface ET and half of soil layer 1 for sheet 0
        if sheet == 0:
            # Identify path to DSSAT Surface ET file
            dssat_data_path = os.path.join(coupled_mod_dssat_dir,str(dssat_model) + '_SurfaceET.csv')
            # Grab val up from surface file
            valup = pd.read_csv(dssat_data_path)['EOAA'].values[0]
            # Identify path to DSSAT Soil ET File
            dssat_data_path = os.path.join(coupled_mod_dssat_dir,str(dssat_model) + '_SoilET.csv')
            # Grab val down from soil file layer 1
            valdn = pd.read_csv(dssat_data_path)['ES{}D'.format(sheet + 1)].values[0]
            # Set value to full surface ET + 1/2 of layer 1 ET
            val = (valup + (0.5*valdn)) * -1 * 24. * 60. / 1000. * (1./area_stat)
        # For bottom node sheet, just get half of last DSSAT layer
        elif sheet == 10:
            # Identify path to DSSAT Soil ET File
            dssat_data_path = os.path.join(coupled_mod_dssat_dir,str(dssat_model) + '_SoilET.csv')
            # Grab val down from soil file layer 1
            valup = pd.read_csv(dssat_data_path)['ES{}D'.format(sheet)].values[0]
            # Set value to 1/2 of layer 10 ET
            val = ((0.5*valup)) * -1 * 24. * 60. / 1000. * (1./area_stat)
        # For all other sheets, take half of layer above and half of layer below
        else:
            # Identify path to DSSAT Soil ET File
            dssat_data_path = os.path.join(coupled_mod_dssat_dir,str(dssat_model) + '_SoilET.csv')
            # Grab val down from soil file layer 1
            valup = pd.read_csv(dssat_data_path)['ES{}D'.format(sheet)].values[0]
            # Grab val down from soil file layer 1
            valdn = pd.read_csv(dssat_data_path)['ES{}D'.format(sheet + 1)].values[0]
            # Set value to 1/2 of layer n ET and 1/2 of layer n+1 ET
            val = ((0.5*valdn) + (0.5*valup)) * -1 * 24. * 60. / 1000. * (1./area_stat)
        # Convert DSSAT total mm to HGS total m3 and then multiply by minutes in a day to force all to be taken out in first minute of day
        vals.append(val)
    # Write out nflux.txt file
    nflux_path = os.path.join(coupled_mod_hgs_dir,'nflux.txt')
    with open(nflux_path,'w') as file:
        file.write(str(len(vals))+'\n')
        lines = []
        for val in vals:
            lines.append(str(val)+'\n')
        lines[-1] = lines[-1][:-1]
        for line in lines:
            file.write(line)


def Build_Solute_IC_File(day,mapping_pkl_path,rz_node_order_file_path,full_node_order_file_path,grok_file_stem,coupled_mod_dssat_dir,coupled_mod_hgs_dir):
    """Build files used to apply solute concentrations from DSSAT as initial conditions in a daily HGS model

    Parameters:
    day (int): days after start of simulation
    mapping_pkl_path (str): path to pickle file containing mapping information
    rz_node_order_file_path (str): path to file containing the order of HGS nodes in the root zone
    full_node_order_file_path (str): path to file containing the order of HGS nodes in the HGS model
    grok_file_stem (str): standalone hgs grok file name minus file extension
    coupled_mod_dssat_dir (str): path to coupled model DSSAT subdirectory
    coupled_mod_hgs_dir (str): path to coupled model HGS subdirectory

        
            
    Returns:

   """
    # Load rz node list
    with open(rz_node_order_file_path,'r') as file:
        lines = file.readlines()
    rz_nodes = [int(x.strip()) for x in lines]
    # Load full node list
    with open(full_node_order_file_path,'r') as file:
        lines = file.readlines()
    full_nodes = [int(x.strip()) for x in lines]
    # Get list of non-coupled nodes
    hgs_only_nodes = [x for x in full_nodes if not (x in rz_nodes)]
    # Load mapping pickle
    with open(mapping_pkl_path,'rb') as file:
        map_dict = pkl.load(file)
    # Blank list for vals
    vals = []
    ## Load yesterdays HGS NH3 and NO4 values
    # Get pm file path
    pm_file = grok_file_stem.split('_')[0] + '_eday{}o.pm.dat'.format(day-1)
    pm_file_path = os.path.join(coupled_mod_hgs_dir,pm_file)
    # Load lines
    with open(pm_file_path,'r') as file:
        lines = file.readlines()
    # Get last entry in file for solution time = 1
    start = [i for i, line in enumerate(lines) if 'SOLUTIONTIME=1.00000000000000' in line][0]
    # Get indexes for starts and ends of no3 and nh4 sections
    st1lines = lines[start:]
    start_no3 = st1lines.index('# NO3\n')
    sub_lines = st1lines[start_no3:]
    inds = [i for i, line in enumerate(sub_lines) if '#' in line]
    no3lines = sub_lines[inds[0]+1:inds[1]]
    nh4lines = sub_lines[inds[1]+1:inds[2]]
    hgs_no3_vals = []
    for line in no3lines:
        for num in line.strip().split():
            hgs_no3_vals.append(float(num))
    hgs_nh4_vals = []
    for line in nh4lines:
        for num in line.strip().split():
            hgs_nh4_vals.append(float(num))
    ## Load dssat vals
    # Get list of possible dssat model names
    dssat_models = set([map_dict[x][0] for x in map_dict.keys()])
    # Store dssat vals in dictionary
    dssat_no3_vals = {}
    for mdl in dssat_models:
        dssat_output_path = os.path.join(coupled_mod_dssat_dir,str(mdl) + '_SoilNO3.csv')
        dssat_no3_vals[mdl] = pd.read_csv(dssat_output_path)
    dssat_nh4_vals = {}
    for mdl in dssat_models:
        dssat_output_path = os.path.join(coupled_mod_dssat_dir,str(mdl) + '_SoilNH4.csv')
        dssat_nh4_vals[mdl] = pd.read_csv(dssat_output_path)
    ## Iterate through nodes and store values from correct source in list
    no3_vals = []
    for node in hgs_only_nodes:
        # Get concentration from hgs_vals and append to list
        no3_vals.append(hgs_no3_vals[-1*node])
    for node in rz_nodes:
        # Identify model and sheet number
        mdl,sheet,a_stat = map_dict[node]
        # Get concentration from dssat_vals, convert and append to list
        if sheet == 0:
            no3_vals.append(dssat_no3_vals[mdl].loc[0,'NI{}D'.format(sheet+1)]*1000.)
        elif sheet == 10:
            no3_vals.append(dssat_no3_vals[mdl].loc[0,'NI{}'.format(sheet)]*1000.)
        elif sheet == 9:
            no3_vals.append(0.5*(dssat_no3_vals[mdl].loc[0,'NI{}D'.format(sheet)]*1000.)+0.5*(dssat_no3_vals[mdl].loc[0,'NI{}'.format(sheet+1)]*1000.))
        else:
            no3_vals.append(0.5*(dssat_no3_vals[mdl].loc[0,'NI{}D'.format(sheet)]*1000.)+0.5*(dssat_no3_vals[mdl].loc[0,'NI{}D'.format(sheet+1)]*1000.))
    nh4_vals = []
    for node in hgs_only_nodes:
        # Get concentration from hgs_vals and append to list
        nh4_vals.append(hgs_nh4_vals[-1*node])
    for node in rz_nodes:
        # Identify model and sheet number
        mdl,sheet,a_stat = map_dict[node]
        # Get concentration from dssat_vals, convert and append to list
        if sheet == 0:
            nh4_vals.append(dssat_nh4_vals[mdl].loc[0,'NH{}D'.format(sheet+1)]*1000.)
        elif sheet == 10:
            nh4_vals.append(dssat_nh4_vals[mdl].loc[0,'NH{}'.format(sheet)]*1000.)
        elif sheet == 9:
            nh4_vals.append(0.5*(dssat_nh4_vals[mdl].loc[0,'NH{}D'.format(sheet)]*1000.)+0.5*(dssat_nh4_vals[mdl].loc[0,'NH{}'.format(sheet+1)]*1000.))
        else:
            nh4_vals.append(0.5*(dssat_nh4_vals[mdl].loc[0,'NH{}D'.format(sheet)]*1000.)+0.5*(dssat_nh4_vals[mdl].loc[0,'NH{}D'.format(sheet+1)]*1000.))
    # Write out to file
    iconc_path = os.path.join(coupled_mod_hgs_dir,'iconc.txt')
    with open(iconc_path,'w') as file:
        lines = []
        for val in no3_vals:
            lines.append(str(val)+'\n')
        for val in nh4_vals:
            lines.append(str(val)+'\n')
        for line in lines:
            file.write(line)


## Main functions

def HGS_Daily_Loop(day,mapping_pkl_path,rz_node_order_file_path,full_node_order_file_path,grok_file_stem,coupled_mod_dir,coupled_mod_hgs_dir,coupled_mod_dssat_dir):
    """Synthesize and run all of the steps of the HGS daily loop

    Parameters:
    day (int): days after start of simulation
    mapping_pkl_path (str): path to pickle file containing mapping information
    rz_node_order_file_path (str): path to file containing the order of HGS nodes in the root zone
    full_node_order_file_path (str): path to file containing the order of HGS nodes in the HGS model
    grok_file_stem (str): standalone hgs grok file name minus file extension
    coupled_mod_dssat_dir (str): path to coupled model DSSAT subdirectory
    coupled_mod_hgs_dir (str): path to coupled model HGS subdirectory
            
    Returns:

    """
    if day > 0:
        print('Creating nflux filed for DSSAT ET: Day {}'.format(day))
        Build_ET_Time_Value_Table(mapping_pkl_path,rz_node_order_file_path,coupled_mod_hgs_dir,coupled_mod_dssat_dir)
        print('Creating solute IC file for DSSAT solute outputs: Day {}'.format(day))
        # Build_Solute_IC_File(day,mapping_pkl_path,rz_node_order_file_path,full_node_order_file_path,grok_file_stem,coupled_mod_dssat_dir,coupled_mod_hgs_dir)
    Run_Coupled_Model_HGS_Day(day,grok_file_stem,coupled_mod_hgs_dir,)

def Dummy_DSSAT_1Day_Run():
    """Dummy function for development purposes - pretend that a DSSAT model just ran

    Parameters:
    day (int): days after start of simulation
            
    Returns:

    """
    sleep(3)
