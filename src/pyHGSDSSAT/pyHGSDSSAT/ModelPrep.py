import os
from shutil import copy
from numpy import arange



def Create_Coupled_Model_Dir(mod_dir):
    """Create a directory for a coupled HGS-DSSAT model run

    Parameters:
    mod_dir (str): path to parent directory named after model containing standalone HGS and DSSAT models
    
    Returns:
    coupled_mod_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files
    coupled_mod_hgs_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to HGS
    coupled_mod_dssat_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to DSSAT

   """
    # Create directories if they don't exist
    coupled_mod_dir = os.path.join(mod_dir,'coupled')
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
    return coupled_mod_dir,coupled_mod_hgs_dir,coupled_mod_dssat_dir



def Get_Spin_Up_Heads_Output_File(hgs_mod_dir,coupled_mod_hgs_dir,grok_file_stem):
    """Copy spin-up heads output file from HGS

    Parameters:
    hgs_mod_dir (str): path to subdirectory containing standalone HGS model
    coupled_mod_hgs_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to HGS
    grok_file_stem (str): standalone hgs grok file name minus file extension

    Returns:
    
   """
    # Identify spin up grok name
    heads_file_stem = grok_file_stem.split('_')[0] + '_suo.head_pm'
    # Get highest number head_pm output file
    heads_file = [x for x in os.listdir(hgs_mod_dir) if heads_file_stem in x][-1]
    # Get path of that file
    spin_up_heads_file_path = os.path.join(hgs_mod_dir,heads_file)
    # Get path of coupled model hgs dir
    coupled_spin_up_heads_file_path = os.path.join(coupled_mod_hgs_dir,heads_file)
    # Copy file
    copy(spin_up_heads_file_path,coupled_spin_up_heads_file_path)



def Get_HGS_Props_Files(hgs_mod_dir,coupled_mod_hgs_dir,grok_file_stem):
    """Copy props files from HGS

    Parameters:
    hgs_mod_dir (str): path to subdirectory containing standalone HGS model
    coupled_mod_hgs_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to HGS
    grok_file_stem (str): standalone hgs grok file name minus file extension

    Returns:
    
   """
    # Get model name
    model_name = grok_file_stem.split('_')[0]
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



