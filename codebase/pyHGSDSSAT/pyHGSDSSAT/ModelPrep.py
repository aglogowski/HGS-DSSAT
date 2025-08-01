import os
from shutil import copy
from numpy import arange



def Create_Coupled_Model_Dir(mod_dir,coupled_model_name):
    """Create a directory for a coupled HGS-DSSAT model run

    Parameters:
    mod_dir (str): path to parent directory named after model containing standalone HGS and DSSAT models
    coupled_model_name (str): name for coupled model directory
    
    Returns:
    coupled_mod_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files
    coupled_mod_hgs_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to HGS
    coupled_mod_dssat_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to DSSAT
    coupled_mod_mapping_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to mapping

   """
    # Create directories if they don't exist
    coupled_mod_dir = os.path.join(mod_dir,coupled_model_name)
    try:
        os.mkdir(coupled_mod_dir)
    except:
        print(coupled_mod_dir + ' already exists')
    # Create hgs subdirectory
    coupled_mod_hgs_dir = os.path.join(coupled_mod_dir,'hgs')
    try:
        os.mkdir(coupled_mod_hgs_dir)
    except:
        print(coupled_mod_hgs_dir + ' already exists')
    # Create dssat subdirectory
    coupled_mod_dssat_dir = os.path.join(coupled_mod_dir,'dssat')
    try:
        os.mkdir(coupled_mod_dssat_dir)
    except:
        print(coupled_mod_dssat_dir + ' already exists')
    # Create mapping subdirectory
    coupled_mod_mapping_dir = os.path.join(coupled_mod_dir,'mapping')
    try:
        os.mkdir(coupled_mod_mapping_dir)
    except:
        print(coupled_mod_mapping_dir + ' already exists')
    return coupled_mod_dir,coupled_mod_hgs_dir,coupled_mod_dssat_dir,coupled_mod_mapping_dir



def Get_HGS_Props_Files(hgs_mod_dir,coupled_mod_hgs_dir,model_name):
    """Copy props files from HGS

    Parameters:
    hgs_mod_dir (str): path to subdirectory containing standalone HGS model
    coupled_mod_hgs_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to HGS
    model_name (str): standalone hgs grok file name minus .grok

    Returns:
    
   """
    # Get file names
    mprops_name = model_name + '.mprops'
    oprops_name = model_name + '.oprops'
    etprops_name = model_name + '.etprops'
    for file in [mprops_name,oprops_name,etprops_name]:
        # Paths and copy
        copy(os.path.join(hgs_mod_dir,file),os.path.join(coupled_mod_hgs_dir,file))



def Get_NFMB_Shapefile(hgs_mod_dir,coupled_mod_hgs_dir):
    """Copy props files from HGS

    Parameters:
    hgs_mod_dir (str): path to subdirectory containing standalone HGS model
    coupled_mod_hgs_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to HGS
    shape_name (str): name of shape file minus file extension

    Returns:
    
   """
    shp_list = ['.cpg','.dbf','.shp','.shx']
    shp_list = ['nfmb_shp' + x for x in shp_list]
    for file in shp_list:
        copy(os.path.join(hgs_mod_dir,file),os.path.join(coupled_mod_hgs_dir,file))


def Get_Standalone_Grok_Lines(grok_file_path):
    """Get lines from standalone grok file as a list of python strings

    Parameters:
    grok_file_path (str): full path to grok file

    Returns:
    lines (list): list of strings containing contents of grok file
    
   """
    # Read grok file
    with open(grok_file_path,'r') as file_in:
        lines = file_in.readlines()
    return lines



def Get_Standalone_Grok_Prec_Series(standalone_grok_lines):
    """Get lines containing precipitation series and end day in grok file

    Parameters:
    standalone_grok_lines (list): list of strings containing contents of grok file

    Returns:
    p (list): list of daily p values from HGS
    end_day (int): last day of simulation
    
    """
    # Get start index
    start = standalone_grok_lines.index('!!--Begin Precipitation Time Series Section--\n')
    # Get end index
    end = standalone_grok_lines.index('!!--End Precipitation Time Series Section--\n')
    # Get P Block
    plines = standalone_grok_lines[start:end]
    # Get p series
    start = plines.index('    time value table\n')
    end = plines.index('    end\n')
    # Get time series lines
    tslines = plines[start+1:end]
    # Get Daily P Series
    p = [float(x.split()[1]) for x in tslines]
    # Get end day
    end_day = len(p)
    return p, end_day


