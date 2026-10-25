function [angle_f, delta_u, TDD, P_loss, x_final, seed, ieee_vio, v_harm] = RTOPP_D19_simple_rip(x_star, PHI, enable, mod_index, phi_index, gammas, fg)
%RTOPP_D19_SIMPLE_RIP  RTOPP_D19_simple_vh + peso de RISADO lado convertidor.
%
%   CAMBIO RESPECTO DE RTOPP_D19_simple_vh (propuesta A)
%     Los armonicos 53..97 (impares, no multiplos de 3) no tienen limite
%     IEEE 519 en el modelo, asi que el optimizador les tiraba la energia
%     que sacaba de 5..49 (sobre todo al 53).  Eso casi no se ve en la red
%     (el LCL los atenua ~1/n^3) pero si en la corriente del CONVERTIDOR
%     (atenuacion ~1/n): sube el risado y las perdidas.
%
%     Aqui esos 16 armonicos se agregan al modelo exacto (misma recurrencia
%     de Chebyshev, hasta j = 49) y entran SOLO como costo en la FO:
%
%         + 1/2 * sum_n  LAMBDA_RIP * (g_c(n)/I_L_N)^2 * |x_n + J_n*u|^2
%
%     con g_c(n) la corriente del lado convertidor [A] por unidad de
%     espectro (Vdc2/2 * |H_conv(n)|, LCL de params.m).  Es un peso fijo,
%     sin integrador ni limite: no compite con IEEE 519 ni con el TDD.
%     NX pasa de 34 a NXT = 66 filas en J (W cuesta ~2x en fases 1..3).
%     Interfaz y salidas identicas a RTOPP_D19_simple_vh.
%
%   Base (RTOPP_D19_simple): optimizador RT-OPP (D = 19) con restricciones
%   por pesos adaptativos.  Misma interfaz, mismo paso de Gauss-Newton, mismo modelo
%   de perdidas y misma tabla de semillas que RTOPP_D19.  Lo que cambia es
%   COMO se imponen las restricciones.
%
%   IDEA
%     RTOPP_D19 calcula el paso de GN y DESPUES lo proyecta sobre discos,
%     bola de TDD y fundamental, todo en el modelo LINEALIZADO.  Como el
%     modelo lineal se equivoca, necesita reserva de Taylor, filtro de
%     aceptacion, modo reparacion con un QP propio y re-siembras rotativas.
%
%     Aqui las restricciones armonicas y de TDD NO se proyectan: entran a la
%     misma funcion objetivo como PESOS que se ajustan solos, una vez por
%     superciclo, midiendo el espectro EXACTO del patron que esta saliendo:
%
%         theta_k <- theta_k * |xh_k| / eps_k        (armonico k, IEEE 519)
%         theta_T <- theta_T * TDD / TDD_obj          (TDD)
%
%     Si un armonico se pasa de su limite su peso sube; si le sobra, baja.
%     Es un integrador (en escala logaritmica) por restriccion.  En regimen
%     cada theta queda en uno de dos estados:
%       - restriccion activa   : theta tal que |xh_k| = eps_k exacto
%       - restriccion inactiva : theta = TH_MIN (peso despreciable)
%     que son justamente las condiciones KKT del problema restringido, con
%     theta*w_k como multiplicador de Lagrange.  El error de linealizacion
%     no importa: el lazo se cierra con el espectro exacto, y el integrador
%     lo corrige solo.
%
%     La fundamental es una IGUALDAD y se trata aparte: el paso de GN se
%     resuelve con la restriccion J1*u = r1 exacta (KKT con 2 filas, un
%     complemento de Schur 2x2) y, en cada muestra, el trim de Newton exacto
%     de siempre la deja en FT_TOL.
%
%     El poliedro de angulos (orden, cruce por pi, nivel maximo, caja) entra
%     como barrera logaritmica -MU_B*sum(log(holgura)): su gradiente va al
%     rhs y su Hessiano a W, y el paso se recorta para no consumir mas de
%     TAU_B de la holgura (frac_bound).  Los pulsos no chocan, que era donde
%     el lazo de pesos se estancaba.  clamp_angles queda de salvaguarda.
%
%     Region de confianza: DG_MAX en norma, DG_OUT fuera de norma.
%
%     Estancamiento: si el patron sigue fuera de norma N_STK superciclos sin
%     mejorar un 5%, se rota la celda semilla (+0, +1, +2 en PHI).  En cada
%     re-siembra los multiplicadores vuelven a TH_MIN: heredar pesos
%     saturados de otra cuenca deja al lazo pegado.
%
%   REPARTO (M_CYC = 5, fases 0..4)
%     0  publica el paso anterior (frac_bound + clamp), modelo exacto,
%        merito, multiplicadores, rhs y barrera
%     1  W = J'*Q*J, filas 1..RW1
%     2  W, filas RW1+1..RW2
%     3  W, filas RW2+1..N + bandas de perdidas + Hessiano de barrera
%        + LU columnas 1..LC1
%     4  LU columnas LC1+1..N-1 + paso con igualdad de fundamental
%        + recorte de region de confianza
%   Todas las muestras: trim de fundamental, vigia y salidas.
%   El costo por muestra NO depende del punto de operacion: no hay QP, ni
%   rondas de proyeccion, ni modo reparacion.
%
%   ENTRADAS, PARAMETROS y SALIDAS: identicos a RTOPP_D19.
%     x_star  [34x1]  espectro deseado; (1:2) fundamental, (3:34) fondo de red
%     PHI     [1x1]   fase de la corriente [rad] (modelo de perdidas y semilla)
%     enable  [1x1]   0 = pausa; flanco 0->1 = re-arranque desde la tabla
%     mod_index, phi_index, gammas : tabla offline (Parameter)
%     angle_f, delta_u : patron de conmutacion del periodo completo
%     TDD, P_loss      : del patron que sale [%], [W]
%     x_final          : espectro exacto del patron que sale
%     seed             : [M; PHI en grados] de la celda sembrada
%     ieee_vio         : 1 si el armonico excede el limite IEEE 519
%   SALIDA ADICIONAL (diagnostico)
%     v_harm  [NV_K x 1] magnitud del armonico de VOLTAJE del patron que
%                        sale, solo ordenes impares NO multiplos de 3 entre
%                        NV_L = 50 y NV_H = 100, es decir la banda de risado
%                        (sin limite IEEE; aqui entran solo con el peso
%                        LAMBDA_RIP).  Los pares son 0 por simetria de media
%                        onda:
%                          j :  1  2  3  4  5  6  7  8 ... 15 16
%                          n : 53 55 59 61 65 67 71 73 ... 95 97
%                        n(j) = 3*j + 50 - (j par).  v_harm(j) = |V_n(j)|.
%                        Mismas unidades que x_final (amplitud pico en pu de
%                        Vdc de celda; la fundamental vale M).
%
%   Escrito para MATLAB Coder: sin eig(), sin tamanos variables, bucles
%   explicitos y conteos acotados.
%#codegen

