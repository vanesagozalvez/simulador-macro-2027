# -*- coding: utf-8 -*-
"""
Verificación reproducible del modelo IS-LM-BP de dos sectores, versión 6.
Uso:  python3 verificacion_modelo_v6.py     (requiere sympy)
Salida: resultados_v6.json
Novedades v6: (1) tensión financiera u con carga de servicio en dólares DSR; (2) salario real con indexación parcial
en el consumo; (3) capacidad de N decreciente en q. Parámetros ILUSTRATIVOS (no estimados).
Convención: numerario = bien no transable N; flujos trimestrales; tasas anuales en decimales.
"""
import sympy as sp, json, math

P0 = dict(
  cN=0.85, tN=0.25, cT=0.40, tTo=0.15, lamx=0.85, tx0=0.10, cW=0.02, cu=0.30, cr=0.80, Tr0=5.0,
  d=40.0, Om=10.0, psi=0.01, aN=0.60, aL=0.10, a0N=15.0, omN=0.70, rr=0.34, tauT=0.17, vs=0.50, dD=0.80,
  piNe=0.30, nI=0.20, aT0=5.0, iota=0.30, n0=0.60, ntau=0.50, tm0=0.10, nq=0.0, gn=0.90, G0=30.0,
  sT=0.15, YT00=22.0, phi=0.10, theta=0.70, alpha=0.60, a1=0.30, a2=0.30, a4=0.50, th1=0.50, th4=0.30,
  siI=0.30, k1=0.20, k2=0.50, k4=0.10, l2=3.0, l3=1.0, a=0.30, e4=0.40, rho0=0.064, p0=0.05,
  YN0=100.0, q0=1.0, i0=0.25, eps0=0.20, mbase=25.0, Pur0=0.5, lN=1.0, lT=0.2,
  # --- novedades v6
  chiw=0.60, lamw=0.50, betaN=0.30, ubar=0.30, ubase=0.10, u1=5.0, u2=25.0, spreadL=0.15, sOm=0.20, gw=0.0,
  aq=0.10, YNmax0=105.0)

S = sp.symbols
YN, i, q, dR, mm = S('YN i q dR mm')
G, Tr, tm, YT0, tx, k0s, Pur, eps_s, p_s, rho_s, c0, m0, l1, u0s = S('G Tr tm YT0 tx k0s Pur eps_s p_s rho_s c0 m0 l1 u0s')

