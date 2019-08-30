FROM ubuntu
RUN apt-get -y update
RUN apt-get -y install python2.7 gcc gfortran g++ make python-pip wget gnuplot bc cmake rsync
RUN pip install numpy scipy
RUN mkdir /code
WORKDIR /code
RUN wget "http://lcgapp.cern.ch/project/simu/HepMC/download/HepMC-2.06.09.tar.gz"; tar -xzf HepMC-2.06.09.tar.gz; 
RUN mkdir hepmc2; 
ARG pythia_version="8240"
RUN echo "PYTHIA version is ${pythia_version}"
RUN wget "http://home.thep.lu.se/~torbjorn/pythia8/pythia${pythia_version}.tgz"; tar -xzf pythia${pythia_version}.tgz; rm pythia${pythia_version}.tgz; mv pythia${pythia_version} pythia8
RUN cd pythia8; ./configure --with-hepmc2=/code/PYTHIA/HEPTools/hepmc --with-lhapdf6=/code/PYTHIA/HEPTools/lhapdf6 --with-boost=/code/PYTHIA/HEPTools/boost; make;
RUN cd pythia8/examples; make main42
ADD steer_pythia.py .