%% ====================================================================
%  0) CONSTANTES E INICIALIZACION UNICA
%  ====================================================================
D   = 19;                  % angulos por semiciclo
N   = 2*D;                 % variables de decision
N_H = 17;                  % armonicos modelados
NX  = 34;                  % 2*N_H
N_R = 16;                  % armonicos de risado: 53 55 59 61 ... 95 97
NXT = NX + 2*N_R;          % filas del modelo exacto (34 + 32 = 66)
NV_L = 50;                 % orden minimo del espectro de voltaje de diagnostico
NV_H = 100;                % orden maximo del espectro de voltaje de diagnostico
NV_K = 16;                 % impares no multiplos de 3 en NV_L..NV_H (53,55,...,97)

% --- Paso de Gauss-Newton (igual que RTOPP_D19) ----------------------
LAMBDA_U    = 1.0;         % amortiguacion proximal
LAMBDA_LOSS = 0.01;        % peso de las perdidas
W_TDD       = 1.0;         % peso base del TDD
LAMBDA_RIP  = 0.1;         % peso del risado lado convertidor (53..97)
RHO         = 0.90;        % margen sobre el limite IEEE 519
LIN_FRAC    = 0.70;        % fija el tope del paso DG_MAX (ver abajo)
DG_OUT      = 0.05;        % tope del paso mientras el patron esta fuera de norma [rad]
TDD_MAX     = 5.0;         % tope de TDD [%]
TDD_FRAC    = 0.95;        % objetivo interno: TDD_FRAC*TDD_MAX
EPS_SEP_DEG = 0.2;         % separacion minima entre conmutaciones [grados]
M_CYC       = 5;           % fases por iteracion.  5 = segmentado, 1 = todo junto

% --- Multiplicadores de las restricciones ----------------------------
TH_MIN = 0.05;             % peso minimo (restriccion inactiva), relativo a w_k
TH_MAX = 1e3;              % peso maximo (punto infactible: minima violacion)
BETA   = 1.0;              % ganancia del integrador (exponente de la razon)
F_UP   = 4.0;              % el peso a lo mas se cuadruplica por superciclo...
F_DN   = 0.9;              % ... y baja lento: evita el ciclo limite en el borde

% --- Barrera del poliedro de angulos ---------------------------------
MU_B   = 1e-6;             % peso de la barrera logaritmica
TAU_B  = 0.9;              % fraccion de la holgura que un paso puede consumir
S_FLR  = 1e-6;             % holgura minima con que se evalua la barrera [rad]

% --- Semilla, trim y vigia (igual que RTOPP_D19) ---------------------
HYST_P  = 0.10;  HYST_PA = 0.0;       % histeresis del eje PHI
HYST_M  = 0.10;  HYST_MA = 0.0015;    % histeresis del eje M
GAM_TR  = 0.60;            % caja alrededor de la semilla [rad]
FT_TOL  = 1e-5;            % tolerancia del trim de fundamental
FT_IT   = 4;               % correcciones del trim por muestra
FT_MAX  = 0.05;            % tope de paso del trim [rad]
FT_BAD  = 1e-3;            % error de fundamental que arma el vigia
N_FBAD  = 16;              % muestras seguidas antes de re-sembrar
N_STK   = 100;             % superciclos fuera de norma sin mejorar -> rota semilla

% --- Planta y perdidas ------------------------------------------------
F_RED  = 50;  K_IN = 3;  I_L_N = 20;
R_ON   = 0.011;  I_CON = 20;  R_GATE = 22;

persistent is_init HARM HIDX wk EPS EPSN2 DG_MAX ...
           E_ON E_OFF C_CD C_SW P_CD0 P_SW0 EPS_SEP LVL_C RW1 RW2 LC1 ...
           gamma_p ph Jp Wp Wpv rhsp qwp bd1 bd2 bdx Hb r1p xp TDDp PLp ...
           th thT upd hpend ipp imp seedp gsd glo ghi ipa ima nfb frf ...
           en_p angf_p du_p viop AI1 AI2 AC1 AC2 AH roff vbst nstk frot fuera ...
           vhp WR

