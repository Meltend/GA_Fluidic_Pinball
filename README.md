# GA_Fluidic_Pinball
Application of Genetic Algorithms(GA) for the control of the fluidic pinball. 

The contents of the main branch are in 3 Separate folders named icoFoam_fluidic_pinball, Genetic Algorithms and Visualisation tools. 


In icoFoam_fluidic_pinball there is OpenFOAM files which include 0,cgonstant and system files. 0 files outline the pressure and velocity boundary conditions. Constant includes the created mesh via polyMesh. System incldues the time step,solver and discreteisation schemes.

The Genetic Algorithms contains two python scripts with .py extensions. One is used to complete the offline training via Genetic Algorithms and has a run time of 7 hours with 10 cores i7 16GB ram system while the second code runs one simulations and provides visualisation tools for understanding the flow control and the effect of Vortex Shedding.

The visualisation tool are .m files as they are produced in Matlab. 

This code is free to use.

Note: This code will only work on Windows version 10 and above. It is required to install Ubuntu and WSL as well as ParaView Windows version.
This is the first version of the code therefore not yet optimised to work on all systems so please raise any errors.
