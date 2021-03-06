from SystemSetup import *
import numpy as np
from optparse import OptionParser
import os
'''
SetupStage5_ZCon:
    Z-Constrained molecular dynamics, recording restraining forces
    Tracers should be at different z-windows and well-equilibrated
    Define another pulling potential around that z-window
    Run time is same across all simulation
    Do this N_window/N_tracer times for each z-window
    Will need to re-grompp with new top, mdp, gro files

'''


#Read in tracers
parser = OptionParser()
parser.add_option('--t', action = 'store', type = 'string', dest = 'tracerfile', default = 'tracers.out')
parser.add_option('--z', action = 'store', type = 'string', dest = 'zwindows', default  = 'z_windows.out')
#parser.add_option('--gro', action = 'store', type = 'string', dest = 'grofile', default = 'pureDSPC.gro')
#parser.add_option('--top', action = 'store', type = 'string', dest = 'topfile', default = 'RedonepureDSPC.top')
parser.add_option('--k', action = 'store', type = 'float', dest = 'pull_coord_k', default = '500')
#parser.add_option('--r', action = 'store', type = 'float', dest = 'pull_coord_rate', default = '0.00005') #0.05nm/ns = 0.05e-3 nm/ps
(options, args) = parser.parse_args()

thing = SystemSetup()
tracerlist_filename = options.tracerfile
zwindows_filename = options.zwindows
#topfile = options.topfile
pull_coord_k = options.pull_coord_k
pull_coord_rate = 0
indexfile = 'FullIndex.ndx'
duration = 2e3 # Run z-constraining and record forces for 2 ns

#Read tracers
tracerlist = open(tracerlist_filename, 'r')
tracerlistlines = tracerlist.readlines()
thing.read_tracers(tracerlistlines)
N_tracer = len(tracerlistlines)


#Read zwindows
zwindows = open(zwindows_filename, 'r')
zwindowslines = zwindows.readlines()
thing.read_zlist(zwindowslines)
N_window = len(zwindowslines)

N_sims = int(N_window / N_tracer)
dz = np.round(float(thing.get_dz()), 3)
z0 = np.round(float(thing.get_z0()), 3)

print('Setup Stage 5 ZConstraining: Z-Constrained MD')
print('{:10s} = {}'.format('dz', dz))
print('{:10s} = {}'.format('z0', z0))
print('{:10s} = {}'.format('N_window', N_window))
print('{:10s} = {}'.format('N_tracer', N_tracer))
print('{:10s} = {}'.format('Tracerfile', tracerlist_filename))
print('{:10s} = {}'.format('Zwindows', zwindows_filename))
#print('{:10s} = {}'.format('Topfile', topfile))
#print('{:10s} = {}'.format('k', pull_coord_k))


#tracer_list = thing.get_Tracers()
tracer_list = thing.tracer_list
z_list = z0*np.ones(len(tracer_list))
#With references, each tracer will be moving to a different location, unlike stages 1 and 2
#Need to modify z_list to account for each tracer hitting different zwindows now
z_sep = dz*N_window/N_tracer
for i in range(len(z_list)):
    z_list[i] = z_list[i] + (z_sep*i)

#Need to write position restraint file for mdp file

for i in range(N_sims):
    #print('Writing mdp and submit files for k = {} pulling to z = {}'.format(pull_coord_k, np.round(z_list[0],2)))
    print('Z_windows: {}'.format(z_list))
    directoryname = 'Sim{}'.format(str(i))
    mdpfile = str('Stage5_ZCon' + str(i) + '.mdp')
    filename = str('Stage5_ZCon' + str(i))
    oldfilename = str('Stage4_Eq' + str(i))
    #posres = 'POSRES'
    cptfile = (oldfilename + '.cpt')
    oldtpr = (oldfilename + '.tpr')
    grofile = (directoryname + '/' + oldfilename+'.gro')
    #thing.write_posres(directoryname, posres, tracer_list, grofile)
    #thing.add_posres(directoryname, topfile, posres, grofile, tracer_list)
    curr_dir_grofile = (oldfilename+'.gro')
    thing.write_pulling_mdp(directoryname + '/' + 'Stage5_ZCon'+str(i)+'.mdp', tracer_list, z_list, grofile, pull_coord_rate =
            pull_coord_rate, pull_coord_k = pull_coord_k, t_pulling = duration, stagefive = True)
    #thing.write_posres(directoryname, posres, tracer_list, grofile)
    #thing.add_posres(directoryname, topfile, posres, grofile, tracer_list)

    thing.write_slurm_stage2(directoryname, filename, mdpfile, grofile, oldfilename)
    thing.write_grompp_file(directoryname, filename, grofile, mdpfile, indexfile, oldtpr=oldtpr, cptfile=cptfile)
    #thing.write_grompp_file(directoryname, filename, curr_dir_grofile, mdpfile, indexfile, topfile=topfile, posres=posres) 

    z_list += dz

#for i in range(0, N_sims, 2):
#    directoryname1 = 'Sim{}'.format(str(i))
#    directoryname2 = 'Sim{}'.format(str(i+1))
#
#
#    mdpfile1 = str(directoryname1 + '/' + 'Stage2_Strong' + str(i) + '.mdp')
#    mdpfile2 = str(directoryname2 + '/' + 'Stage2_Strong' + str(i+1) + '.mdp')
#    pbsname = 'Stage2_Strong{}and{}'.format(str(i), str(i+1))
#
#    oldfilename1 = str(directoryname1 + '/' + 'Stage1_Weak' + str(i))
#    oldfilename2 = str(directoryname2 + '/' + 'Stage1_Weak' + str(i+1))
#    if i == N_sims - 1:
#        pbsname = 'Stage2_Strong{}'.format(str(i))
#        thing.write_pbs_single_stage2(pbsname, oldfilename1,  directoryname1, mdpfile1)
#    else:
#        thing.write_pbs_stage2(pbsname, oldfilename1, directoryname1, mdpfile1, oldfilename2, directoryname2, mdpfile2)
#


