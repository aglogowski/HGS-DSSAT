import pandas as pd
import geopandas as gpd
from shapely import Point,Polygon
import pickle as pkl
import numpy as np
import os

def GenerateMappingShapefiles(hgs_mod_dir,coupled_mod_mapping_dir,model_name):
    """Generate Shapefile of HGS nodes and control volumes to assist in mapping process used to link DSSAT models to HGS zones.

    Parameters:
    hgs_mod_dir (str): path to subdirectory containing stand alone  HGS model files 
    coupled_mod_mapping_dir (str): path to subdirectory containing all coupled HGS-DSSAT model files that relate to mapping
    model_name (str): standalone hgs grok file name minus .grok

    Returns:
    node_shapefile_path (str): path to shapefile of HGS nodes
    all_cv_shapefile_path (str): path to shapefile of HGS nodal control volumes
    
    """
    # Look in grok file for gen interactive layers section
    # Get grok file path
    grok_file_path = os.path.join(hgs_mod_dir,model_name + '.grok')
    # Read grok file
    with open(grok_file_path,'r') as file_in:
        lines = file_in.readlines()
    # Find index of mesh generation section start
    ind = lines.index('    generate variable rectangles\n')
    # Iterate to find number of x dimensions
    i = ind
    x_dim = 0
    while x_dim == 0:
        i+=1
        if len(lines[i].strip()) > 0:
            # Remove whitespace and split by space to remove comments after value
            x_dim = int(lines[i].strip().split(' ')[0])
    print('x dim is ' + str(x_dim))
    # Iterate to populate node x coordinates
    node_xs = []
    for i in range(i+1,i+1+x_dim):
        node_xs.append(float(lines[i].strip()))
    print(node_xs)
    # Iterate to find number of y dimensions
    ind = i+x_dim+2
    y_dim = 0
    while y_dim == 0:
        i+=1
        if len(lines[i].strip()) > 0:
            # Remove whitespace and split by space to remove comments after value
            y_dim = int(lines[i].strip().split(' ')[0])
    print('y dim is ' + str(y_dim))
    # Iterate to populate node y coordinates
    node_ys = []
    for i in range(i+1,i+1+y_dim):
        node_ys.append(float(lines[i].strip()))
    print(node_ys)
    # Make shapefile of nodes with geopandas
    coords = []
    node_id = []
    dssat_id = []
    for j,y in enumerate(node_ys):
        for i,x in enumerate(node_xs):
            node_id.append((i+1) + ((j)*3))
            coords.append(Point([x,y]))
            dssat_id.append(1) # CHANGE TO KEEP THIS FIELD BLANK
    df = pd.DataFrame.from_dict(data = {'node_id':node_id,'dssat_id':dssat_id,'geometry':coords})
    gdf = gpd.GeoDataFrame(df, geometry = 'geometry')
    node_shapefile_path = os.path.join(coupled_mod_mapping_dir,'model_2d_nodes.shp')
    gdf.to_file(node_shapefile_path)
    # Make shapefile of control volumes
    coords = []
    node_id = []
    dssat_id = []
    area = []
    x_st_ind = 0
    x_end_ind = len(node_xs)-1
    y_st_ind = 0
    y_end_ind = len(node_ys)-1
    for j,y in enumerate(node_ys):
        for i,x in enumerate(node_xs):
            # print(i,j)
            x1 = 0
            x2 = 0
            y1 = 0
            y2 = 0
            # Get x1
            if i == x_st_ind:
                x1 = node_xs[0]
            else:
                x1 = (node_xs[i] + node_xs[i-1])/(2)
            # Get x2
            if i == x_end_ind:
                x2 = node_xs[-1]
            else:
                x2 = (node_xs[i+1] + node_xs[i])/(2)
            # Get y1
            if j == y_st_ind:
                y1 = node_ys[0]
            else:
                y1 = (node_ys[j] + node_ys[j-1])/(2)
            # Get y2
            if j == y_end_ind:
                y2 = node_ys[-1]
            else:
                y2 = (node_ys[j+1] + node_ys[j])/(2)
            # print(x1,x2,y1,y2)
            poly = Polygon([(x1,y1),(x1,y2,),(x2,y2,),(x2,y1),(x1,y1)])
            coords.append(poly)
            node_id.append((i+1) + ((j)*3))
            dssat_id.append(1) # CHANGE TO KEEP THIS FIELD BLANK
            area.append(poly.area)
    df = pd.DataFrame.from_dict(data = {'node_id':node_id,'dssat_id':dssat_id,'geometry':coords,'area':area})
    gdf = gpd.GeoDataFrame(df, geometry = 'geometry')
    all_cv_shapefile_path = os.path.join(coupled_mod_mapping_dir,'model_2d_cvs.shp')
    gdf.to_file(all_cv_shapefile_path)
    return node_shapefile_path,all_cv_shapefile_path

