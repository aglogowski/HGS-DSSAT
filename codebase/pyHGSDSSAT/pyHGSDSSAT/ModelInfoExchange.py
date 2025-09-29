import os
import numpy as np
import pandas as pd
import pickle as pkl

def ExposeMappingVariables(coupled_mod_dir):
    """

    Parameters:
    coupled_mod_dir (str): path to coupled model
            
    Returns:
    mapping_dict (dict): dictionary containing all mapping information

    """
    # Get path
    mapping_dict_path = os.path.join(coupled_mod_dir,r'mapping\mapping_pkl.p')
    # Unpickle the file
    with open(mapping_dict_path,'rb') as file:
        mapping = pkl.load(file)
    return mapping

def GenerateNodalFluxTimeValueTableDSSATET(mapping,day,coupled_mod_hgs_dir,coupled_mod_dssat_dir):
    """Build the daily ET Time Value tables, to bring DSSAT evaporation outputs into HGS

    Parameters:
    mapping(dict): mapping dictionary
    day (int): day of simulation
    coupled_mod_hgs_dir (str): path to coupled model HGS subdirectory
    coupled_mod_dssat_dir (str): path to coupled model DSSAT subdirectory
            
    Returns:

    """
    ## NEED TO CHECK IF SORTING HAS ANY POSSIBILITY OF GETTING MESSED UP
    ## Get # Nodes in Nodeset
    # Get # of HGS Node Sheets in Coupled Zone
    sheets_list = list(mapping['hnsdb'].keys())
    sheets_list.sort()
    nodes_list = list(mapping['hncvdm'].keys())
    nodes_list.sort()
    print(sheets_list,nodes_list)
    num_nodes = len(sheets_list) * len(nodes_list)
    ## Get DSSAT ET Vals
    # Blank dict to store values
    vals_dict = {}
    # Iterate through DSSAT model id's
    model_ids_list = list(mapping['dm_area_shp'].keys())
    for id in model_ids_list:
        # Dict
        vals_dict[id] = {}
        # Load ET Out File
        dssat_zone_mod_path = os.path.join(coupled_mod_dssat_dir,str(id))
        etout_path = os.path.join(dssat_zone_mod_path,'ET.OUT')
        print(etout_path)
        et_df = pd.read_csv(etout_path, skiprows = 12, sep = '\s+')
        print(et_df)
        # Load RWU File
        dssat_zone_mod_data_path = os.path.join(dssat_zone_mod_path,'data')
        rwu_path = os.path.join(dssat_zone_mod_data_path,'RWU.txt')
        headers = ['day']
        for n in np.arange(1,21):
            headers.append(str(n))
        rwu_df = pd.read_csv(rwu_path, names=headers, sep = '\s+')
        print(rwu_df)
        # Iterate through DSSAT Model Layers
        layers_list = list(mapping['dlhl'].keys())
        rwu_temp=[]
        for layer in layers_list:
            # vals_dict[id][layer] = et_df.iloc[-1,:]['ES{}D'.format(layer)] + rwu_df.iloc[-1,:][str(layer)]
            vals_dict[id][layer] = et_df.loc[et_df['DAS'] == day,'ES{}D'.format(layer)].values[0] + rwu_df.loc[rwu_df['day'] == day,str(layer)].values[0]
            #print(vals_dict)
        print(vals_dict)
    ## Store HGS Nodal Flux vals
    vals_list = []
    # Iterate through node sheets from lowest to highest
    for i,sheet in enumerate(sheets_list):
        print(i,sheet)
        # Iterate through nodes in each node sheet
        for node in nodes_list:
            # Get DSSAT Model id
            id = mapping['hncvdm'][node][0]
            area = mapping['hncvdm'][node][1]
            # Deal with Bottom Sheet
            if i == 0:
                ## Up Flux
                # Get DSSAT Layer #
                dslay = mapping['hnsdb'][sheet] - 1
                # Get DSSAT flux
                uflux = vals_dict[id][dslay]
                print(i,uflux)
                # Get HGS equivalent ET Flux
                val = 0.5*uflux * -1 * 24. * 60. / 1000. * area
                vals_list.append(val)
            # Deal with Top Sheet
            elif i == len(sheets_list)-1:
                ## Down Flux
                # Get DSSAT Layer #
                dslay = mapping['hnsdb'][sheet]
                # Get DSSAT flux
                dflux = vals_dict[id][dslay]
                print(i,dflux)
                # Get HGS equivalent ET Flux
                val = 0.5*dflux * -1 * 24. * 60. / 1000. * area
                vals_list.append(val)
            # All other sheets
            else:
                ## Up Flux
                # Get DSSAT Layer #
                dslay = mapping['hnsdb'][sheet] - 1
                # Get DSSAT flux
                uflux = vals_dict[id][dslay]
                ## Down Flux
                # Get DSSAT Layer #
                dslay = mapping['hnsdb'][sheet]
                # Get DSSAT flux
                dflux = vals_dict[id][dslay]
                print(i,uflux,dflux)
                # Get HGS equivalent ET Flux
                val = ((0.5*uflux) + (0.5*dflux)) * -1 * 24. * 60. / 1000. * area
                vals_list.append(val)
    ## Write out file
    # nflux file path
    nflux_path = os.path.join(coupled_mod_hgs_dir,'nflux.txt')
    arch_nflux_path = os.path.join(coupled_mod_hgs_dir,str(day)+ 'nflux.txt')
    # Write vals from val list
    with open(nflux_path,'w') as file:
        file.write(str(num_nodes) + '\n')
        for val in vals_list:
            file.write(str(val) + '\n')
    with open(arch_nflux_path,'w') as file:
        file.write(str(num_nodes) + '\n')
        for val in vals_list:
            file.write(str(val) + '\n')        