if isempty(is_init)
    is_init = true;

    HARM = [1 5 7 11 13 17 19 23 25 29 31 35 37 41 43 47 49];
    % indice de n = 2j-1 dentro de HARM (0 = no modelado)
    % 1..17 = HARM (IEEE 519), 18..33 = banda de risado (53..97)
    HIDX = [1 0 2 3 0 4 5 0 6 7 0 8 9 0 10 11 0 12 13 0 14 15 0 16 17 ...
            0 18 19 0 20 21 0 22 23 0 24 25 0 26 27 0 28 29 0 30 31 0 32 33];

    % Ganancia del LCL lado CONVERTIDOR: corriente [A] por unidad de
    % espectro en n = 53 55 59 ... 97.  g_c = Vdc2/2*|H_conv(n)| con
    % Lf = 1 mH, Rf = 0.3 mOhm, Cf = 46 uF, Rc = 4 mOhm,
    % Lg + Lt = 1 mH, Rg + Rt = 16.54 mOhm (params.m).
    g_c = [24.6164168, 23.5525908, 21.6972088, 20.8821136, 19.4328511, ...
           18.7851491, 17.6170795, 17.0882969, 16.1242344, 15.6834096, ...
           14.8727045, 14.4990026, 13.8068488, 13.4856674, 12.8872572, ...
           12.6080214];
    WR = zeros(1, N_R);
    for kr = 1:N_R
        WR(kr) = LAMBDA_RIP*(g_c(kr)/I_L_N)^2;
    end

    % Ganancia del LCL: corriente de red [A] por unidad de espectro.
    g_h = [597.92110413, 126.538042084, 95.9476344983, 74.8032630665, ...
           74.4869198249, 102.032992726, 174.139190167, 128.914579495, ...
           56.9469796608, 22.6380073396, 16.2885205746, 9.58202527679, ...
           7.653481689,   5.16883716396, 4.34365581426, 3.1657069979, ...
           2.73687158907];

    % Por armonico: peso del TDD (wk), radio objetivo (EPS, con margen RHO)
    % y limite normativo al cuadrado (EPSN2, solo para ieee_vio).
    wk = zeros(1, N_H);  EPS = zeros(1, N_H);  EPSN2 = zeros(N_H, 1);
    EPS(1) = Inf;  EPSN2(1) = Inf;
    for k = 2:N_H
        h = HARM(k);
        if     h < 11,  L = 0.040;
        elseif h < 17,  L = 0.020;
        elseif h < 23,  L = 0.015;
        elseif h < 35,  L = 0.006;
        else,           L = 0.003;
        end
        e        = L*I_L_N/g_h(k);
        wk(k)    = (g_h(k)/I_L_N)^2;
        EPS(k)   = RHO*e;
        EPSN2(k) = e*e;
    end

    % Tope del paso: el resto de Taylor del armonico mas sensible,
    % sqrt(2)*n/pi*|dg|^2, no pasa de LIN_FRAC de su radio.
    DG_MAX = Inf;
    for k = 2:N_H
        lim = sqrt(LIN_FRAC*EPS(k)*pi/(sqrt(2)*HARM(k)));
        if lim < DG_MAX, DG_MAX = lim; end
    end

    % Perdidas (mismo modelo que RTOPP_D19)
    kon   = (-0.0048149  *R_GATE^2 + 0.31277*R_GATE + 0.25531)/0.25531;
    koff  = (-0.00088891 *R_GATE^2 + 0.14795*R_GATE + 0.16746)/0.16746;
    E_ON  = 4.570969372e-6*kon;
    E_OFF = 2.369616108e-7*koff;
    C_CD  = (I_CON^2*R_ON)/pi;
    C_SW  = 2*F_RED*I_CON;
    P_CD0 = I_CON^2*R_ON;
    P_SW0 = 2*F_RED*D*(1.025851298e-4*kon + 5.127701211e-6*koff);

    EPS_SEP = min(EPS_SEP_DEG*pi/180, 0.9*pi/(D - 0.5));
    LVL_C   = (K_IN-1)/2;
    [AI1, AI2, AC1, AC2, AH] = ang_rows(D, LVL_C, EPS_SEP);

    % Cortes de fase para que las fases 1..4 cuesten parecido
    RW1 = round(N*(1 - sqrt(1 - 0.41)));
    RW2 = round(N*(1 - sqrt(1 - 0.82)));
    LC1 = round(N*(1 - (1 - 0.38)^(1/3)));

    gamma_p = zeros(N, 1);
    ph   = 0;
    Jp   = zeros(NXT, N);   Wp  = zeros(N, N);   Wpv = zeros(N, 1);
    rhsp = zeros(N, 1);    qwp = zeros(NXT, 1);
    bd1  = zeros(D, 1);    bd2 = zeros(D, 1);   bdx = zeros(D, 1);
    Hb   = zeros(N, N);
    r1p  = zeros(2, 1);    xp  = zeros(NX, 1);
    TDDp = 0;  PLp = 0;
    th   = TH_MIN*ones(1, N_H);  thT = TH_MIN;
    upd  = zeros(N, 1);    hpend = false;
    ipp  = 0;  imp = 0;  seedp = zeros(2, 1);
    gsd  = zeros(N, 1);  glo = zeros(N, 1);  ghi = zeros(N, 1);
    ipa  = 0;  ima = 0;  nfb = 0;  frf = false;
    roff = 0;  vbst = Inf;  nstk = 0;  frot = false;  fuera = false;
    en_p = false;  angf_p = zeros(1, 2*N);  du_p = zeros(1, 2*N);
    viop = zeros(N_H, 1);
    vhp  = zeros(NV_K, 1);
end


%% ====================================================================
%  1) ENABLE Y SEMILLA                            [TODAS LAS MUESTRAS]
%  ====================================================================
if enable == 0
    en_p     = false;
    angle_f  = angf_p;   delta_u = du_p;   TDD = TDDp;   P_loss = PLp;
    x_final  = xp;       seed    = seedp;  ieee_vio = viop;
    v_harm   = vhp;
    return
end
if ~en_p                              % flanco 0->1: arranque limpio
    ipp = 0;  imp = 0;
end
en_p = true;

