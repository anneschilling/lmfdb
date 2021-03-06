# Different helper functions.

import re
from lmfdb.lfunctions import logger
from sage.all import *


###############################################################
# Functions for displaying numbers in correct format etc.
###############################################################

def pair2complex(pair):
    ''' Turns the pair into a complex number.
    '''
    local = re.match(" *([^ ]+)[ \t]*([^ ]*)", pair)
    if local:
        rp = local.group(1)
        if local.group(2):
            ip = local.group(2)
        else:
            ip = 0
    else:
        rp = 0
        ip = 0
    return float(rp) + float(ip) * I


def splitcoeff(coeff):
    local = coeff.split("\n")
    answer = []
    for s in local:
        if s:
            answer.append(pair2complex(s))

    return answer


def truncatenumber(numb, precision):
    localprecision = precision
    if numb < 0:
        localprecision = localprecision + 1
    return(str(numb)[0:int(localprecision)])


def styleTheSign(sign):
    ''' Returns the string to display as sign
    '''
    try:
        logger.debug(1 - sign)
        if sign == 0:
            return "unknown"
        if abs(1 - sign) < 1e-10:
            return '1'
        elif abs(1 + sign) < 1e-10:
            return '-1'
        elif abs(1 - sign.imag()) < 1e-10:
            return 'i'
        elif abs(1 + sign.imag()) < 1e-10:
            return '-i'
        elif sign.imag > 0:
            return "${0} + {1}i$".format(truncatenumber(sign.real(), 5), truncatenumber(sign.imag(), 5))
        else:
            return "${0} {1}i$".format(truncatenumber(sign.real(), 5), truncatenumber(sign.imag(), 5))
    except:
        logger.debug("no styling of sign")
        return str(sign)


def seriescoeff(coeff, index, seriescoefftype, seriestype, truncationexp, precision):
    truncation = float(10 ** truncationexp)
    if type(coeff) == complex:
        rp = coeff.real
        ip = coeff.imag
    else:
        rp = real_part(coeff)
        ip = imag_part(coeff)
# below we use float(abs()) instead of abs() to avoid a sage bug
    if (float(abs(rp)) > truncation) & (float(abs(ip)) > truncation):
        ans = ""
        if seriescoefftype == "series" or seriescoefftype == "signed":
            ans += "+"
        ans += "("
        ans += truncatenumber(rp, precision)
        if ip > 0:
            ans += "+"
        ans += truncatenumber(ip, precision) + " i"
        return(ans + ")" + seriesvar(index, seriestype))
    elif (float(abs(rp)) < truncation) & (float(abs(ip)) < truncation):
        if seriescoefftype != "literal":
            return("")
        else:
            return("0")
# if we get this far, either pure real or pure imaginary
    ans = ""
#    if seriescoefftype=="series":
#        ans=ans+" + "
# commenting out the above "if" code so as to fix + - problem
    logger.info("rp={0}".format(rp))
    if rp > truncation:
        if float(abs(rp - 1)) < truncation:
            if seriescoefftype == "literal":
                return("1")
            elif seriescoefftype == "signed":
                return("+1")
            elif seriescoefftype == "factor":
                return("")
            elif seriescoefftype == "series":
                return(ans + " + " + seriesvar(index, seriestype))
        else:
            if seriescoefftype == "series":
                return(" + " + ans + truncatenumber(rp, precision) + seriesvar(index, seriestype))
            elif seriescoefftype == "signed":
                return(ans + "+" + truncatenumber(rp, precision))
            elif seriescoefftype == "literal" or seriescoefftype == "factor":
                return(ans + truncatenumber(rp, precision))
    elif rp < -1 * truncation:
        if float(abs(rp + 1)) < truncation:
            if seriescoefftype == "literal":
                return("-1" + seriesvar(index, seriestype))
            elif seriescoefftype == "signed":
                return("-1" + seriesvar(index, seriestype))
            elif seriescoefftype == "factor":
                return("-" + seriesvar(index, seriestype))
            elif seriescoefftype == "series":  # adding space between minus sign and value
                return(" - " + seriesvar(index, seriestype))
            else:
                return("-" + seriesvar(index, seriestype))
        else:
            if seriescoefftype == "series":
                return(ans + " - " + truncatenumber(float(abs(rp)), precision) + seriesvar(index, seriestype))
            elif seriescoefftype == "literal" or seriescoefftype == "factor":
                return(ans + truncatenumber(rp, precision))