def build(Pp, branch='U', v6=True):
    f = lambda k: sp.Float(Pp[k])
    tT = f('tTo') + f('lamx')*tx
    n = f('n0') + f('nq')*(q-f('q0')) + f('ntau')*(tm-f('tm0'))
    # --- tensión financiera
    om = (q/f('q0'))**(-(1-f('chiw'))*f('betaN'))            # índice de salario real (relativo a la referencia)
    DSR = q*f('sOm')*f('Om')/YN                               # carga de servicio en dólares sobre ingreso en pesos de N
    if v6:
        z = u0s + f('u1')*((i+f('spreadL'))-f('piNe')-f('gw')-sp.log(om)) + f('u2')*DSR
        u = f('ubar')/(1+sp.exp(-z))
    else:
        u = sp.Float(Pp['ubase']); om = sp.Integer(1)
    kapm = (1-f('rr')-f('tauT'))*(1-f('vs')*u)*f('dD')
    LN = f('omN')*kapm*mm
    YT = YT0 + f('sT')*(1-tx)*q if branch == 'U' else sp.Float(Pp['YT00']) + f('sT')*(1-f('tx0'))*f('q0')
    W = mm + q*f('d')
    lw = f('lamw') if v6 else 0.0
    C = c0 + f('cW')*W - f('cu')*u + f('cN')*(1-f('tN'))*YN*(1+lw*(om-1)) + f('cT')*(1-tT)*q*YT + f('cr')*Tr
    IN = f('a0N') - f('aN')*(i-f('piNe')) + f('aL')*LN - f('psi')*q*f('Om')
    IT = f('aT0') + f('iota')*q
    Esp = C + IN
    DN = n*Esp + f('nI')*IT + f('gn')*G
    Yd = (1-f('tN'))*YN + (1-tT)*q*YT + Tr
    Sav = Yd - C
    Sf = Sav - f('siI')*IN
    eps = eps_s + f('e4')*(p_s-f('p0'))
    alpha = f('alpha') - f('a1')*((i-f('i0'))-(eps-f('eps0'))) + f('a2')*(rho_s-f('rho0')) + f('a4')*(p_s-f('p0'))
    theta = f('theta') + f('th1')*(rho_s-f('rho0')) + f('th4')*(p_s-f('p0'))
    PD = f('phi')*(alpha*(W+Sf) - q*f('d'))
    FAE = theta*PD
    NX = q*YT - (1-n)*Esp - (1-f('nI'))*IT - (1-f('gn'))*G
    KA = k0s + f('k1')*((i-f('i0'))-(eps-f('eps0'))) - f('k2')*(rho_s-f('rho0')) - f('k4')*(p_s-f('p0'))
    BOP = NX + KA - FAE
    LM = l1*(YN + q*YT) - f('l2')*i - f('l3')*eps - mm
    Ymax = f('YNmax0')*(1 - f('aq')*(q-f('q0'))) if v6 else sp.Float(Pp['YNmax0'])
    xgap = (YN - Ymax)/Ymax
    return dict(n=n, YT=YT, C=C, IN=IN, IT=IT, Esp=Esp, DN=DN, Sav=Sav, Sf=Sf, FAE=FAE, PD=PD, NX=NX, KA=KA,
                BOP=BOP, LM=LM, tT=tT, kapm=kapm, eps=eps, alpha=alpha, theta=theta, W=W, u=u, om=om, DSR=DSR,
                Ymax=Ymax, xgap=xgap, z=(z if v6 else None))

def baseline(Pp, branch, v6=True):
    M = build(Pp, branch, v6)
    ref = {G:Pp['G0'], Tr:Pp['Tr0'], tm:Pp['tm0'], YT0:Pp['YT00'], tx:Pp['tx0'], Pur:Pp['Pur0'], eps_s:Pp['eps0'],
           p_s:Pp['p0'], rho_s:Pp['rho0'], YN:Pp['YN0'], i:Pp['i0'], q:Pp['q0'], dR:Pp['Pur0'], mm:Pp['mbase'],
           m0:Pp['mbase']-Pp['a']*Pp['Pur0']}
    if v6:
        # u0s tal que u(referencia) = ubase
        ubase = Pp['ubase']; zb = math.log((ubase/Pp['ubar'])/(1-ubase/Pp['ubar']))
        ref[u0s] = float(sp.solve(sp.Eq(M['z'].subs(ref), zb), u0s)[0])
    YTv = float(M['YT'].subs(ref))
    ref[l1] = (Pp['mbase'] + Pp['l2']*Pp['i0'] + Pp['l3']*Pp['eps0'])/(Pp['YN0'] + Pp['q0']*YTv)
    ref[c0] = float(sp.solve((YN-M['DN']).subs(ref), c0)[0])
    ref[k0s] = float(sp.solve((M['BOP']-dR).subs(ref), k0s)[0])
    return M, ref

def ev(e, ref): return float(sp.N(e.subs(ref)))