% Celda (PHI, M) con histeresis.  Re-siembran: un cambio de celda PHI, el
% vigia de fundamental y el estancamiento fuera de norma.  El eje M solo
% decide la columna de la semilla y el ancla de la caja.
Mnow   = sqrt(x_star(1)^2 + x_star(2)^2)/((K_IN-1)/2);
ip_new = hyst_idx(PHI,  phi_index, ipp, numel(phi_index), HYST_P, HYST_PA);
im_new = hyst_idx(Mnow, mod_index, imp, numel(mod_index), HYST_M, HYST_MA);

% Estancamiento: el problema no es convexo y la semilla de la celda propia
% puede caer en un minimo local fuera de norma.  Se rota entre la celda
% PHI propia, +1 y +2 (otras ramas del mismo espectro), como RTOPP_D19.
if ipp == 0 || ip_new ~= ipp
    roff = 0;
elseif frot
    roff = mod(roff + 1, 3);
end
npi = numel(phi_index);
ipr = ip_new + roff;
if ipr > npi, ipr = ipr - (npi-1); end

if ipp == 0 || ip_new ~= ipp || frf || frot
    for i = 1:N, gamma_p(i) = gammas(ipr, im_new, i); end
    seedp = [mod_index(im_new); phi_index(ipr)*180/pi];
    ph = 0;  hpend = false;  frf = false;  nfb = 0;
    frot = false;  vbst = Inf;  nstk = 0;
    % Los multiplicadores de la rama vieja no sirven para la nueva: con
    % pesos saturados el paso ignora todo menos el armonico peor y se pega.
    for k = 1:N_H, th(k) = TH_MIN; end
    thT = TH_MIN;
end
ipp = ip_new;  imp = im_new;
seed = seedp;

% Caja de confianza alrededor del patron de la celda vigente.
if ipr ~= ipa || imp ~= ima
    for i = 1:N
        gsd(i) = gammas(ipr, imp, i);
        glo(i) = max(0.035*0,    gsd(i) - GAM_TR);% CAMBIO
        ghi(i) = min(2*pi-0.035*0, gsd(i) + GAM_TR);% CAMBIO
    end
    ipa = ipr;  ima = imp;
end

M1 = (M_CYC <= 1);


