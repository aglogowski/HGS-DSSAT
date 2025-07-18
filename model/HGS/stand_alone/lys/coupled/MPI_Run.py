import os
from mpi4py import MPI
from pyHGSDSSAT import CoupledRun as cr
import numpy as np

def main():
    # variables
    mod_dir = os.path.dirname(os.getcwd())
    coupled_mod_dir = os.getcwd()
    coupled_mod_hgs_dir = os.path.join(coupled_mod_dir,'hgs')
    coupled_mod_dssat_dir = os.path.join(coupled_mod_dir,'dssat')
    hgs_mod_dir = os.path.join(mod_dir,'hgs')
    model_name = 'lys'
    grok_file_stem = model_name + '_e'
    mapping_dir = os.path.join(mod_dir,'mapping')
    mapping_pkl_path = os.path.join(mapping_dir,'lys_mapping.p')
    rz_node_order_file_path = os.path.join(hgs_mod_dir,'rz_node_order.txt')
    full_node_order_file_path = os.path.join(hgs_mod_dir,'full_node_order.txt')

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    # Iterate through days to run daily hgs models
    for day in np.arange(0,5):
        print('Starting Day {}'.format(day))
        if rank == 0:
            # Process 1: HGS call
            print('Running HGS for Day {}'.format(day))
            cr.HGS_Daily_Loop(day,mapping_pkl_path,rz_node_order_file_path,full_node_order_file_path,grok_file_stem,coupled_mod_dir,coupled_mod_hgs_dir,coupled_mod_dssat_dir)
            print("HGS for Day {} completed".format(day))

            # Signal Process 2 to start
            comm.send(None, dest=1, tag=0)

            # Wait for Process 2 to finish
            comm.recv(source=1, tag=1)
            print("Process 1: Both models completed for Day {}. Exiting.".format(day))

        elif rank == 1:
            # Wait for Process 1 to complete
            comm.recv(source=0, tag=0)

            # Process 2: Call function
            print('Running DSSAT for Day {}'.format(day))
            cr.Dummy_DSSAT_1Day_Run()
            print('Completed DSSAT simulation for Day {}'.format(day))
            # Signal Process 1 that Process 2 is done
            comm.send(None, dest=0, tag=1)


# This allows execution when running the module directly
if __name__ == "__main__":
    main()