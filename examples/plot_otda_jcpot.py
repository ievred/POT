# -*- coding: utf-8 -*-
"""
========================
OT for multi-source target shift
========================

This example introduces a target shift problem with two 2D source and 1 target domain.

"""

# Authors: Remi Flamary <remi.flamary@unice.fr>
#          Ievgen Redko <ievgen.redko@univ-st-etienne.fr>
#
# License: MIT License

import pylab as pl
import numpy as np
import ot

##############################################################################
# Generate data
# -------------
n = 50
sigma = 0.3
np.random.seed(1985)


def get_data(n, p, dec):
    y = np.concatenate((np.ones(int(p * n)), np.zeros(int((1 - p) * n))))
    x = np.hstack((0 * y[:, None] - 0, 1 - 2 * y[:, None])) + sigma * np.random.randn(len(y), 2)

    x[:, 0] += dec[0]
    x[:, 1] += dec[1]

    return x, y


p1 = .2
dec1 = [0, 2]

p2 = .9
dec2 = [0, -2]

pt = .4
dect = [4, 0]

xs1, ys1 = get_data(n, p1, dec1)
xs2, ys2 = get_data(n + 1, p2, dec2)
xt, yt = get_data(n, pt, dect)
all_Xr = [xs1, xs2]
all_Yr = [ys1, ys2]
# %%
da = 1.5


def plot_ax(dec, name):
    pl.plot([dec[0], dec[0]], [dec[1] - da, dec[1] + da], 'k', alpha=0.5)
    pl.plot([dec[0] - da, dec[0] + da], [dec[1], dec[1]], 'k', alpha=0.5)
    pl.text(dec[0] - .5, dec[1] + 2, name)


##############################################################################
# Fig 1 : plots source and target samples
# ---------------------------------------

pl.figure(1)
pl.clf()
plot_ax(dec1, 'Source 1')
plot_ax(dec2, 'Source 2')
plot_ax(dect, 'Target')
pl.scatter(xs1[:, 0], xs1[:, 1], c=ys1, s=35, marker='x', cmap='Set1', vmax=9, label='Source 1 (0.8,0.2)')
pl.scatter(xs2[:, 0], xs2[:, 1], c=ys2, s=35, marker='+', cmap='Set1', vmax=9, label='Source 2 (0.1,0.9)')
pl.scatter(xt[:, 0], xt[:, 1], c=yt, s=35, marker='o', cmap='Set1', vmax=9, label='Target (0.6,0.4)')
pl.title('Data')

pl.legend()
pl.axis('equal')
pl.axis('off')


##############################################################################
# Instantiate Sinkhorn transport algorithm and fit them for all source domains
# ----------------------------------------------------------------------------
ot_sinkhorn = ot.da.SinkhornTransport(reg_e=1e-2, metric='euclidean')

M1 = ot.dist(xs1, xt, 'euclidean')
M2 = ot.dist(xs2, xt, 'euclidean')


def print_G(G, xs, ys, xt):
    for i in range(G.shape[0]):
        for j in range(G.shape[1]):
            if G[i, j] > 5e-4:
                if ys[i]:
                    c = 'b'
                else:
                    c = 'r'
                pl.plot([xs[i, 0], xt[j, 0]], [xs[i, 1], xt[j, 1]], c, alpha=.2)


##############################################################################
# Fig 2 : plot optimal couplings and transported samples
# ------------------------------------------------------
pl.figure(2)
pl.clf()
plot_ax(dec1, 'Source 1')
plot_ax(dec2, 'Source 2')
plot_ax(dect, 'Target')
print_G(ot_sinkhorn.fit(Xs=xs1, Xt=xt).coupling_, xs1, ys1, xt)
print_G(ot_sinkhorn.fit(Xs=xs2, Xt=xt).coupling_, xs2, ys2, xt)
pl.scatter(xs1[:, 0], xs1[:, 1], c=ys1, s=35, marker='x', cmap='Set1', vmax=9)
pl.scatter(xs2[:, 0], xs2[:, 1], c=ys2, s=35, marker='+', cmap='Set1', vmax=9)
pl.scatter(xt[:, 0], xt[:, 1], c=yt, s=35, marker='o', cmap='Set1', vmax=9)