def CreateETNodalFluxBlock(hnsdb_dict):
    """Create block of text defining ET subtraction with nodal fluxes

    Parameters:
    hnsdb_dict (dict): maps HGS node sheets to DSSAT borders

    Returns:
    nf_lines (list): list of strings containing contents of grok file nodal flux ET subtraction block
    
    """
    # Blank list to store strings
    nf_lines = []
    nf_lines.append('!Flux Nodal Block for Coupled Model\n')
    # Iterate to add all node sheets in coupled zone
    for val in list(hnsdb_dict.keys()):
        nf_lines.append('choose nodes sheet\n')
        nf_lines.append('{}\n'.format(val))
    # Add node creation
    nf_lines.append('\ncreate node set\ncoupled_section\n\nclear chosen zones\nclear chosen elements\nclear chosen nodes\nclear chosen faces\n\n')
    # Add BC Section
    nf_lines.append('! Set flux nodal to force DSSAT ET\nboundary condition\n    type\n    flux nodal\n\n    node set\n    coupled_section\n\n    time file table\n    0.0 nflux.txt\n    0.00069444 none\n    end\nend\n\n')
    return nf_lines

def CreateNFMBOutputBlock(dm_area_shp_dict):
    """Create block of text defining areas for which to output nodal fluid mass balance results, one for each DSSAT model

    Parameters:
    dm_area_shp_dict (dict): dictionary detailing area and shapefile path for each DSSAT model's associated nodal control volume

    Returns:
    onfmb_lines (list): list of strings containing contents of grok file nodal fluid mass balance for drainage calculation block
    
    """
    # Blank list to store strings
    onfmb_lines = []
    # Iterate through dssat models and point to correct shapefile
    for key in list(dm_area_shp_dict.keys()):
        onfmb_lines.append('\n\nnodal fluid mass balance from shp file\n{0}\nnfmb_dssat_id_{1}\n\n'.format(dm_area_shp_dict[key][1],key))
    return onfmb_lines


def Create_Daily_Coupled_Grok_File_Day_0(standalone_grok_lines,day,p,onfmb_lines):
    """Create coupled model HGS grok file for day 0 (no DSSAT inputs)

    Parameters:
    standalone_grok_lines (list): list of strings containing contents of grok file
    day (int): day of coupled model simulation for precipitation lookup
    p (list): list of daily p values from HGS
    onfmb_lines (list): list of strings containing contents of grok file nodal fluid mass balance for drainage calculation block

    Returns:
    new_lines (list): list of strings containing contents of new grok file
    
    """
    ## P Section
    # Get start index
    pstart = standalone_grok_lines.index('!!--Begin Precipitation Time Series Section--\n')
    # Get end index
    pend = standalone_grok_lines.index('!!--End Precipitation Time Series Section--\n')
    # Build P entry
    pentry = f'    time value table\n    0.0 {p[day]:.2f}\n    end\n'
    ## PET Section - this turns off the PET that was used in the standalone mode, because that will be provided by DSSAT now
    # Get start index
    petstart = standalone_grok_lines.index('!!--Begin PET Time Series Section--\n')
    # Get end index
    petend = standalone_grok_lines.index('!!--End PET Time Series Section--\n')
    ## Solute Transport IC Section
    # Get start index
    sticstart = standalone_grok_lines.index('!!--Begin Solute Transport Initial Concentration Section--\n')
    # Get end index
    sticend = standalone_grok_lines.index('!!--End Solute Transport Initial Concentration Section--\n')
    # # Build IC Entry
    # sticentry = ['! NH4 and NO3 boundary initial concentrations from DSSAT model in root zone and hgs in non-coupled zone\n\n!choose nodes all\n\n!initial concentration from file\n!iconc.txt\n\n']
    ## Output Section
    # Get start index
    ostart = standalone_grok_lines.index('!!--Begin Output Times Section--\n')
    # Get end index
    oend = standalone_grok_lines.index('!!--End Output Times Section--\n')
    new_lines = standalone_grok_lines[:pstart+1]+[pentry]+standalone_grok_lines[pend:petstart+1] + standalone_grok_lines[petend:sticstart+1] + standalone_grok_lines[sticend:ostart+1]+['1.0\nend\n']+standalone_grok_lines[oend:]+onfmb_lines
    return new_lines