%% ====================================================================
%  2) FASE 0: PUBLICAR, MODELO EXACTO, MULTIPLICADORES
%  ====================================================================
if ph == 0 || M1
    % El paso del superciclo anterior se publica AQUI, antes de medir: asi
    % el espectro de esta fase es el del patron que sale todo el superciclo.
    if hpend
        a = frac_bound(gamma_p, upd, AI1, AI2, AC1, AC2, AH, glo, ghi, TAU_B);
        gamma_p = clamp_angles(gamma_p + a*upd, D, LVL_C, EPS_SEP, glo, ghi);
        hpend = false;
    end
    g0 = gamma_p;

    % --- Espectro y jacobiana exactos (recurrencia de Chebyshev) --------
    %   a_n = -2/(n*pi)*sum(sin(n*g))     da_n/dg_i = -2/pi*cos(n*g_i)
    %   b_n =  2/(n*pi)*sum(cos(n*g))     db_n/dg_i = -2/pi*sin(n*g_i)
    K2P = 2/pi;
    cg = cos(g0);  sg = sin(g0);
    t2 = 2*(2*(cg.*cg) - 1);           % 2*cos(2g)
    cn = cg;  sn = sg;  cq = cg;  sq = -sg;
    x = zeros(NXT, 1);  J = zeros(NXT, N);
    for j = 1:49                       % n = 1..97
        k = HIDX(j);
        if k > 0
            n = 2*j - 1;  ss = 0;  sc = 0;
            for i = 1:N
                sc = sc + cn(i);  ss = ss + sn(i);
                J(2*k-1, i) = -K2P*cn(i);
                J(2*k,   i) = -K2P*sn(i);
            end
            x(2*k-1) = -2/(n*pi)*ss;
            x(2*k)   =  2/(n*pi)*sc;
        end
        if j < 49
            for i = 1:N
                cx = t2(i)*cn(i) - cq(i);  sx = t2(i)*sn(i) - sq(i);
                cq(i) = cn(i);  sq(i) = sn(i);  cn(i) = cx;  sn(i) = sx;
            end
        end
    end

    % --- Residuo armonico, TDD y cumplimiento ---------------------------
    % Todo se mide sobre xh = x - x_star (red distorsionada: el convertidor
    % debe reproducir el fondo para no inyectar corriente).
    xh = zeros(NX, 1);
    tsum = 0;
    for k = 2:N_H
        xh(2*k-1) = x(2*k-1) - x_star(2*k-1);
        xh(2*k)   = x(2*k)   - x_star(2*k);
        tsum = tsum + wk(k)*(xh(2*k-1)^2 + xh(2*k)^2);
    end
    tc = sqrt(tsum)*100;
    vn = tc/TDD_MAX;                  % merito normativo: > 1 fuera de norma
    for k = 2:N_H
        e2 = xh(2*k-1)^2 + xh(2*k)^2;
        viop(k) = double(e2 > EPSN2(k));
        if e2 > vn*vn*EPSN2(k), vn = sqrt(e2/EPSN2(k)); end
    end
    fuera = (vn > 1);
    % Vigia de estancamiento: N_STK superciclos fuera de norma sin que el
    % merito baje un 5% -> rotar semilla.
    if vn <= 1 || vn < 0.95*vbst
        vbst = min(vbst, vn);  nstk = 0;
        if vn <= 1, vbst = Inf; end
    else
        nstk = nstk + 1;
        if nstk >= N_STK, frot = true; end
    end

    % --- MULTIPLICADORES -------------------------------------------------
    % Cada restriccion multiplica su peso por lo que se pasa (o le falta)
    % respecto de su objetivo.  El factor se acota a [F_DN, F_UP] para que
    % un salto grande no dispare el peso en un solo superciclo.
    rT  = tc/(TDD_FRAC*TDD_MAX);
    thT = upd_theta(thT, rT, BETA, F_DN, F_UP, TH_MIN, TH_MAX);
    % Pesos de la FO:  fundamental 1,  armonico k  (W_TDD + thT + th_k)*w_k.
    % (Se probo sumar un termino proporcional theta*razon^p: empeora la
    % robustez desde semillas malas.  Queda solo el integrador.)
    qw = zeros(NXT, 1);
    qw(1) = 1;  qw(2) = 1;
    for k = 2:N_H
        r = sqrt(xh(2*k-1)^2 + xh(2*k)^2)/EPS(k);
        th(k) = upd_theta(th(k), r, BETA, F_DN, F_UP, TH_MIN, TH_MAX);
        q = (W_TDD + thT + th(k))*wk(k);
        qw(2*k-1) = q;  qw(2*k) = q;
    end
    % Risado lado convertidor: peso fijo, objetivo 0 (x_star no tiene
    % fondo de red sobre 49).
    for kr = 1:N_R
        qw(NX+2*kr-1) = WR(kr);  qw(NX+2*kr) = WR(kr);
    end

    % --- rhs = J'*Q*(x* - x) + perdidas ---------------------------------
    rq = zeros(NXT, 1);
    rq(1) = x_star(1) - x(1);  rq(2) = x_star(2) - x(2);
    for r = 3:NX, rq(r) = -qw(r)*xh(r); end
    for r = NX+1:NXT, rq(r) = -qw(r)*x(r); end
    rhs = zeros(N, 1);
    for i = 1:N
        s = 0;
        for r = 1:NXT, s = s + J(r,i)*rq(r); end
        rhs(i) = s;
    end

    % Perdidas: residuos T0 (conduccion, signo -) y S0 (conmutacion),
    % evaluados en g - PHI.  BP y BS son bloques diagonales: solo bandas.
    cc = I_CON^2*R_ON;
    cP = cos(PHI);  sP = sin(PHI);
    sT = 0;  sS = 0;
    for i = 1:D
        id = i + D;
        si = sg(i)*cP  - cg(i)*sP;    ci = cg(i)*cP  + sg(i)*sP;
        sd = sg(id)*cP - cg(id)*sP;   cd = cg(id)*cP + sg(id)*sP;
        T0i = (g0(id) - pi - g0(i))/2 - (2*sd*cd - 2*si*ci)/4;
        S0i = E_ON*abs(si) + E_OFF*abs(sd);
        p1 = si*si;  p2 = sd*sd;
        s1 = -E_ON*ci*sign(si);  s2 = -E_OFF*cd*sign(sd);
        bd1(i) = LAMBDA_LOSS*(-cc*p1*p1 + s1*s1);
        bd2(i) = LAMBDA_LOSS*(-cc*p2*p2 + s2*s2);
        bdx(i) = LAMBDA_LOSS*( cc*p1*p2 + s1*s2);
        rhs(i)  = rhs(i)  + LAMBDA_LOSS*(-cc*p1*T0i + s1*S0i);
        rhs(id) = rhs(id) + LAMBDA_LOSS*( cc*p2*T0i + s2*S0i);
        sT = sT + T0i;  sS = sS + S0i;
    end

    % Barrera del poliedro:  -MU_B*sum(log(s)),  s = holgura de cada fila.
    % Su gradiente va al rhs y su hessiano (casi todo ceros) se suma a W
    % en la fase 3.  Asi el paso de GN ya "ve" el orden, los niveles y la
    % caja, y dos pulsos que se acercan se frenan en vez de chocar.
    [gb, Hb] = barrier(g0, AI1, AI2, AC1, AC2, AH, glo, ghi, MU_B, S_FLR, Hb);
    for i = 1:N, rhs(i) = rhs(i) - gb(i); end

    PLp  = (P_CD0 - C_CD*sT) + (P_SW0 + C_SW*sS);
    TDDp = tc;
    xp = x(1:NX);  Jp = J;  rhsp = rhs;  qwp = qw;
    r1p(1) = x_star(1) - x(1);
    r1p(2) = x_star(2) - x(2);
end


%% ====================================================================
%  3) FASES 1..4: PASO DE GAUSS-NEWTON CON LA FUNDAMENTAL FIJA
%  ====================================================================
%   min_u  1/2*u'*W*u - rhs'*u     s.a.   J1*u = r1
%   W = J'*Q*J + perdidas + LAMBDA_U*I      (Q = diag(qw), con los pesos
%                                           adaptativos de las restricciones)
if ph == 1 || M1
    Wp = build_W_rows(Wp, Jp, qwp, 1, RW1, N, NXT, LAMBDA_U);
end
if ph == 2 || M1
    Wp = build_W_rows(Wp, Jp, qwp, RW1+1, RW2, N, NXT, LAMBDA_U);
end
if ph == 3 || M1
    Wp = build_W_rows(Wp, Jp, qwp, RW2+1, N, N, NXT, LAMBDA_U);
    for i = 1:D
        id = i + D;
        Wp(i,i)   = Wp(i,i)   + bd1(i);
        Wp(id,id) = Wp(id,id) + bd2(i);
        Wp(i,id)  = Wp(i,id)  + bdx(i);
        Wp(id,i)  = Wp(id,i)  + bdx(i);
    end
    Wp = Wp + Hb;
    [Wp, Wpv] = lu_cols(Wp, Wpv, 1, LC1, N);