def GenerateDSSATDailyDRNHGSNodalFlux(mapping,day,model_name,coupled_mod_hgs_dir,coupled_mod_dssat_dir):
    """Generate daily DRN file for each DSSAT model that summarizes downward flux through each nodesheet according to HGS model.

    Parameters:
    mapping(dict): mapping dictionary
    day (int): day of simulation
    model_name (str):
    coupled_mod_hgs_dir (str): path to coupled model HGS subdirectory
    coupled_mod_dssat_dir (str): path to coupled model DSSAT subdirectory

    Returns:
    
    """
    # Get right dictionary
    dm_area_shp_dict = mapping['dm_area_shp']
    # Get list of Zones (combinations of nodal control volumes)/DSSAT Model ID's
    zones_list = list(dm_area_shp_dict.keys())
    # Iterate through DSSAT model id's
    for id in zones_list:
        # Get area of nodal control volume
        area = dm_area_shp_dict[id]
        # Get path to nfmb file
        nfmb_path = os.path.join(coupled_mod_hgs_dir,model_name+'_day'+str(day)+'o.nodal_fluid_mass_balance.id_str.dat')
        
        # Open file and grab area and variable list
        with open(nfmb_path,'r') as file:
            for i,line in enumerate(file.readlines()):
                if i == 1:
                    area = float(line.split(':')[1].strip())
                elif i == 2: #make this Variable related to be flexible for changes
                    vars = [x.replace('"','') for x in line.strip().split('=')[1].split(',')]
                    
                else:
                    if 'Zone T=' in line:
                        start_line = i+1
        # Load whole table as df
        print(vars)
        print(start_line)
        df = pd.read_csv(nfmb_path, skiprows = start_line, names = vars, delim_whitespace=True)
        print(df)
        # Get column of time increment
        df['Time Inc'] = df['Time'].diff()
        df.loc[0,'Time Inc'] = df['Time'].values[0]
        # Iterate thru node sheets to get drainage fluxes
        hnsdb_dict = mapping['hnsdb']
        node_sheets = list(hnsdb_dict.keys())
        top_node_sheet = np.max(node_sheets)
        bottom_node_sheet = np.min(node_sheets)
        Net_Q_Vals = []
        for i in np.flip(np.arange(bottom_node_sheet,top_node_sheet)):
            net_q_name = 'Net_Q_{:02d}'.format(i)
            df[net_q_name] = df.apply(lambda x: (x['QVD+{:02d}'.format(i)]+-1*(x['QVU-{:02d}'.format(i)]))*x['Time Inc']/area*100., axis = 1)
            Net_Q_Vals.append(df[net_q_name].sum())
        # Write out to file
        zone_mod_path = os.path.join(coupled_mod_dssat_dir,r'{}\data'.format(id))
        drn_path = os.path.join(zone_mod_path,'DRN_{}.inp'.format(day))
        with open(drn_path,'w') as file:
            line = ''
            for val in Net_Q_Vals:
                line += (f"{val:7.4f}"+'   ')
            for i in range(11):
                line +=(f" 0.0000"+'   ')
            file.write(line)