def DevelopVerticalMapping(dssat_layers,hgs_layers):
    """Develop dictionaries defining the vertical mapping used to link the coupled zone in HGS and DSSAT

    Parameters:
    dssat_layers (int): number of layers in standalone dssat model
    hgs_layers (int): number of layers in standalone hgs model


    Returns:
    dlhl_dict (dict): maps DSSAT layers to HGS layers
    hldl_dict (dict): maps HGS layers to DSSAT layers
    hnsdb_dict (dict): maps HGS node sheets to DSSAT borders
    dlhnsud_dict (dict): maps DSSAT layers to HGS up and down node sheets
    
    """
    # Map DSSAT Layers to HGS Layers 
    dlhl_dict = {}
    hldl_dict = {}
    for i in range(dssat_layers):
        # back to 1-based
        i += 1
        # HGS Layer numbering in reverse order
        j = hgs_layers - (i - 1)
        dlhl_dict[i] = j
        hldl_dict[j] = i
    # Map HGS Node Sheets to DSSAT Borders
    hnsdb_dict = {}
    # One more border than there are layers
    dssat_bords = dssat_layers + 1
    for i in range(dssat_bords):
        # back to 1-based
        i += 1
        # HGS Node Sheet numbering in reverse order. One more node sheet than there are layers
        j = (hgs_layers + 1) - (i-1)
        hnsdb_dict[j] = i
    # Map DSSAT Layers to HGS Up and Down Node Sheets
    dlhnsud_dict = {}
    for i in range(dssat_layers):
        # back to 1-based
        i += 1
        # HGS Node sheet numbering in reverse order. One more node sheet than there are layers
        j_up = (hgs_layers + 1) - (i-1)
        j_dn = (hgs_layers + 1) - (i)
        dlhnsud_dict[i] = [j_up,j_dn]
    return dlhl_dict,hldl_dict,hnsdb_dict,dlhnsud_dict
    
def DevelopHorizontalMapping(all_cv_shapefile_path,coupled_mod_mapping_dir):
    """Develop dictionaries and shapefiles defining the horizontal mapping of HGS areas onto individual DSSAT models

    Parameters:
    all_cv_shapefile_path (str): path to shapefile of HGS nodal control volumes
    coupled_mod_mapping_dir (str): 

    Returns:
    hncvdm_dict (dict): dictionary defining horizontal mapping of HGS node numbers (CV #'s) to DSSAT models
    dm_area_shp_dict (dict): dictionary detailing area and shapefile path for each DSSAT model's associated nodal control volume
    
    
    """
    # Load cv shapefile
    all_cv = gpd.read_file(all_cv_shapefile_path)
    print(all_cv)
    # Develop horizontal dictionary that maps HGS node cv numbers to DSSAT models and includes area information
    hncvdm_dict = {}
    for entry in all_cv['node_id'].values:
        hncvdm_dict[entry] = [all_cv.loc[all_cv['node_id'] == entry,'dssat_id'].values[0],all_cv.loc[all_cv['node_id'] == entry,'area'].values[0]]
    # Create individual shapefiles of the area of nodal control volumes used for each dssat model and store areas and shapefile paths in a dictionary
    dm_area_shp_dict = {}
    for id_val in all_cv['dssat_id'].unique():
        cv = all_cv.loc[all_cv['dssat_id'] == id_val,:]
        cv = cv.dissolve(by = 'dssat_id', aggfunc = {'node_id':'first',
                                                     'area':'sum'})
        cv_shapefile_path = os.path.join(coupled_mod_mapping_dir,'cv_dssatmod_{}.shp'.format(id_val))
        dm_area_shp_dict[id_val] = [cv['area'].values[0],cv_shapefile_path]
        cv.to_file(cv_shapefile_path)
    return hncvdm_dict,dm_area_shp_dict

def GenerateMappingPickle(coupled_model_mapping_dir,dlhl_dict,hldl_dict,hnsdb_dict,dlhnsud_dict,hncvdm_dict,dm_area_shp_dict):
    """Bundle all mapping outputs and pickle them in mapping directory for model controller to use

    Parameters:
    dlhl_dict (dict): maps DSSAT layers to HGS layers
    hldl_dict (dict): maps HGS layers to DSSAT layers
    hnsdb_dict (dict): maps HGS node sheets to DSSAT borders
    dlhnsud_dict (dict): maps DSSAT layers to HGS up and down node sheets
    hncvdm_dict (dict): dictionary defining horizontal mapping of HGS node numbers (CV #'s) to DSSAT models
    dm_area_shp_dict (dict): dictionary detailing area and shapefile path for each DSSAT model's associated nodal control volume


    Returns:
    
    
    """
    # Pickle Path
    pickle_path = os.path.join(coupled_model_mapping_dir,'mapping_pkl.p')
    # Create dictionary
    mapping = {}
    mapping['dlhl'] = dlhl_dict
    mapping['hldl'] = hldl_dict
    mapping['hnsdb'] = hnsdb_dict
    mapping['dlhnsud'] = dlhnsud_dict
    mapping['hncvdm'] = hncvdm_dict
    mapping['dm_area_shp'] = dm_area_shp_dict
    with open(pickle_path,'wb') as file:
        pkl.dump(mapping,file)