import os
import numpy as np
import pandas as pd

def GenerateNodalFluxTimeValueTableDSSATET(mapping_pkl_path,rz_node_order_file_path,coupled_mod_hgs_dir,coupled_mod_dssat_dir):
    """Build the daily ET Time Value tables, to bring DSSAT evaporation outputs into HGS

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
    for day in range(275):
        # Blank list for vals
        vals = []
        # Load CSV's
        # Identify path to DSSAT Surface ET file
        surface_data_path = os.path.join(coupled_mod_dssat_dir,'Full_SurfaceET.txt')
        # Load
        surface_data = pd.read_csv(surface_data_path, sep = '\s+')['EOAA'].values
        # Identify path to DSSAT Soil ET file
        soil_data_path = os.path.join(coupled_mod_dssat_dir,'Full_SoilET.txt')
        # Load
        soil_data = pd.read_csv(soil_data_path, sep = '\s+')
        # Iterate through nodes
        for node in nodes:
            # Get DSSAT location information
            dssat_model,sheet,area_stat = map_dict[node]
            # Get surface ET and half of soil layer 1 for sheet 0
            if sheet == 0:
                # Grab val up from surface file
                valup = surface_data[day]
                # Grab val down from soil file layer 1
                valdn = soil_data['ES{}D'.format(sheet + 1)].values[day]
                # Set value to full surface ET + 1/2 of layer 1 ET
                val = (valup + (0.5*valdn)) * -1 * 24. * 60. / 1000. * (1./area_stat)
            # For bottom node sheet, just get half of last DSSAT layer
            elif sheet == 10:
                # Grab val down from soil file layer 1
                valup = soil_data['ES{}D'.format(sheet)].values[day]
                # Set value to 1/2 of layer 10 ET
                val = ((0.5*valup)) * -1 * 24. * 60. / 1000. * (1./area_stat)
            # For all other sheets, take half of layer above and half of layer below
            else:
                # Grab val down from soil file layer 1
                valup = soil_data['ES{}D'.format(sheet)].values[day]
                # Grab val down from soil file layer 1
                valdn = soil_data['ES{}D'.format(sheet + 1)].values[day]
                # Set value to 1/2 of layer n ET and 1/2 of layer n+1 ET
                val = ((0.5*valdn) + (0.5*valup)) * -1 * 24. * 60. / 1000. * (1./area_stat)
            # Convert DSSAT total mm to HGS total m3 and then multiply by minutes in a day to force all to be taken out in first minute of day
            vals.append(val)
        print(vals)
        # Write out nflux.txt file
        nflux_path = os.path.join(coupled_mod_hgs_dir,'n{}flux.txt'.format(day))
        with open(nflux_path,'w') as file:
            file.write(str(len(vals))+'\n')
            lines = []
            for val in vals:
                lines.append(str(val)+'\n')
            lines[-1] = lines[-1][:-1]
            for line in lines:
                file.write(line)

def GenerateDRNFileFromHGSNFMB(model_name,coupled_mod_hgs_dir,coupled_mod_dssat_dir,dm_area_shp_dict,hldl_dict,day):
    """Generate Shapefile of HGS nodes and control volumes to assist in mapping process used to link DSSAT models to HGS zones.

    Parameters:
    model_name (str):
    coupled_mod_hgs_dir (str):
    coupled_mod_dssat_dir (str):
    dm_area_shp_dict (dict):
    hldl_dict (dict):
    day (int): 

    Returns:

    
    """
    # Iterate through DSSAT model id's
    for id in list(dm_area_shp_dict.keys()):
        # Get area of nodal control volume
        area = dm_area_shp_dict[id]
        # Get path to nfmb file
        nfmb_path = os.path.join(coupled_mod_hgs_dir,model_name +str(day)+'o.nodal_fluid_mass_balance.nfmb_dssat_id_'+id+'.dat')
        # Open file and grab area and variable list
        with open(nfmb_path,'r') as file:
            for i,line in enumerate(file.readlines()):
                if i == 1:
                    area = float(line.split(':')[1].strip())
                elif i == 3:
                    vars = [x.replace('"','') for x in line.strip().split('=')[1].split(',')]
                else:
                    if 'Zone T=' in line:
                        start_line = i+1
        # Load whole table as df
        df = pd.read_csv(nfmb_path, skiprows = start_line, names = vars, delim_whitespace=True)
        # Get column of time increment
        df['Time Inc'] = df['Time'].diff()
        df.loc[0,'Time Inc'] = df['Time'].values[0]
        # Iterate thru node sheets to get drainage fluxes
        node_sheets = list(hldl_dict.keys())
        top_node_sheet = np.max(node_sheets)
        bottom_node_sheet = np.min(node_sheets)
        Net_Q_Vals = []
        for i in np.flip(np.arange(bottom_node_sheet,top_node_sheet)):
            net_q_name = 'Net_Q_{:02d}'.format(i)
            df[net_q_name] = df.apply(lambda x: (x['QVD+{:02d}'.format(i)]+-1*(x['QVD-{:02d}'.format(i)]))*x['Time Inc']/area*100., axis = 1)
            Net_Q_Vals.append(df[net_q_name].sum())
        # Write out to file
        drn_path = os.path.join(coupled_mod_dssat_dir,'{}_{}_DRN.inp'.format(id,day))
        with open(drn_path,'w') as file:
            line = ''
            for val in Net_Q_Vals:
                line += (f"{val:7.4f}"+'   ')
            for i in range(9):
                line +=(f" 0.0000"+'   ')
            file.write(line)
