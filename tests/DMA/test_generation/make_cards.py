#!/usr/bin/env python

import sys
import argparse
import os
import itertools


def quit(p):
    p.print_help()
    sys.exit()


def swCalc(type, gQ, gL, gDM, mMed, mDM):
    ''' 
        Calculates the total width for s-channel mediated dark matter:
        q              dark matter
         \\   med.   //
           ========== 
         //          \\
        q              dark matter
        Gamma_min = Gamma_DM + sum_q Gamma_qq

        type: indicates type of the mediator (scalar, pseudo, vector, axial)
        gQ: coupling of mediator to quarks
        gL: coupling of mediator to charged leptons (neutrino coupling fixed by gauge invariance)
        gDM: coupling of mediator to dark matter
        mMed: mass of mediator in GeV
        mDM: mass of dark matter in GeV
    '''

    import sys
    import math as m

    # Partial width has the form: normFactor * ratioFunc * betaFact

    # Quark Partial Width Calculation. Calculate for each quark in list.
    normFactorQQ = 1.
    vev = 246.
    betaExp = 0.
    # http://pdg.lbl.gov/2014/tables/rpp2014-sum-quarks.pdf
    quarkName = ['u', 'd', 'c', 's', 't', 'b']
    quarkMass = [2.3e-3, 4.8e-3, 1.275, 9.5e-2, 173.21, 4.66]  # in GeV
    ratioFuncQQ, betaQQ = list(), list()  # lists containing entry for each quark
    if type == 'vector' or type == 'axial':
        normFactorQQ = (3. * gQ**2 * mMed)/(12. * m.pi)
        if type == 'vector':
            betaExp = 0.5
            ratioFuncQQ = [(1. + (2. * mass**2)/mMed**2) for mass in quarkMass]
        elif type == 'axial':
            betaExp = 1.5
            ratioFuncQQ = [1. for mass in quarkMass]
        for mass in quarkMass:
            if mMed > 2.*mass:
                betaQQ.append((1. - (2. * mass)**2/mMed**2)**betaExp)
            else:
                betaQQ.append(0.)
    elif type == 'scalar' or type == 'pseudo':
        normFactorQQ = (3. * gQ**2 * mMed)/(8. * m.pi * vev**2)
        if type == 'scalar':
            betaExp = 1.5
        elif type == 'pseudo':
            betaExp = 0.5
        for mass in quarkMass:
            if mMed > 2.*mass:
                betaQQ.append(1.)
                ratioFuncQQ.append(mass**2 *
                                   (1. - (2. * mass)**2/mMed**2)**betaExp)
            else:
                betaQQ.append(0.)
                ratioFuncQQ.append(0.)
    else:
        print("Invalid type")
        return 0
    # sum over all quarks
    Gamma_qq = [normFactorQQ * b * r for r, b in zip(ratioFuncQQ, betaQQ)]
    sumGamma_qq = 0.
    for w in Gamma_qq:
        sumGamma_qq += w

    # Lepton Partial Width Calculation
    leptonName = ['e', 'nu_e', 'mu', 'nu_mu', 'tau', 'nu_tau']
    leptonMass = [0.5109989461e-3, 0, 105.6583745e-3, 0, 1.77686, 0]  # in GeV
    fLL = (gL**2)*mMed/(12*m.pi)
    fNN = (gL**2)*mMed/(24*m.pi)
    normFactorLL = [fLL, fNN, fLL, fNN, fLL, fNN]
    betaFactorsLL = list()  # lists containing entry for each lepton
    sumGamma_ll = 0.
    if type == 'vector' or type == 'axial':
        for (i, mass) in enumerate(leptonMass):
            if i % 2 == 0:
                zL = (mass/mMed)**2
                if type == 'vector':
                    betaFactorsLL.append(((1-(4*zL))**(1/2.))*(1+2*zL))
                elif type == 'axial':
                    betaFactorsLL.append(((1-(4*zL))**(3/2.)))
                else:
                    print(
                        "warning: lepton partial width not implemented for non-vector models")
                    betaFactorsLL.append(1)
            else:
                betaFactorsLL.append(1)
        if False:  # debugging
            print("lepton widths:")
            for (name, mass, n, b) in zip(leptonName, leptonMass, normFactorLL, betaFactorsLL):
                print(name, n*b)
        # sum over all leptons
        Gamma_ll = [n * b for n, b in zip(normFactorLL, betaFactorsLL)]
        for w in Gamma_ll:
            sumGamma_ll += w

    # Dark Matter Partial Width Calculation
    ratioFuncDM = 0.
    if type == 'vector' or type == 'axial':
        normFactorDM = (gDM**2 * mMed)/(12. * m.pi)
        if type == 'vector':
            ratioFuncDM = (1. + (2. * mDM**2)/mMed**2)
        elif type == 'axial':
            ratioFuncDM = 1.
        if mMed > 2.*mDM:
            betaDM = (1. - (2. * mDM)**2/mMed**2)**betaExp
        else:
            betaDM = 0.
    if type == 'scalar' or type == 'pseudo':
        normFactorDM = (gDM**2 * mMed)/(8. * m.pi)
        if type == 'scalar':
            betaExp = 1.5
        elif type == 'pseudo':
            betaExp = 0.5
        ratioFuncDM = 0.
        if mMed > 2.*mDM:
            betaDM = 1.
            ratioFuncDM = (1. - (2. * mDM)**2/mMed**2)**betaExp
        else:
            betaDM = 0.
            ratioFuncDM = 0.
    Gamma_DM = normFactorDM * ratioFuncDM * betaDM

    return Gamma_DM + sumGamma_qq + sumGamma_ll


def make_param_card(mMed, mDM, output_path):
    med_width = swCalc('axial', 0.25, 0, 1.0, mMed, mDM)
    template_path = os.path.join('templates', 'param_card.dat')
    with open(template_path, 'r') as f:
        template_text = f.read()
    template_text = template_text.replace('$AMASS', str(mMed))
    template_text = template_text.replace('$AWIDTH', str(med_width))
    template_text = template_text.replace('$CHIMASS', str(mDM))
    with open(output_path, 'w+') as f:
        f.write(template_text)


def make_input_yaml(output_path, param_card_path):
    with open(os.path.join('templates', 'input.yml'), 'r') as f:
        template_text = f.read()
    template_text = template_text.replace('$PARAM_CARD', param_card_path)
    with open(output_path, 'w+') as f:
        f.write(template_text)


def main():
    parser = argparse.ArgumentParser(
        description='Create directories for each mMed, mDM combinaton that holds appropriate cards and an input.yml.')
    parser.add_argument('--mMeds', nargs='+', type=int,
                        help='Mediator masses in GeV.')
    parser.add_argument('--mDMs', nargs='+', type=int,
                        help='Dark matter masses in GeV.')
    parser.add_argument('--base_dir', help='Base directory for the parameter grid.')
    args = parser.parse_args()

    for mMed, mDM in itertools.product(args.mMeds, args.mDMs):
        d = 'mMed_{}_mDM_{}'.format(mMed, mDM)
        if args.base_dir:
            d = os.path.join(args.base_dir, d)
        os.makedirs(d)
        param_card_path = os.path.join(d, 'param_card.dat')
        make_param_card(mMed, mDM, param_card_path)
        make_input_yaml(os.path.join(d, 'input.yml'), param_card_path)


if __name__ == '__main__':
    main()