# if we get this far, it is pure imaginary
    elif ip > truncation:
        if float(abs(ip - 1)) < truncation:
            if seriescoefftype == "literal":
                return("i")
            elif seriescoefftype == "signed":
                return("+i")
            elif seriescoefftype == "factor":
                return("i")
            elif seriescoefftype == "series":
                return(ans + " + i" + seriesvar(index, seriestype))
        else:
            if seriescoefftype == "series":
                return(ans + truncatenumber(ip, precision) + " + i" + seriesvar(index, seriestype))
            elif seriescoefftype == "signed":
                return(ans + "+" + truncatenumber(ip, precision) + "i")
            elif seriescoefftype == "literal" or seriescoefftype == "factor":
                return(ans + truncatenumber(ip, precision) + "i")
    elif ip < -1 * truncation:
        if float(abs(ip + 1)) < truncation:
            return("-i" + seriesvar(index, seriestype))
        else:
            if seriescoefftype == "series":
                return(ans + truncatenumber(ip, precision) + "i" + seriesvar(index, seriestype))
            elif seriescoefftype == "signed":
                return(ans + truncatenumber(ip, precision) + " i")
            elif seriescoefftype == "literal" or seriescoefftype == "factor":
                return(ans + truncatenumber(ip, precision) + " i")

#    elif float(abs(ip+1))<truncation:
#        return("-" + "i"+ seriesvar(index, seriestype))
    else:
        return(latex(coeff) + seriesvar(index, seriestype))


def seriesvar(index, seriestype):
    if seriestype == "dirichlet":
        return(" \\ " + str(index) + "^{-s}")
    elif seriestype == "":
        return("")
    elif seriestype == "qexpansion":
        return("\\, " + "q^{" + str(index) + "}")
    else:
        return("")


def lfuncDStex(L, fmt):
    """ Returns the LaTex for displaying the Dirichlet series of the L-function L.
        fmt could be any of the values: "analytic", "langlands", "abstract"
    """

    if len(L.dirichlet_coefficients) == 0:
        return '\\text{No Dirichlet coefficients supplied.}'

    numperline = 4
    maxcoeffs = 20
    if L.selfdual:
        numperline = 9  # Actually, we want 8 per line, and one extra addition to counter to ensure
                        # we add only one newline
        maxcoeffs = 30
    ans = ""
    # Changes to account for very sparse series, only count actual nonzero terms to decide when to go to next line
    # This actually jumps by 2 whenever we add a newline, to ensure we just add one new line
    nonzeroterms = 1
    if fmt == "analytic" or fmt == "langlands":
        ans = "\\begin{align}\n"
        ans = ans + L.texname + "=" + seriescoeff(L.dirichlet_coefficients[0], 0, "literal", "", -
                                                  6, 5) + "\\mathstrut&"
        for n in range(1, len(L.dirichlet_coefficients)):
            tmp = seriescoeff(L.dirichlet_coefficients[n], n + 1, "series", "dirichlet", -6, 5)
            if tmp != "":
                nonzeroterms += 1
            ans = ans + tmp
            if nonzeroterms > maxcoeffs:
                break
            if(nonzeroterms % numperline == 0):
                ans = ans + "\\cr\n"
                ans = ans + "&"
                nonzeroterms += 1   # This ensures we don t add more than one newline
        ans = ans + " + \\ \\cdots\n\\end{align}"

    elif fmt == "abstract":
        if L.Ltype() == "riemann":
            ans = "\\begin{equation} \n \\zeta(s) = \\sum_{n=1}^{\\infty} n^{-s} \n \\end{equation} \n"

        elif L.Ltype() == "dirichlet":
            ans = "\\begin{equation} \n L(s,\\chi) = \\sum_{n=1}^{\\infty} \\chi(n) n^{-s} \n \\end{equation}"
            ans = ans + "where $\\chi$ is the character modulo " + str(L.charactermodulus)
            ans = ans + ", number " + str(L.characternumber) + "."

        else:
            ans = "\\begin{equation} \n " + L.texname + \
                " = \\sum_{n=1}^{\\infty} a(n) n^{-s} \n \\end{equation}"
    return(ans)