end
if ph == 4 || M1
    [Wp, Wpv] = lu_cols(Wp, Wpv, LC1+1, N-1, N);

    % Paso libre y las dos columnas de W\J1'
    u  = lu_apply(Wp, Wpv, rhsp, N);
    z1 = lu_apply(Wp, Wpv, Jp(1,:)', N);
    z2 = lu_apply(Wp, Wpv, Jp(2,:)', N);

    % KKT de la igualdad:  u <- u + [z1 z2]*nu,  S*nu = r1 - J1*u,
    % con S = J1*W^-1*J1' (2x2).  Deja J1*u = r1 exacto en el modelo lineal.
    s11 = 0;  s12 = 0;  s22 = 0;  e1 = r1p(1);  e2 = r1p(2);
    for i = 1:N
        s11 = s11 + Jp(1,i)*z1(i);
        s12 = s12 + Jp(1,i)*z2(i);
        s22 = s22 + Jp(2,i)*z2(i);
        e1  = e1  - Jp(1,i)*u(i);
        e2  = e2  - Jp(2,i)*u(i);
    end
    [n1, n2] = solve2(s11, s12, s22, e1, e2);
    nu2 = 0;
    for i = 1:N
        u(i) = u(i) + n1*z1(i) + n2*z2(i);
        nu2  = nu2 + u(i)*u(i);
    end

    % Region de confianza sobre la norma del paso.  En norma, DG_MAX: el
    % error de Taylor no alcanza a sacar ningun armonico.  Fuera de norma,
    % DG_OUT: hay que volver rapido y el lazo exacto corrige el resto.
    dgm = DG_MAX;
    if fuera, dgm = DG_OUT; end
    nu2 = sqrt(nu2);
    if nu2 > dgm
        for i = 1:N, u(i) = u(i)*dgm/nu2; end
    end
    upd = u;
    hpend = true;                     % se publica en la proxima fase 0
end

if ~M1
    ph = ph + 1;
    if ph >= M_CYC, ph = 0; end
end


%% ====================================================================
%  4) TRIM DE FUNDAMENTAL Y VIGIA                  [TODAS LAS MUESTRAS]
%  ====================================================================
% Newton de norma minima en el espacio EXACTO, contra el x_star mas
% reciente, alternado con clamp_angles.  Es la ultima palabra sobre gamma.
K2F = 2/pi;
fa = 0;  fb = 0;  r1f = 0;  r2f = 0;
for it = 1:FT_IT+1
    fa = 0;  fb = 0;  s11 = 0;  s12 = 0;
    for i = 1:N
        ci = cos(gamma_p(i));  si = sin(gamma_p(i));
        fa = fa - si;  fb = fb + ci;
        s11 = s11 + ci*ci;  s12 = s12 + ci*si;
    end
    fa = K2F*fa;  fb = K2F*fb;
    r1f = x_star(1) - fa;  r2f = x_star(2) - fb;
    if r1f*r1f + r2f*r2f < FT_TOL*FT_TOL, break; end
    if it > FT_IT, break; end
    kk = K2F*K2F;
    [z1f, z2f] = solve2(kk*s11 + 1e-9, kk*s12, kk*(N - s11) + 1e-9, r1f, r2f);
    dgf = zeros(N, 1);  nf = 0;
    for i = 1:N
        dgf(i) = -K2F*(cos(gamma_p(i))*z1f + sin(gamma_p(i))*z2f);
        nf = nf + dgf(i)*dgf(i);
    end
    nf = sqrt(nf);
    if nf > FT_MAX
        for i = 1:N, dgf(i) = dgf(i)*FT_MAX/nf; end
    end
    gamma_p = clamp_angles(gamma_p + dgf, D, LVL_C, EPS_SEP, glo, ghi);
end

% Vigia: fundamental fuera de FT_BAD por N_FBAD muestras -> re-siembra.
if r1f*r1f + r2f*r2f > FT_BAD*FT_BAD
    nfb = nfb + 1;
    if nfb >= N_FBAD, nfb = 0;  frf = true;  imp = 0; end
else
    nfb = 0;
end


%% ====================================================================
%  5) SALIDAS
%  ====================================================================
xp(1) = fa;  xp(2) = fb;          % fundamental exacta de este gamma
x_final  = xp;
TDD      = TDDp;
P_loss   = PLp;
ieee_vio = viop;

% Espectro de voltaje de diagnostico hasta NV_H, sobre el gamma que sale
% en esta muestra (despues del trim).  Solo observa: no realimenta nada.
v_harm = volt_spectrum(gamma_p, NV_L, NV_H, NV_K);
vhp    = v_harm;

% Fusion de los dos semiciclos (ya ordenados): O(2D), sin sort.
alpha = zeros(1, N);  du = zeros(1, N);
ia = 1;  ib = D+1;
for r = 1:N
    if ia <= D && (ib > N || gamma_p(ia) <= gamma_p(ib) - pi)
        alpha(r) = gamma_p(ia);       du(r) =  1;  ia = ia + 1;
    else
        alpha(r) = gamma_p(ib) - pi;  du(r) = -1;  ib = ib + 1;
    end
end
angle_f = [alpha*(1/fg)/2/pi, (1/fg)/2 + alpha*(1/fg)/2/pi];
delta_u = [cumsum(du, 2), -cumsum(du, 2)];
angf_p = angle_f;
du_p   = delta_u;
end


% =====================================================================
%  AUXILIARES
% =====================================================================