def coefficients(Pp, branch='U', v6=True):
    M, ref = baseline(Pp, branch, v6); f = lambda k: Pp[k]
    d = lambda e, x: ev(sp.diff(e, x), ref)
    out = {}
    out['res_IS'] = ev(YN-M['DN'], ref); out['res_LM'] = ev(M['LM'], ref); out['res_BOP'] = ev(M['BOP']-dR, ref)
    out['u_ref'] = ev(M['u'], ref)
    n = ev(M['n'], ref); tT = ev(M['tT'], ref); alpha = ev(M['alpha'], ref); theta = ev(M['theta'], ref)
    Esp = ev(M['Esp'], ref); YTv = ev(M['YT'], ref); Wv = ev(M['W'], ref); Sfv = ev(M['Sf'], ref)
    VT = ev(sp.diff(q*M['YT'], q), ref)
    # derivadas del gasto interno E_s = C + I^N y del ahorro financiero S^f
    eY, ei, eq_, em = [d(M['Esp'], x) for x in (YN, i, q, mm)]
    sY, si, sq, sm = [d(M['Sf'], x) for x in (YN, i, q, mm)]
    # sensibilidades de la tensión financiera
    uY, ui, uq = [d(M['u'], x) for x in (YN, i, q)]
    # coeficientes por derivación directa de la balanza de pagos
    LamY = -d(M['BOP'], YN); Gi = d(M['BOP'], i); zN = -d(M['BOP'], mm); etaq = d(M['BOP'], q)
    ThN = d(M['DN'], q); gp_rho = -d(M['BOP'], rho_s); gp_p = -d(M['BOP'], p_s); Geps = -d(M['BOP'], eps_s)
    # fórmulas generales (en términos de e_x, s_x)
    kN = 1/(1-n*eY)
    th_phi = theta*f('phi')
    LamY_f = (1-n)*eY + th_phi*alpha*sY
    Gi_f = f('k1') - (1-n)*ei + th_phi*f('a1')*(Wv+Sfv) - th_phi*alpha*si
    zN_f = th_phi*alpha*(1+sm) + (1-n)*em
    etaq_f = VT + f('nq')*Esp - (1-n)*eq_ - (1-f('nI'))*f('iota') - th_phi*(alpha*(f('d')+sq) - f('d'))
    ThN_f = f('nq')*Esp + n*eq_ + f('nI')*f('iota')
    Ups_f = 1-(1-n)*f('cT')*(1-tT)-th_phi*alpha*(1-f('cT'))*(1-tT)
    Ups_num = d(M['BOP'], YT0)/f('q0') if branch == 'U' else None
    # descomposición de Θ^N (efecto de una depreciación real sobre la demanda de N)
    cuN = f('cu') + f('aL')*f('omN')*Pp['mbase']*(1-f('rr')-f('tauT'))*f('vs')*f('dD')   # c_u efectivo (consumo + crédito)
    comp = {
      'reasignacion': f('nq')*Esp,
      'riqueza': n*f('cW')*f('d'),
      'hoja_balance': -n*f('psi')*f('Om'),
      'derrame': n*f('cT')*(1-tT)*VT,
      'inversion_T': f('nI')*f('iota'),
      'salario_real': n*d(f('cN')*(1-f('tN'))*YN*(1+(f('lamw') if v6 else 0.0)*(M['om']-1)), q),
      'tension_financiera': n*(-f('cu')*uq + f('aL')*d(M['kapm']*f('omN')*mm, q) if v6 else 0.0),
    }
    out.update(dict(n=n, tT=tT, alpha=alpha, theta=theta, Esp=Esp, YT=YTv, VT=VT, kN=kN, kN_v5=1/(1-n*f('cN')*(1-f('tN'))),
        D=kN*n*f('cT')*(1-tT), gnkN=f('gn')*kN, LamY=LamY, Gi=Gi, zN=zN, etaq=etaq, ThN=ThN, gamma_rho=gp_rho, gamma_p=gp_p,
        Gamma_eps=Geps, Ups=Ups_f, W=Wv, Sf=Sfv, eY=eY, ei=ei, eq=eq_, em=em, sY=sY, si=si, sq=sq, sm=sm, uY=uY, ui=ui, uq=uq,
        alpha_is=n*em, beta_is=-n*ei, comp=comp, cuN=cuN, kapm=ev(M['kapm'], ref), DSR=ev(M['DSR'], ref),
        om_deriv=d(M['om'], q), Ymax=ev(M['Ymax'], ref), dYmax_dq=d(M['Ymax'], q), xgap=ev(M['xgap'], ref),
        dx_dq=d(M['xgap'], q), dx_dYN=d(M['xgap'], YN),
        resid_formulas=dict(Ups=(Ups_num-Ups_f) if Ups_num is not None else None, LamY=LamY-LamY_f, Gi=Gi-Gi_f,
        zN=zN-zN_f, etaq=etaq-etaq_f, ThN=ThN-ThN_f, ThN_decomp=ThN-sum(comp.values())),
        qUps_over_LamY=f('q0')*Ups_f/LamY, ref={str(k):v for k,v in ref.items()}))
    return out, M, ref