#---------


def lfuncEPtex(L, fmt):
    """ Returns the LaTex for displaying the Euler product of the L-function L.
        fmt could be any of the values: "abstract"
    """

    ans = ""
    if fmt == "abstract":
        if L.Ltype() == "SymmetricPower":
            ans = L.euler
            return ans

        ans = "\\begin{equation} \n " + L.texname + " = "
        if L.Ltype() == "riemann":
            ans = ans + "\\prod_p (1 - p^{-s})^{-1}"
        elif L.Ltype() == "dirichlet":
            ans = ans + "\\prod_p (1- \\chi(p) p^{-s})^{-1}"
        elif L.Ltype() == "ellipticmodularform":
            ans = ans + "\\prod_{p\\ \\mathrm{bad}} (1- a(p) p^{-s})^{-1} \\prod_{p\\ \\mathrm{good}} (1- a(p) p^{-s} + \chi(p)p^{-2s})^{-1}"
        elif L.Ltype() == "hilbertmodularform":
            ans = ans + "\\prod_{\mathfrak{p}\\ \\mathrm{bad}} (1- a(\mathfrak{p}) (N\mathfrak{p})^{-s})^{-1} \\prod_{\mathfrak{p}\\ \\mathrm{good}} (1- a(\mathfrak{p}) (N\mathfrak{p})^{-s} + (N\mathfrak{p})^{-2s})^{-1}"
        elif L.Ltype() == "ellipticcurve":
            ans = ans + "\\prod_{p\\ \\mathrm{bad}} (1- a(p) p^{-s})^{-1} \\prod_{p\\ \\mathrm{good}} (1- a(p) p^{-s} + p^{-2s})^{-1}"
        elif L.Ltype() == "maass":
            if L.group == 'GL2':
                ans = ans + "\\prod_{p\\ \\mathrm{bad}} (1- a(p) p^{-s})^{-1} \\prod_{p\\ \\mathrm{good}} (1- a(p) p^{-s} + \chi(p)p^{-2s})^{-1}"
            elif L.group == 'GL3':
                ans = ans + "\\prod_{p\\ \\mathrm{bad}} (1- a(p) p^{-s})^{-1}  \\prod_{p\\ \\mathrm{good}} (1- a(p) p^{-s} + \\overline{a(p)} p^{-2s} - p^{-3s})^{-1}"
            else:
                ans = ans + "\\prod_p \\ \\prod_{j=1}^{" + str(L.degree) + \
                    "} (1 - \\alpha_{j,p}\\,  p^{-s})^{-1}"

        elif L.langlands:
            if L.degree > 1:
                ans = ans + "\\prod_p \\ \\prod_{j=1}^{" + str(L.degree) + \
                    "} (1 - \\alpha_{j,p}\\,  p^{-s})^{-1}"
            else:
                ans = ans + "\\prod_p \\  (1 - \\alpha_{p}\\,  p^{-s})^{-1}"

        else:
            return("No information is available about the Euler product.")
        ans = ans + " \n \\end{equation}"
        return(ans)
    else:
        return("No information is available about the Euler product.")


#---------