pl.plot([], [], 'r', alpha=.2, label='Mass from Class 1')
pl.plot([], [], 'b', alpha=.2, label='Mass from Class 2')

pl.title('Independent OT')

pl.legend()
pl.axis('equal')
pl.axis('off')


##############################################################################
# Instantiate JCPOT adaptation algorithm and fit it
# ----------------------------------------------------------------------------
otda = ot.da.JCPOTTransport(reg_e=1e-2, max_iter=1000, tol=1e-9, verbose=True, log=True)
otda.fit(all_Xr, all_Yr, xt)

ws1 = otda.proportions_.dot(otda.log_['all_domains'][0]['D2'])
ws2 = otda.proportions_.dot(otda.log_['all_domains'][1]['D2'])

pl.figure(3)
pl.clf()
plot_ax(dec1, 'Source 1')
plot_ax(dec2, 'Source 2')
plot_ax(dect, 'Target')
print_G(ot.bregman.sinkhorn(ws1, [], M1, reg=1e-2), xs1, ys1, xt)
print_G(ot.bregman.sinkhorn(ws2, [], M2, reg=1e-2), xs2, ys2, xt)
pl.scatter(xs1[:, 0], xs1[:, 1], c=ys1, s=35, marker='x', cmap='Set1', vmax=9)
pl.scatter(xs2[:, 0], xs2[:, 1], c=ys2, s=35, marker='+', cmap='Set1', vmax=9)
pl.scatter(xt[:, 0], xt[:, 1], c=yt, s=35, marker='o', cmap='Set1', vmax=9)

pl.plot([], [], 'r', alpha=.2, label='Mass from Class 1')
pl.plot([], [], 'b', alpha=.2, label='Mass from Class 2')

pl.title('OT with prop estimation ({:1.3f},{:1.3f})'.format(otda.proportions_[0], otda.proportions_[1]))

pl.legend()
pl.axis('equal')
pl.axis('off')

##############################################################################
# Run oracle transport algorithm with known proportions
# ----------------------------------------------------------------------------

otda = ot.da.JCPOTTransport(reg_e=0.01, max_iter=1000, tol=1e-9, verbose=True, log=True)
otda.fit(all_Xr, all_Yr, xt)

h_res = np.array([1 - pt, pt])

ws1 = h_res.dot(otda.log_['all_domains'][0]['D2'])
ws2 = h_res.dot(otda.log_['all_domains'][1]['D2'])

pl.figure(4)
pl.clf()
plot_ax(dec1, 'Source 1')
plot_ax(dec2, 'Source 2')
plot_ax(dect, 'Target')
print_G(ot.bregman.sinkhorn(ws1, [], M1, reg=1e-2), xs1, ys1, xt)
print_G(ot.bregman.sinkhorn(ws2, [], M2, reg=1e-2), xs2, ys2, xt)
pl.scatter(xs1[:, 0], xs1[:, 1], c=ys1, s=35, marker='x', cmap='Set1', vmax=9)
pl.scatter(xs2[:, 0], xs2[:, 1], c=ys2, s=35, marker='+', cmap='Set1', vmax=9)
pl.scatter(xt[:, 0], xt[:, 1], c=yt, s=35, marker='o', cmap='Set1', vmax=9)

pl.plot([], [], 'r', alpha=.2, label='Mass from Class 1')
pl.plot([], [], 'b', alpha=.2, label='Mass from Class 2')

pl.title('OT with known proportion ({:1.1f},{:1.1f})'.format(h_res[0], h_res[1]))

pl.legend()
pl.axis('equal')
pl.axis('off')
pl.show()