# -*- coding: utf-8 -*-
import json, sympy as sp
import vm
from vm import *
def make(cT, chiw, tag):
    P = dict(vm.P0)
    YN0 = 100.0; share_T = 0.325
    P['YT00'] = YN0*share_T/(1-share_T); Ytot = YN0 + P['YT00']; GDP = 700000.0; SCALE = GDP/Ytot
    P['d'] = 0.384*Ytot; P['mbase'] = 0.18*Ytot; P['cT'] = cT; P['chiw'] = chiw
    IT0 = P['aT0'] + P['iota']*P['q0']; G0 = P['G0']; ST = 0.30*Ytot
    Esp_t = YN0 + ST - IT0 - G0
    P['n0'] = (YN0 - P['nI']*IT0 - P['gn']*G0)/Esp_t
    pur_q = [1158+1557+1671, 2769+2596+1418, 2162+768+473]; P['Pur0'] = (sum(pur_q)/3.0)*4.0/SCALE
    FAE0 = 2250*12/SCALE; P['phi'] = 1.0
    M, ref = baseline(P, 'U'); Wv = ev(M['W'], ref); Sf = ev(M['Sf'], ref)
    P['alpha'] = (P['q0']*P['d'] + (FAE0/P['theta'])/P['phi'])/(Wv+Sf)
    shocks = {'dPsi': ([k0s],[-1.0]), 'dPur': ([Pur],[1.0]), 'dp': ([p_s],[0.01]), 'drho': ([rho_s],[0.01]),
              'dtx': ([tx],[-0.01]), 'dtm': ([tm],[-0.01]), 'dG': ([G],[1.0]), 'dYT0': ([YT0],[1.0])}
    out = {}
    for nm,(sy,sz) in shocks.items():
        sol, co, Mx, rf = structural(P, 'U', sy, sz, 'int', True)
        dYN, di, dq = sol
        dYT = float(sum(sp.diff(Mx['YT'], s_).subs(rf)*z for s_,z in zip(sy,sz))) + float(sp.diff(Mx['YT'], q).subs(rf))*dq
        dYtot = dYN + P['q0']*dYT      # producto real en volumen: N más T a precios relativos de referencia (sin efecto de valuación por q)
        out[nm] = dict(dYN=dYN, di=di, dq=dq, dYT=dYT, dYtot=dYtot, dEmp=P['lN']*dYN+P['lT']*dYT,
                       dgap=(dYN*co['Ymax'] - P['YN0']*co['dYmax_dq']*dq)/co['Ymax']**2*100)
    co, M, ref = coefficients(P, 'U', True)
    info = dict(ThN=co['ThN'], etaq=co['etaq'], kN=co['kN'], D=co['D'], Ups=co['Ups'], xgap=co['xgap'], comp=co['comp'],
                res=dict(IS=co['res_IS'], LM=co['res_LM'], BOP=co['res_BOP']), cT=cT, chiw=chiw)
    json.dump(dict(unit=out, info=info, P=P, SCALE=SCALE, Ytot=Ytot), open(f'set_{tag}.json','w'), indent=1)
    print(tag, 'cT=%.2f chiw=%.2f ThN=%.3f etaq=%.1f kN=%.3f D=%.3f'%(cT,chiw,co['ThN'],co['etaq'],co['kN'],co['D']), {k: round(v,3) for k,v in co['comp'].items()})
    print('   dp: dYN %.4f di %.4f dq %.5f | dPur: dYN %.4f dq %.5f | dtm: dYN %.4f'%(out['dp']['dYN'],out['dp']['di'],out['dp']['dq'],out['dPur']['dYN'],out['dPur']['dq'],out['dtm']['dYN']))
make(0.40, 0.60, 'A')
make(0.10, 0.20, 'B')