def closed_forms(co, Pp, shock):
    n=co['n']; kN=co['kN']; al=co['alpha_is']; be=co['beta_is']; Th=co['ThN']; Lam=co['LamY']; Gi=co['Gi']; zN=co['zN']
    eta=co['etaq']; VT=co['VT']; l1v=co['ref']['l1']; l2=Pp['l2']; a=Pp['a']
    dJ,dPsi,dMl,dPur=shock['dJ'],shock['dPsi'],shock['dMl'],shock['dPur']
    chi=Th/eta; kF=kN/(1-kN*chi*Lam); bF=be+chi*Gi; tL=l1v*VT/eta; lE=l1v+tL*Lam; hE=l2+tL*Gi; DF=1+kF*bF*lE/hE
    dm=a*dPur
    dY_int=(kF/DF)*(dJ+(al+chi*zN)*dm+chi*(dPsi+dPur)-(bF/hE)*(tL*(zN*dm+dPsi+dPur)+dMl-dm))
    di_int=(lE*dY_int+tL*(zN*dm+dPsi+dPur)+dMl-dm)/hE
    dPi=Lam*dY_int-Gi*di_int+zN*dm+dPsi; dq_int=(dPi+dPur)/eta
    abar=al+be/l2; Xi=1+a*(zN+Gi/l2); sig=Lam-Gi*l1v/l2; D0=1+kN*be*l1v/l2+kN*a*abar*sig/Xi
    dY_t=(kN/D0)*(dJ-((be+a*(be*zN-al*Gi))/(l2*Xi))*dMl-(a*abar/Xi)*dPsi)
    dPi_t=(sig*dY_t+(Gi/l2)*(0-dMl)+dPsi)/Xi
    di_t=(l1v*dY_t+dMl-(-a*dPi_t))/l2
    return dict(int=dict(dY=dY_int,di=di_int,dq=dq_int), techo=dict(dY=dY_t,di=di_t,dR=-dPi_t))

def structural(Pp, branch, shocks_syms, sizes, regime, v6=True):
    co, M, ref = coefficients(Pp, branch, v6)
    if regime == 'int':
        mexpr = m0 + Pp['a']*Pur
        Fs = [YN-M['DN'], M['LM'], M['BOP']-Pur]; unk = [YN, i, q]
    else:
        mexpr = m0 + Pp['a']*dR
        Fs = [YN-M['DN'], M['LM'], M['BOP']-dR]; unk = [YN, i, dR]
    Fs = [e.subs(mm, mexpr) for e in Fs]
    if regime == 'int': Fs = [e.subs(dR, Pur) for e in Fs]
    else: Fs = [e.subs(q, Pp['q0']) for e in Fs]
    rf = {k:v for k,v in ref.items() if k not in (mm,)}
    rf[m0] = Pp['mbase']-Pp['a']*Pp['Pur0']
    Jm = sp.Matrix(Fs).jacobian(unk).subs(rf)
    dF = sp.zeros(3,1)
    for s_,sz in zip(shocks_syms, sizes):
        dF += sp.Matrix(Fs).diff(s_).subs(rf)*sz
    sol = -Jm.inv()*dF
    return [float(x) for x in sol], co, M, rf