function v = volt_spectrum(g, nl, nv, nk)
%VOLT_SPECTRUM  Magnitud del armonico de voltaje |V_n| para n impar, no
%   multiplo de 3, nl <= n <= nv.  v(j) = |V_n(j)|, en orden creciente de n
%   (nk filas).
%   Mismo modelo que la fase 0 (valido para n impar):
%       a_n = -2/(n*pi)*sum(sin(n*g)),   b_n = 2/(n*pi)*sum(cos(n*g))
%       |V_n| = 2/(n*pi)*sqrt(sum(cos(n*g))^2 + sum(sin(n*g))^2)
%   La recurrencia recorre todos los impares desde 1 (los que quedan fuera
%   del rango o son multiplos de 3 se calculan de paso pero no se suman).
%   cos(n*g) y sin(n*g) por recurrencia de Chebyshev en pasos de 2:
%       c_(n+2) = 2*cos(2g)*c_n - c_(n-2)   (idem para sin)
    n2 = numel(g);
    v  = zeros(nk, 1);
    j  = 0;
    cg = cos(g);  sg = sin(g);
    t2 = 2*(2*(cg.*cg) - 1);           % 2*cos(2g)
    cn = cg;  sn = sg;  cq = cg;  sq = -sg;
    for n = 1:2:nv
        if n >= nl && mod(n, 3) ~= 0 && j < nk
            sc = 0;  ss = 0;
            for i = 1:n2
                sc = sc + cn(i);  ss = ss + sn(i);
            end
            j = j + 1;
            v(j) = 2/(n*pi)*sqrt(sc*sc + ss*ss);
        end
        if n + 2 <= nv
            for i = 1:n2
                cx = t2(i)*cn(i) - cq(i);  sx = t2(i)*sn(i) - sq(i);
                cq(i) = cn(i);  sq(i) = sn(i);  cn(i) = cx;  sn(i) = sx;
            end
        end
    end
end


function [i1, i2, c1, c2, h] = ang_rows(D, lvl_c, eps_sep)
%ANG_ROWS  Filas del poliedro de angulos SIN la caja, en la forma
%       c1*g(i1) + c2*g(i2) <= h
%   Son las mismas que impone clamp_angles:
%     orden en cada semiciclo   g(i) - g(i+1)            <= -eps_sep
%     cruce por pi              g(D) <= pi - eps_sep/2,  -g(D+1) <= -pi - eps_sep/2
%     niveles                   g(i+D) - g(i+lvl_c)      <= pi
%                               g(i) - g(i+D+lvl_c)      <= -pi
    nc = D - lvl_c;
    m  = 2*(D-1) + 2 + 2*nc;
    i1 = ones(m, 1);  i2 = ones(m, 1);  c1 = zeros(m, 1);  c2 = zeros(m, 1);
    h  = zeros(m, 1);
    r = 0;
    for s = 0:1
        for i = 1:D-1
            r = r + 1;
            i1(r) = s*D + i;  i2(r) = s*D + i + 1;  c1(r) = 1;  c2(r) = -1;
            h(r) = -eps_sep;
        end
    end
    r = r + 1;  i1(r) = D;    i2(r) = D;    c1(r) =  1;  h(r) =  pi - eps_sep/2;
    r = r + 1;  i1(r) = D+1;  i2(r) = D+1;  c1(r) = -1;  h(r) = -pi - eps_sep/2;
    for i = 1:nc
        r = r + 1;
        i1(r) = i + D;  i2(r) = i + lvl_c;      c1(r) = 1;  c2(r) = -1;  h(r) =  pi;
        r = r + 1;
        i1(r) = i;      i2(r) = i + D + lvl_c;  c1(r) = 1;  c2(r) = -1;  h(r) = -pi;
    end
end


function [gb, H] = barrier(g, i1, i2, c1, c2, h, glo, ghi, mu, sf, H)
%BARRIER  Gradiente y hessiano de  -mu*sum(log(s))  sobre las filas del
%   poliedro y la caja [glo, ghi].  Cada fila toca a lo mas 2 angulos, asi
%   que el hessiano se arma por entradas.  s se evalua con piso sf.
    n = numel(g);
    gb = zeros(n, 1);
    for j = 1:n
        for i = 1:n, H(i,j) = 0; end
    end
    for r = 1:numel(h)
        a = i1(r);  b = i2(r);
        s = h(r) - c1(r)*g(a) - c2(r)*g(b);
        if s < sf, s = sf; end
        p = mu/s;  q = mu/(s*s);
        gb(a) = gb(a) + p*c1(r);
        H(a,a) = H(a,a) + q*c1(r)*c1(r);
        if c2(r) ~= 0
            gb(b) = gb(b) + p*c2(r);
            H(b,b) = H(b,b) + q*c2(r)*c2(r);
            H(a,b) = H(a,b) + q*c1(r)*c2(r);
            H(b,a) = H(b,a) + q*c1(r)*c2(r);
        end
    end
    for i = 1:n
        sl = g(i) - glo(i);  if sl < sf, sl = sf; end
        sh = ghi(i) - g(i);  if sh < sf, sh = sf; end
        gb(i)  = gb(i) - mu/sl + mu/sh;
        H(i,i) = H(i,i) + mu/(sl*sl) + mu/(sh*sh);
    end
end


function a = frac_bound(g, u, i1, i2, c1, c2, h, glo, ghi, tau)
%FRAC_BOUND  Mayor a en (0, 1] tal que g + a*u consume a lo mas la
%   fraccion tau de la holgura de cada fila del poliedro y de la caja.
    a = 1;
    for r = 1:numel(h)
        d = c1(r)*u(i1(r)) + c2(r)*u(i2(r));
        if d > 0
            s = h(r) - c1(r)*g(i1(r)) - c2(r)*g(i2(r));
            if s < 0, s = 0; end
            if tau*s < a*d, a = tau*s/d; end
        end
    end
    for i = 1:numel(g)
        if u(i) < 0
            s = g(i) - glo(i);  if s < 0, s = 0; end
            if tau*s < -a*u(i), a = -tau*s/u(i); end
        elseif u(i) > 0
            s = ghi(i) - g(i);  if s < 0, s = 0; end
            if tau*s < a*u(i), a = tau*s/u(i); end
        end
    end
end

function t = upd_theta(t, r, beta, fdn, fup, tmin, tmax)
%UPD_THETA  Integrador logaritmico de un multiplicador:  t <- t*r^beta,
%   con el factor acotado a [fdn, fup] y el resultado a [tmin, tmax].
    f = r^beta;
    if f < fdn, f = fdn; end
    if f > fup, f = fup; end
    t = t*f;
    if t < tmin, t = tmin; end
    if t > tmax, t = tmax; end
end


