FROM ubuntu
RUN apt-get -y update
RUN apt-get -y install python2.7 gcc gfortran g++ make python-pip wget gnuplot bc cmake rsync
RUN pip install numpy scipy
RUN mkdir /code
WORKDIR /code
RUN wget "http://lcgapp.cern.ch/project/simu/HepMC/download/HepMC-2.06.09.tar.gz"; tar -xzf HepMC-2.06.09.tar.gz; 
RUN mkdir hepmc2; 
ARG PYTHIA_VERSION="8240"
RUN echo "PYTHIA version is ${PYTHIA_VERSION}"
RUN wget "http://home.thep.lu.se/~torbjorn/pythia8/pythia${PYTHIA_VERSION}.tgz"; tar -xzf pythia${PYTHIA_VERSION}.tgz; rm pythia${PYTHIA_VERSION}.tgz; mv pythia${PYTHIA_VERSION} pythia8
RUN cd pythia8; ./configure --with-hepmc2=/code/PYTHIA/HEPTools/hepmc --with-lhapdf6=/code/PYTHIA/HEPTools/lhapdf6 --with-boost=/code/PYTHIA/HEPTools/boost; make;
RUN cd pythia8/examples; make main42
ADD steer_pythia.py .