def Create_Daily_Coupled_Grok_File_Day_N(standalone_grok_lines,day,p,nf_lines,onfmb_lines,model_name):
    """Create coupled model HGS grok file for day n (no DSSAT inputs)

    Parameters:
    standalone_grok_lines (list): list of strings containing contents of grok file
    day (int): day of coupled model simulation for precipitation lookup
    p (list): list of daily p values from HGS
    nf_lines (list): list of strings defining grok file lines for nodal flux ET forcing
    onfmb_lines (list): list of strings containing contents of grok file nodal fluid mass balance for drainage calculation block
    model_name (str): standalone hgs grok file name minus .grok

    Returns:
    new_lines (list): list of strings containing contents of new grok file
    
    """
    ## IC Section
    # Get start index
    icstart = standalone_grok_lines.index('!!--Begin Initial Head Section--\n')
    # Get end index
    icend = standalone_grok_lines.index('!!--End Initial Head Section--\n')
    # Build IC
    icentry = '! Set initial heads from day n-1\nchoose nodes all\n\ninitial head from output file\n{0}_day{1}o.head_pm.0001\n\nclear chosen nodes\n'.format(model_name,day-1)
    ## Flux Nodal Section
    # Get start index
    fnstart = standalone_grok_lines.index('!!--Begin Flux Nodal for DSSAT ET Section--\n')
    # Get end index
    fnend = standalone_grok_lines.index('!!--End Flux Nodal for DSSAT ET Section--\n')
    # Build FN
    fnentry = nf_lines
    ## P Section
    # Get start index
    pstart = standalone_grok_lines.index('!!--Begin Precipitation Time Series Section--\n')
    # Get end index
    pend = standalone_grok_lines.index('!!--End Precipitation Time Series Section--\n')
    # Build P entry
    pentry = f'    time value table\n    0.0 {p[day]:.2f}\n    end\n'
    ## PET Section - this turns off the PET that was used in the standalone mode, because that will be provided by DSSAT now
    # Get start index
    petstart = standalone_grok_lines.index('!!--Begin PET Time Series Section--\n')
    # Get end index
    petend = standalone_grok_lines.index('!!--End PET Time Series Section--\n')
    ## Solute Transport IC Section
    # Get start index
    sticstart = standalone_grok_lines.index('!!--Begin Solute Transport Initial Concentration Section--\n')
    # Get end index
    sticend = standalone_grok_lines.index('!!--End Solute Transport Initial Concentration Section--\n')
    # # Build IC Entry
    # sticentry = ['! NH4 and NO3 boundary initial concentrations from DSSAT model in root zone and hgs in non-coupled zone\n\n!choose nodes all\n\n!initial concentration from file\n!iconc.txt\n\n']
    ## Output Section
    # Get start index
    ostart = standalone_grok_lines.index('!!--Begin Output Times Section--\n')
    # Get end index
    oend = standalone_grok_lines.index('!!--End Output Times Section--\n')
    # Build O entry
    oentry = '1.0\nend\n'
    new_lines = standalone_grok_lines[:icstart+1]+[icentry]+standalone_grok_lines[icend:fnstart+1]+fnentry+standalone_grok_lines[fnend:pstart+1]+[pentry]+standalone_grok_lines[pend:petstart+1] + standalone_grok_lines[petend:sticstart+1]+standalone_grok_lines[sticend:ostart+1]+[oentry]+standalone_grok_lines[oend:]+onfmb_lines
    return new_lines



def Write_Coupled_Grok_File(new_lines,day,coupled_mod_hgs_dir,model_name):
    """Create coupled model HGS grok file for day n (no DSSAT inputs)

    Parameters:
    new_lines (list): list of strings containing contents of new grok file
    day (int): day of coupled model simulation for precipitation lookup
    coupled_mod_hgs_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to HGS
    model_name (str): standalone hgs grok file name minus .grok

    Returns:
    
    """
    new_grok_name = model_name + '_day{}'.format(day) + '.grok'
    new_grok_path = os.path.join(coupled_mod_hgs_dir,new_grok_name)
    with open(new_grok_path,'w') as file:
        for entry in new_lines:
            file.write(entry)