function W = build_W_rows(W, J, q, i0, i1, n, nx, lam)
%BUILD_W_ROWS  Filas i0..i1 de W = J'*diag(q)*J + lam*I (triangulo
%   superior espejado).  Reanudable por tramos de filas.
    v = zeros(nx, 1);
    for i = i0:i1
        for r = 1:nx, v(r) = q(r)*J(r,i); end
        for jj = i:n
            s = 0;
            for r = 1:nx, s = s + v(r)*J(r,jj); end
            W(i,jj) = s;  W(jj,i) = s;
        end
        W(i,i) = W(i,i) + lam;
    end
end


function [A, pv] = lu_cols(A, pv, k0, k1, n)
%LU_COLS  Eliminacion gaussiana con pivoteo parcial, columnas k0..k1, in
%   situ.  Reanudable: (1,a) y luego (a+1,n-1) = una sola llamada (1,n-1).
    for k = k0:k1
        p = k;  am = abs(A(k,k));
        for i = k+1:n
            if abs(A(i,k)) > am, am = abs(A(i,k));  p = i; end
        end
        pv(k) = p;
        if p ~= k
            for j = 1:n
                t = A(k,j);  A(k,j) = A(p,j);  A(p,j) = t;
            end
        end
        if abs(A(k,k)) < 1e-12
            if A(k,k) < 0, A(k,k) = -1e-12; else, A(k,k) = 1e-12; end
        end
        for i = k+1:n
            f = A(i,k)/A(k,k);
            A(i,k) = f;
            if f ~= 0
                for j = k+1:n, A(i,j) = A(i,j) - f*A(k,j); end
            end
        end
    end
    if k1 == n-1 && abs(A(n,n)) < 1e-12
        if A(n,n) < 0, A(n,n) = -1e-12; else, A(n,n) = 1e-12; end
    end
end


function x = lu_apply(A, pv, b, n)
%LU_APPLY  Resuelve con la LU de lu_cols (permutacion completa primero).
    for k = 1:n-1
        p = pv(k);
        if p ~= k, t = b(k);  b(k) = b(p);  b(p) = t; end
    end
    for k = 1:n-1
        for i = k+1:n, b(i) = b(i) - A(i,k)*b(k); end
    end
    x = zeros(n, 1);
    for i = n:-1:1
        s = b(i);
        for j = i+1:n, s = s - A(i,j)*x(j); end
        x(i) = s/A(i,i);
    end
end


function [y1, y2] = solve2(a, b, c, x1, x2)
%SOLVE2  Resuelve [a b; b c]*y = x en forma cerrada.
    dt = a*c - b*b;
    if abs(dt) < 1e-300, dt = 1e-300; end
    y1 = ( c*x1 - b*x2)/dt;
    y2 = (-b*x1 + a*x2)/dt;
end


function g = clamp_angles(g, D, lvl_c, eps_sep, glo, ghi)
%CLAMP_ANGLES  Proyecciones alternadas sobre el poliedro de angulos:
%   niveles, caja [glo, ghi], orden estricto y cruce por pi.
    n2 = 2*D;
    for it = 1:6
        mv = 0;
        for i = 1:D-lvl_c
            e = g(i+D) - g(i+lvl_c) - pi;
            if e > 0
                g(i+D) = g(i+D) - e/2;  g(i+lvl_c) = g(i+lvl_c) + e/2;
                if e > mv, mv = e; end
            end
        end
        for i = 1:D-lvl_c
            e = pi - (g(i+D+lvl_c) - g(i));
            if e > 0
                g(i+D+lvl_c) = g(i+D+lvl_c) + e/2;  g(i) = g(i) - e/2;
                if e > mv, mv = e; end
            end
        end
        for i = 1:n2
            if g(i) < glo(i)
                g(i) = glo(i);
            elseif g(i) > ghi(i)
                g(i) = ghi(i);
            end
        end
        for i = 1:D-1
            e = g(i) + eps_sep - g(i+1);
            if e > 0
                g(i) = g(i) - e/2;  g(i+1) = g(i+1) + e/2;
                if e > mv, mv = e; end
            end
        end
        e = g(D) - (pi - eps_sep*0); % CAMBIO
        if e > 0, g(D) = pi - eps_sep/2;  if e > mv, mv = e; end, end
        e = (pi + eps_sep*0) - g(D+1); % CAMBIO
        if e > 0, g(D+1) = pi + eps_sep/2;  if e > mv, mv = e; end, end
        for i = D+1:n2-1
            e = g(i) + eps_sep - g(i+1);
            if e > 0
                g(i) = g(i) - e/2;  g(i+1) = g(i+1) + e/2;
                if e > mv, mv = e; end
            end
        end
        if mv < 1e-10, break; end
    end
end


function k = hyst_idx(v, tab, k0, n, hf, ha)
%HYST_IDX  Indice de la celda mas cercana a v, con histeresis.  Sin estado
%   previo (k0 = 0) es el vecino mas cercano.  Con estado, solo se cambia de
%   celda al cruzar el punto medio mas un margen min(max(hf*paso, ha), 0.4*paso).
    if n <= 1
        k = 1;
        return;
    end
    if k0 < 1 || k0 > n
        k = 1;  db = abs(v - tab(1));
        for i = 2:n
            if abs(v - tab(i)) < db, db = abs(v - tab(i));  k = i; end
        end
        return;
    end
    k = k0;
    if isinf(hf), return; end
    while k < n
        s = tab(k+1) - tab(k);  mg = min(max(hf*s, ha), 0.4*s);
        if v > 0.5*(tab(k) + tab(k+1)) + mg, k = k + 1; else, break; end
    end
    while k > 1
        s = tab(k) - tab(k-1);  mg = min(max(hf*s, ha), 0.4*s);
        if v < 0.5*(tab(k-1) + tab(k)) - mg, k = k - 1; else, break; end
    end
end
