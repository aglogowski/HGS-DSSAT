
def CreatePlanviewMapping(hgs_nodes_shp_path,dssat_models_shp_path):
    import geopandas as gpd
    # Load both shape files
    hgs_gdf = gpd.read_file(hgs_nodes_shp_path)
    dssat_gdf = gpd.read_file(dssat_models_shp_path)
    # Perform spatial join to combine attributes
    merged = hgs_gdf.sjoin(dssat_gdf, how = 'left', predicate = 'intersects').loc[:,['Node','DSSAT_ID']]
    ## Create Mapping Dictionary
    hd_dict = dict(zip(merged['Node'], merged['DSSAT_ID']))
    return hd_dict

def CreateHGSNodesShape(hgs_nodes_xyz_path):
    import pandas as pd
    import geopandas as gpd
    # Load xyz file
    df = pd.read_csv(hgs_nodes_xyz_path, header = None, names = ['Node','X','Y','Z'], sep = '\s+')
    # Create point geometry column
    df['geometry'] = df.apply(lambda x: Point(x['X'],x['Y']), axis = 1)
    # Export as shapefile
    gdf = gpd.GeoDataFrame(data = df, geometry = 'geometry')
    gdf.to_file(hgs_nodes_xyz_path[:-4]+'.shp')

def SaveMapping(hd_dict,mapping_pkl_path):
    import pickle as pkl
    # Pickle mapping dictionary
    with open(mapping_pkl_path,'wb') as file:
        pkl.dump(hd_dict,file)