def lfuncFEtex(L, fmt):
    """ Returns the LaTex for displaying the Functional equation of the L-function L.
        fmt could be any of the values: "analytic", "selberg"
    """

    ans = ""
    if fmt == "analytic":
        ans = "\\begin{align}\n" + L.texnamecompleteds + "=\\mathstrut &"
        if L.level > 1:
            # ans+=latex(L.level)+"^{\\frac{s}{2}}"
            ans += latex(L.level) + "^{s/2}"
        for mu in L.mu_fe:
            ans += "\Gamma_{\R}(s" + seriescoeff(mu, 0, "signed", "", -6, 5) + ")"
        for nu in L.nu_fe:
            ans += "\Gamma_{\C}(s" + seriescoeff(nu, 0, "signed", "", -6, 5) + ")"
        ans += " \\cdot " + L.texname + "\\cr\n"
        ans += "=\\mathstrut & "
        if L.sign == 0:
            ans += "\epsilon \cdot "
        else:
            ans += seriescoeff(L.sign, 0, "factor", "", -6, 5)
        ans += L.texnamecompleted1ms
        if L.sign == 0 and L.degree == 1:
            ans += "\quad (\\text{with }\epsilon \\text{ not computed})"
        if L.sign == 0 and L.degree > 1:
            ans += "\quad (\\text{with }\epsilon \\text{ unknown})"
        ans += "\n\\end{align}\n"
    elif fmt == "selberg":
        print L.nu_fe, "!!!!!!!"
        ans += "(" + str(int(L.degree)) + ","
        ans += str(int(L.level)) + ","
        ans += "("
        if L.mu_fe != []:
            for mu in range(len(L.mu_fe) - 1):
                ans += seriescoeff(L.mu_fe[mu], 0, "literal", "", -6, 5) + ", "
            ans += seriescoeff(L.mu_fe[-1], 0, "literal", "", -6, 5)
        ans = ans + ":"
        if L.nu_fe != []:
            for nu in range(len(L.nu_fe) - 1):
                ans += str(L.nu_fe[nu]) + ", "
            ans += str(L.nu_fe[-1])
        ans += "), "
        ans += seriescoeff(L.sign, 0, "literal", "", -6, 5)
        ans += ")"

    return(ans)


def specialValueString(L, s, sLatex):
    ''' Returns the LaTex to dislpay for L(s)
    '''
    number_of_decimals = 10
    val = L.sageLfunction.value(s)
    lfunction_value_tex = L.texname.replace('(s', '(' + sLatex)
    # We must test for NaN first, since it would show as zero otherwise
    # Try "RR(NaN) < float(1e-10)" in sage -- GT
    if val.real().is_NaN():
        return "\\[{0}=\\infty\\]".format(lfunction_value_tex)
    elif val.abs() < 1e-10:
        return "\\[{0}=0\\]".format(lfunction_value_tex)
    else:
        return "\\[{0} \\approx {1}\\]".format(lfunction_value_tex,
                                               latex(round(val.real(), number_of_decimals)
                                                     + round(val.imag(), number_of_decimals) * I))


###############################################################
# Functions for Siegel dirichlet series
###############################################################
NN = 500
CF = ComplexField(NN)


def compute_dirichlet_series(p_list, PREC):
    ''' computes the dirichlet series for a Lfunction_SMF2_scalar_valued
    '''
    # p_list is a list of pairs (p,y) where p is a prime and y is the list of roots of the Euler factor at x
    LL = [0] * PREC
    # create an empty list of the right size and now populate it with the powers of p
    for (p, y) in p_list:
        p_prec = log(PREC) / log(p) + 1
        ep = euler_p_factor(y, PREC)
        for n in range(ep.prec()):
            if p ** n < PREC:
                LL[p ** n] = ep.coefficients()[n]
    for i in range(1, PREC):
        f = factor(i)
        if len(f) > 1:  # not a prime power
            LL[i] = prod([LL[p ** e] for (p, e) in f])
    print LL[:5]
    return LL[1:]


def euler_p_factor(root_list, PREC):
    ''' computes the coefficients of the pth Euler factor expanded as a geometric series
      ax^n is the Dirichlet series coefficient p^(-ns)
    '''
    PREC = floor(PREC)
    # return satake_list
    R = LaurentSeriesRing(CF, 'x')
    x = R.gens()[0]
    ep = prod([1 / (1 - a * x) for a in root_list])
    return ep + O(x ** (PREC + 1))