def capacity_binding(Pp, shocks_syms, sizes):
    """Régimen con capacidad de N vinculante (interior de la banda): Y^N = Ymax(q); el exceso de demanda se importa."""
    P1 = dict(Pp); P1['YNmax0'] = Pp['YN0']            # referencia en el punto de quiebre: capacidad = producto
    co, M, ref = coefficients(P1, 'U', True)
    mexpr = m0 + P1['a']*Pur
    ex = M['DN'] - M['Ymax']                           # exceso de demanda de N (importado)
    Bc = (M['BOP'] - ex) - Pur
    Lm = M['LM']
    Fs = [Lm.subs(YN, M['Ymax']), Bc.subs(YN, M['Ymax'])]
    Fs = [e.subs(mm, mexpr).subs(dR, Pur) for e in Fs]
    rf = {k:v for k,v in ref.items() if k not in (mm,)}; rf[m0] = P1['mbase']-P1['a']*P1['Pur0']
    Jm = sp.Matrix(Fs).jacobian([i, q]).subs(rf)
    dF = sp.zeros(2,1)
    for s_,sz in zip(shocks_syms, sizes): dF += sp.Matrix(Fs).diff(s_).subs(rf)*sz
    sol = -Jm.inv()*dF
    dq_ = float(sol[1]); di_ = float(sol[0])
    dY = float(sp.diff(M['Ymax'], q).subs(rf))*dq_
    ext = ex.subs(YN, M['Ymax']).subs(mm, mexpr).subs(dR, Pur)
    exr = float(sum(sp.diff(ext, s_).subs(rf)*z for s_, z in zip(shocks_syms, sizes)) + sp.diff(ext, q).subs(rf)*dq_ + sp.diff(ext, i).subs(rf)*di_)
    return dict(dYN=dY, di=di_, dq=dq_, dexcess=exr)