def Create_Daily_Coupled_Grok_File_Day_0(standalone_grok_lines,day,p):
    """Create coupled model HGS grok file for day 0 (no DSSAT inputs)

    Parameters:
    standalone_grok_lines (list): list of strings containing contents of grok file
    day (int): day of coupled model simulation for precipitation lookup
    p (list): list of daily p values from HGS

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
    ## Output Section
    # Get start index
    ostart = standalone_grok_lines.index('!!--Begin Output Times Section--\n')
    # Get end index
    oend = standalone_grok_lines.index('!!--End Output Times Section--\n')
    new_lines = standalone_grok_lines[:pstart+1]+[pentry]+standalone_grok_lines[pend:ostart+1]+['1.0\nend\n']+standalone_grok_lines[oend:]
    return new_lines



def Create_Daily_Coupled_Grok_File_Day_N(standalone_grok_lines,day,p,grok_file_stem):
    """Create coupled model HGS grok file for day n (no DSSAT inputs)

    Parameters:
    standalone_grok_lines (list): list of strings containing contents of grok file
    day (int): day of coupled model simulation for precipitation lookup
    p (list): list of daily p values from HGS
    grok_file_stem (str): standalone hgs grok file name minus file extension

    Returns:
    new_lines (list): list of strings containing contents of new grok file
    
    """
    ## IC Section
    # Get start index
    icstart = standalone_grok_lines.index('!!--Begin Initial Head Section--\n')
    # Get end index
    icend = standalone_grok_lines.index('!!--End Initial Head Section--\n')
    # Build IC
    icentry = '! Set initial heads from day n-1\nchoose nodes all\n\ninitial head from output file\n{0}day{1}o.head_pm.0001\n\nclear chosen nodes\n'.format(grok_file_stem,day-1)
    ## Flux Nodal Section
    # Get start index
    fnstart = standalone_grok_lines.index('!!--Begin Flux Nodal for DSSAT ET Section--\n')
    # Get end index
    fnend = standalone_grok_lines.index('!!--End Flux Nodal for DSSAT ET Section--\n')
    # Build FN
    fnentry = '! Set flux nodal to force DSSAT ET\nboundary condition\n    type\n    flux nodal\n\n    node set\n    coupled_section\n\n    time file table\n    0.0 nflux.txt\n    0.00069444 none\n    end\nend\n'
    ## P Section
    # Get start index
    pstart = standalone_grok_lines.index('!!--Begin Precipitation Time Series Section--\n')
    # Get end index
    pend = standalone_grok_lines.index('!!--End Precipitation Time Series Section--\n')
    # Build P entry
    pentry = f'    time value table\n    0.0 {p[day]:.2f}\n    end\n'
    ## Solute Transport IC Section
    # Get start index
    sticstart = standalone_grok_lines.index('!!--Begin Solute Transport Initial Concentration Section--\n')
    # Get end index
    sticend = standalone_grok_lines.index('!!--End Solute Transport Initial Concentration Section--\n')
    # Build IC Entry
    sticentry = ['! NH4 and NO3 boundary initial concentrations from DSSAT model in root zone and hgs in non-coupled zone\n\n!choose nodes all\n\n!initial concentration from file\n!iconc.txt\n\n']
    ## Output Section
    # Get start index
    ostart = standalone_grok_lines.index('!!--Begin Output Times Section--\n')
    # Get end index
    oend = standalone_grok_lines.index('!!--End Output Times Section--\n')
    new_lines = standalone_grok_lines[:icstart+1]+[icentry]+standalone_grok_lines[icend:fnstart+1]+[fnentry]+standalone_grok_lines[fnend:pstart+1]+[pentry]+standalone_grok_lines[pend:sticstart+1]+sticentry+standalone_grok_lines[sticend:ostart+1]+['1.0\nend\n']+standalone_grok_lines[oend:]
    return new_lines



def Write_Coupled_Grok_File(new_lines,day,coupled_mod_hgs_dir,grok_file_stem):
    """Create coupled model HGS grok file for day n (no DSSAT inputs)

    Parameters:
    new_lines (list): list of strings containing contents of new grok file
    day (int): day of coupled model simulation for precipitation lookup
    coupled_mod_hgs_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to HGS
    grok_file_stem (str): standalone hgs grok file name minus file extension

    Returns:
    
    """
    new_grok_name = grok_file_stem + 'day{}'.format(day) + '.grok'
    new_grok_path = os.path.join(coupled_mod_hgs_dir,new_grok_name)
    with open(new_grok_path,'w') as file:
        for entry in new_lines:
            file.write(entry)



def Build_Coupled_Model_Files(mod_dir,grok_file_stem):
    """Create coupled model daily HGS grok files

    Parameters:
    mod_dir (str): path to parent directory named after model containing standalone HGS and DSSAT models
    grok_file_stem (str): standalone hgs grok file name minus file extension

    Returns:
    
    """
    ## Build Coupled Model
    # Create Directory Structure
    coupled_mod_dir,coupled_mod_hgs_dir,coupled_mod_dssat_dir = Create_Coupled_Model_Dir(mod_dir)
    # Get HGS standalone model dir
    hgs_mod_dir = os.path.join(mod_dir,'hgs')
    # Get grok file path
    grok_file_path = os.path.join(hgs_mod_dir,grok_file_stem + '.grok')
    # Copy over necessary hgs files
    Get_Spin_Up_Heads_Output_File(hgs_mod_dir,coupled_mod_hgs_dir,grok_file_stem)
    Get_HGS_Props_Files(hgs_mod_dir,coupled_mod_hgs_dir,grok_file_stem)
    Get_NFMB_Shapefile(hgs_mod_dir,coupled_mod_hgs_dir)
    # Get standalone model grok lines and Prec series
    standalone_grok_lines = Get_Standalone_Grok_Lines(grok_file_path)
    P, End_Day = Get_Standalone_Grok_Prec_Series(standalone_grok_lines)
    # Iterate through days to build daily hgs models
    for day in arange(0,End_Day):
        # Day 0 model
        if day == 0:
            # Build text lines
            new_lines = Create_Daily_Coupled_Grok_File_Day_0(standalone_grok_lines,day,P)
            # Write out
            Write_Coupled_Grok_File(new_lines,day,coupled_mod_hgs_dir,grok_file_stem)
        # All other Day models
        else:
            # Build text lines
            new_lines = Create_Daily_Coupled_Grok_File_Day_N(standalone_grok_lines,day,P,grok_file_stem)
            # Write out
            Write_Coupled_Grok_File(new_lines,day,coupled_mod_hgs_dir,grok_file_stem)