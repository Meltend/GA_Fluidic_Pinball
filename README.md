# GPC_Fluidic_Pinball
Application of Genetic Programming Control of the fluidic pinball. 

The contents of the main branch are in 2 Separate folders named icoFoam_fluidic_pinball & Genetic Algorithms. 


In icoFoam_fluidic_pinball there is OpenFOAM files which include 0,cgonstant and system files. 0 files outline the pressure and velocity boundary conditions. Constant includes the created mesh via polyMesh. System incldues the time step,solver and discreteisation schemes.

The Genetic Algorithms contains two python scripts with .py extensions. One is used to complete the offline training via Genetic Algorithms and has a run time of 10 hours with 10 cores i7 16GB ram system while the second code runs one simulations and provides visualisation tools for understanding the flow control and the effect of Vortex Shedding.

This code is free to use.