if __name__ == '__main__':
    R = {'params': P0}
    cU, MU, refU = coefficients(P0, 'U', True); cB, MB, refB = coefficients(P0, 'B', True)
    c5, _, _ = coefficients(P0, 'U', False)
    R['coef_U'] = cU; R['coef_B'] = cB; R['coef_v5'] = {k: c5[k] for k in ('kN','D','gnkN','LamY','Gi','zN','etaq','ThN','Ups','Esp','VT')}
    # sensibilidades
    R['sens_chiw'] = {}
    for cw in (0.0, 0.6, 1.0):
        Pq = dict(P0); Pq['chiw'] = cw; c, _, _ = coefficients(Pq, 'U', True)
        R['sens_chiw'][str(cw)] = dict(ThN=c['ThN'], etaq=c['etaq'], salario_real=c['comp']['salario_real'], tension=c['comp']['tension_financiera'], uq=c['uq'])
    R['sens_u2'] = {}
    for u2 in (0.0, 25.0, 100.0):
        Pq = dict(P0); Pq['u2'] = u2; c, _, _ = coefficients(Pq, 'U', True)
        R['sens_u2'][str(u2)] = dict(ThN=c['ThN'], etaq=c['etaq'], kN=c['kN'], tension=c['comp']['tension_financiera'], uY=c['uY'])
    R['sens_nq'] = {}
    for nqv in (0.3, -0.3):
        Pq = dict(P0); Pq['nq'] = nqv; c, _, _ = coefficients(Pq, 'U', True)
        R['sens_nq'][str(nqv)] = dict(ThN=c['ThN'], etaq=c['etaq'])
    # umbral de indexación salarial: Θ^N es lineal en chi_w (con u de referencia fijo)
    t0 = R['sens_chiw']['0.0']['ThN']; t1 = R['sens_chiw']['1.0']['ThN']
    R['chi_star'] = -t0/(t1-t0)
    # umbral de deuda en dólares: Θ^N es lineal en Ω (con u de referencia fijo)
    th = []
    for Om in (10.0, 110.0):
        Pq = dict(P0); Pq['Om'] = Om; c, _, _ = coefficients(Pq, 'U', True); th.append((Om, c['ThN']))
    slope = (th[1][1]-th[0][1])/(th[1][0]-th[0][0])
    R['Omega_star'] = th[0][0] - th[0][1]/slope; R['ThN_slope_Om'] = slope
    # estática comparativa
    shocks = {
     'gasto': ([G], [1.0]), 'apertura': ([tm], [-0.01]), 'auge': ([YT0], [1.0]), 'retenciones': ([tx], [-0.01]),
     'cuenta_fin': ([k0s], [-1.0]), 'compras': ([Pur], [1.0]), 'prob_caida': ([p_s], [0.25]), 'eps_e': ([eps_s], [0.10])}
    R['cs'] = {}
    for br in ('U', 'B'):
        R['cs'][br] = {}
        for nm, (sy, sz) in shocks.items():
            R['cs'][br][nm] = {}
            for reg in ('int', 'techo'):
                if reg == 'techo' and nm == 'compras': continue
                sol, co, M, rf = structural(P0, br, sy, sz, reg, True)
                dYT = float(sum(sp.diff(M['YT'], s_).subs(rf)*z for s_, z in zip(sy, sz)))
                dq_ = sol[2] if reg == 'int' else 0.0
                if reg == 'int': dYT += float(sp.diff(M['YT'], q).subs(rf))*sol[2]
                dEmp = P0['lN']*sol[0] + P0['lT']*dYT
                dxg = (sol[0]*co['Ymax'] - P0['YN0']*co['dYmax_dq']*dq_)/co['Ymax']**2*100   # variación de la brecha de N en puntos
                R['cs'][br][nm][reg] = dict(dYN=sol[0], di=sol[1], third=sol[2], dYT=dYT, dEmp=dEmp, dgap=dxg)
    # el mismo cálculo con el modelo v5 (u fijo, sin salario real, capacidad fija) para comparar
    R['cs_v5'] = {}
    for nm, (sy, sz) in shocks.items():
        R['cs_v5'][nm] = {}
        for reg in ('int', 'techo'):
            if reg == 'techo' and nm == 'compras': continue
            sol, co, M, rf = structural(P0, 'U', sy, sz, reg, False)
            R['cs_v5'][nm][reg] = dict(dYN=sol[0], di=sol[1], third=sol[2])
    # verificación de formas cerradas
    chk = {}
    for nm, (sy, sz) in shocks.items():
        shk = dict(dJ=float(sum(ev(sp.diff(MU['DN'], s_), refU)*z for s_, z in zip(sy, sz))),
                   dPsi=float(sum(-ev(sp.diff(MU['BOP'], s_), refU)*z for s_, z in zip(sy, sz) if s_ != Pur)),
                   dMl=float(sum(ev(sp.diff(MU['LM'], s_), refU)*z for s_, z in zip(sy, sz) if s_ != Pur)),
                   dPur=float(sum(z for s_, z in zip(sy, sz) if s_ == Pur)))
        cf = closed_forms(cU, P0, shk)
        a_ = R['cs']['U'][nm]['int']; b_ = R['cs']['U'][nm].get('techo')
        chk[nm] = dict(int=abs(cf['int']['dY']-a_['dYN'])+abs(cf['int']['di']-a_['di'])+abs(cf['int']['dq']-a_['third']))
        if b_: chk[nm]['techo'] = abs(cf['techo']['dY']-b_['dYN'])+abs(cf['techo']['di']-b_['di'])+abs(cf['techo']['dR']-b_['third'])
        chk[nm]['shk'] = shk
    R['check_closed_forms'] = chk
    # capacidad vinculante
    R['cap_bind'] = {nm: capacity_binding(P0, sy, sz) for nm, (sy, sz) in shocks.items() if nm in ('gasto', 'apertura', 'cuenta_fin', 'prob_caida')}
    # efecto de la depreciación sobre la brecha de N a través de la capacidad
    R['gap_effect'] = dict(dx_dq=cU['dx_dq'], per10pct_points=cU['dx_dq']*0.10*100, xgap=cU['xgap'], kappa_N=0.40, dpi_points=0.40*cU['dx_dq']*0.10*100)
    # lazo riesgo-brecha
    c4 = 4.0; rows = []
    for g in (0.35, 0.9, 1.0, 1.02, 1.05, 1.10):
        row = dict(g=g)
        if g < 1: row['fixed'] = c4/(1-g)
        elif g == 1: row['fixed'] = None
        else: row['fixed'] = c4/(1-g)
        r0 = 6.15; t = 0; r = r0; hist = [r0]
        while r < 20 and t < 60:
            r = c4 + g*r; t += 1; hist.append(r)
        row['t_to_20'] = t if r >= 20 else None
        row['hist'] = hist[:6]
        row['admissible'] = (g < 1 and row['fixed'] is not None and row['fixed'] > 0)
        rows.append(row)
    R['loop'] = rows
    # Φ^V y riesgo de equilibrio con acuerdo vigente
    pb, lp, pm, lm, g1 = 1.0, 2.0, 0.5, 3.0, 0.35
    Phi = lambda m: -pb*(1-math.exp(-lp*m)) if m >= 0 else pm*(math.exp(lm*(-m))-1)
    R['phi'] = [dict(m=m, Phi=Phi(m), rho=(4.0+Phi(m))/(1-g1)) for m in (1.0, 0.5, 0.0, -0.25, -0.5, -1.0)]
    R['phi_floor'] = (4.0-pb)/(1-g1)
    # estanflación
    Q = dict(g=0.5, th=0.6, ka=0.40, bi=0.10, be=0.30, bm=0.10, pi1=35.0, piA=25.0, ebar=20.0, i_n=35.0)
    dpi = lambda x, ie, i_, mu, v, pi1=None: (1-Q['g'])*(1-Q['th'])*(Q['piA']-(Q['pi1'] if pi1 is None else pi1)) + (1-Q['g'])*Q['be']*(ie-Q['ebar']) + Q['ka']*x + Q['bi']*(i_-Q['i_n']) + Q['bm']*mu + v
    sc = {'base': (-2, 20, 35, 0, 0), 'S1': (-2, 20, 35, 0, 3), 'S2': (-3, 20, 50, 0, 0), 'S3': (-2, 22, 35, 10, 0),
          'S12': (-3, 20, 50, 0, 3), 'S5': (-3, 40, 55, 0, 0)}
    R['stag'] = {}
    for k, (x, ie, i_, mu, v) in sc.items():
        left = (1-Q['g'])*Q['be']*(ie-Q['ebar']) + Q['bi']*(i_-Q['i_n']) + Q['bm']*mu + v
        right = Q['ka']*abs(x) + (1-Q['g'])*(1-Q['th'])*(Q['pi1']-Q['piA'])
        R['stag'][k] = dict(x=x, left=left, right=right, dpi=dpi(x, ie, i_, mu, v), dpi_ipc=0.65*dpi(x, ie, i_, mu, v))
    R['ecrit'] = {str(x): Q['ebar'] + (Q['ka']*abs(x)+(1-Q['g'])*(1-Q['th'])*(Q['pi1']-Q['piA']))/((1-Q['g'])*Q['be']) for x in (-2, -3)}
    def path(eta, T=8):
        Yp, Y, pi = 100.0, 97.0, 35.0; xs, ps = [], []
        for t in range(T):
            x = (Y/Yp-1)*100; pi = pi + dpi(x, 20.0, 35.0, 0.0, 0.0, pi1=pi); xs.append(x); ps.append(pi); Yp = Yp*(1-eta*max(0.0, -x/100))
        return dict(x=xs, pi=ps)
    R['hist'] = {str(e): path(e) for e in (0.0, 0.5, 1.0)}
    json.dump(R, open('resultados_v6.json', 'w'), indent=1, ensure_ascii=False)
    print('OK v6; u de referencia:', round(cU['u_ref'], 6), '; chi* =', round(R['chi_star'],4), '; Omega* =', round(R['Omega_star'],1))
    print('Residuos referencia:', {k: round(cU[k], 10) for k in ('res_IS', 'res_LM', 'res_BOP')})
    print('Residuos fórmulas generales:', {k: (None if v is None else round(v, 10)) for k, v in cU['resid_formulas'].items()})
    print('Formas cerradas:', {k: {kk: round(vv, 10) for kk, vv in v.items() if kk != 'shk'} for k, v in chk.items()})