def compute_local_roots_SMF2_scalar_valued(ev_data, k, embedding):
    ''' computes the dirichlet series for a Lfunction_SMF2_scalar_valued
    '''

    logger.debug("Start SMF2")
    K = ev_data[0].parent().fraction_field()  # field of definition for the eigenvalues
    ev = ev_data[1]  # dict of eigenvalues
    print "ev=--------->>>>>>>", ev
    L = ev.keys()
    m = ZZ(max(L)).isqrt() + 1
    ev2 = {}
    for p in primes(m):

        try:
            ev2[p] = (ev[p], ev[p * p])
        except:
            break

    logger.debug(str(ev2))
    ret = []
    for p in ev2:
        R = PolynomialRing(K, 'x')
        x = R.gens()[0]

        f = (1 - ev2[p][0] * x + (ev2[p][0] ** 2 - ev2[p][1] - p ** (
            2 * k - 4)) * x ** 2 - ev2[p][0] * p ** (2 * k - 3) * x ** 3 + p ** (4 * k - 6) * x ** 4)

        Rnum = PolynomialRing(CF, 'y')
        x = Rnum.gens()[0]
        fnum = Rnum(0)
        if K != QQ:
            for i in range(int(f.degree()) + 1):
                fnum = fnum + f[i].complex_embeddings(NN)[embedding] * (x / p ** (k - 1.5)) ** i
        else:
            for i in range(int(f.degree()) + 1):
                fnum = fnum + f[i] * (x / CF(p ** (k - 1.5))) ** i

        r = fnum.roots(CF)
        r = [1 / a[0] for a in r]
        # a1 = r[1][0]/r[0][0]
        # a2 = r[2][0]/r[0][0]
        # a0 = 1/r[3][0]

        ret.append((p, r))

    return ret


###############################################################
# Functions for computing the number of coefficients needed
# in order to be able to show plot and compute zeros.
###############################################################
def number_of_coefficients_needed(Q, kappa_fe, lambda_fe, max_t):
    # TODO: This doesn't work. Trouble when computing t0
    # We completely mimic what lcalc does when it decides whether
    # to print a warning.

    DIGITS = 14    # These are names of lcalc parameters, and we are
    DIGITS2 = 2    # mimicking them.

    logger.debug("Start NOC")
    theta = sum(kappa_fe)
    c = DIGITS2 * log(10.0)
    a = len(kappa_fe)

    c1 = 0.0
    for j in range(a):
        logger.debug("In loop NOC")
        t0 = kappa_fe[j] * max_t + complex(lambda_fe[j]).imag()
        logger.debug("In loop 2 NOC")
        if abs(t0) < 2 * c / (math.pi * a):
            logger.debug("In loop 3_1 NOC")
            c1 += kappa_fe[j] * pi / 2.0
        else:
            c1 += kappa_fe[j] * abs(c / (t0 * a))
            logger.debug("In loop 3_2 NOC")

    return int(round(Q * exp(log(2.3 * DIGITS * theta / c1) * theta) + 10))


###############################################################
# Functions for cusp forms
###############################################################


def signOfEmfLfunction(level, weight, coefs, tol=10 ** (-7), num=1.3):
    """ Computes the sign of a EMF with give level, weight and
        coefficients numerically by computing the value of the EMF
        at two points related by the Atkin-Lehner involution.
        If the absolute value of the result is more than tol from 1
        then it returns "Not able to compute" which indicates to few
        (or wrong) coeffcients.
        The parameter num chooses the related points and shouldn't be 1.
    """
    sum1 = 0
    sum2 = 0
    for i in range(1, len(coefs)):
        sum1 += coefs[i - 1] * math.exp(- 2 * math.pi * i * num / math.sqrt(level))
        logger.debug("Sum1: {0}".format(sum1))
        sum2 += coefs[i - 1].conjugate() * math.exp(- 2 * math.pi * i / num / math.sqrt(level)) / \
            num ** weight
        logger.debug("Sum2: {0}".format(sum2))
    sign = sum1 / sum2
    if abs(abs(sign) - 1) > tol:
        logger.critical("Not enough coefficients to compute the sign of the L-function.")
        sign = "Not able to compute."
    return sign