def Get_DSSAT_Model_Files(dssat_mod_dir,coupled_mod_dssat_dir,dm_area_shp_dict):
    """Copy model files from DSSAT into each DSSAT zone model firectory

    Parameters:
    dssat_mod_dir (str): path to subdirectory containing standalone DSSAT model
    coupled_mod_dssat_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to DSSAT
    dm_area_shp_dict (dict): dictionary detailing area and shapefile path for each DSSAT model's associated nodal control volume

    Returns:
    
   """
    ## Make DSSAT zone model directory
    # Get all DSSAT Zone ID Values
    ID_Vals = list(dm_area_shp_dict.keys())
    # Iterate to make directories and copy files
    for id in ID_Vals:
        # Make zone subdirectory
        zone_dir = os.path.join(coupled_mod_dssat_dir,str(id))
        try:
            os.mkdir(zone_dir)
        except:
            print(zone_dir + ' already exists')
        # Copy in necessary DSSAT files
        for file in os.listdir(dssat_mod_dir):
            print(file)
            if ('.' in file) & (not ('.OUT' in file)):
                print(file)
                copy(os.path.join(dssat_mod_dir,file),os.path.join(zone_dir,file))
        # Make data directory to store coupling data
        zone_data_dir = os.path.join(zone_dir,'data')
        try:
            os.mkdir(zone_data_dir)
        except:
            print(zone_data_dir + ' already exists')


def Build_Coupled_Model_Files(mod_dir,model_name,coupled_model_name,hgs_mod_dir,dssat_mod_dir,hnsdb_dict,dm_area_shp_dict):
    """Create coupled model daily HGS grok files

    Parameters:
    mod_dir (str): path to parent directory named after model containing standalone HGS and DSSAT models
    model_name (str): standalone hgs grok file name minus .grok
    coupled_model_name (str): name under which to store all coupled model files
    hgs_mod_dir (str): path to standalone hgs model
    dssat_mod_dir (str): path to standalone dssat model
    hnsdb_dict (dict): maps HGS node sheets to DSSAT borders
    dm_area_shp_dict (dict): dictionary detailing area and shapefile path for each DSSAT model's associated nodal control volume

    Returns:
    coupled_mod_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files
    coupled_mod_hgs_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to HGS
    coupled_mod_dssat_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to DSSAT
    coupled_mod_mapping_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to mapping
    
    """
    ## Build Coupled Model
    # Create Directory Structure
    coupled_mod_dir,coupled_mod_hgs_dir,coupled_mod_dssat_dir,coupled_mod_mapping_dir = Create_Coupled_Model_Dir(mod_dir,coupled_model_name)
    # Get grok file path
    grok_file_path = os.path.join(hgs_mod_dir,model_name + '.grok')
    # Copy over necessary hgs files
    Get_HGS_Props_Files(hgs_mod_dir,coupled_mod_hgs_dir,model_name)
    Get_NFMB_Shapefile(hgs_mod_dir,coupled_mod_hgs_dir)
    # Copy over DSSAT model into zone directories
    Get_DSSAT_Model_Files(dssat_mod_dir,coupled_mod_dssat_dir,dm_area_shp_dict)
    # Get standalone model grok lines and Prec series
    standalone_grok_lines = Get_Standalone_Grok_Lines(grok_file_path)
    P, End_Day = Get_Standalone_Grok_Prec_Series(standalone_grok_lines)
    # Get blocks of new grok lines for coupled model
    nf_lines = CreateETNodalFluxBlock(hnsdb_dict)
    onfmb_lines = CreateNFMBOutputBlock(dm_area_shp_dict)
    # Iterate through days to build daily hgs models
    for day in arange(0,End_Day):
        # Day 0 model
        if day == 0:
            # Build text lines
            new_lines = Create_Daily_Coupled_Grok_File_Day_0(standalone_grok_lines,day,P,onfmb_lines)
            # Write out
            Write_Coupled_Grok_File(new_lines,day,coupled_mod_hgs_dir,model_name)
        # All other Day models
        else:
            # Build text lines
            new_lines = Create_Daily_Coupled_Grok_File_Day_N(standalone_grok_lines,day,P,nf_lines,onfmb_lines,model_name)
            # Write out
            Write_Coupled_Grok_File(new_lines,day,coupled_mod_hgs_dir,model_name)
    return coupled_mod_dir,coupled_mod_hgs_dir,coupled_mod_dssat_dir,coupled_mod_mapping_dir