"""
Module of plotting functions.
"""

# imports

from lo_tools import Lfun, zfun, zrfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()
if Ldir['lo_env'] == 'pm_mac': # mac version
    pass
else: # remote linux version
    import matplotlib as mpl
    mpl.use('Agg')

from importlib import reload
import dm_pfun; reload(dm_pfun)
import pinfo; reload(pinfo)

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def P1(Q, M):
    fig = plt.figure(figsize=(6.5,12))
    fs=18
    plt.rc('font', size=fs)
    
    ds = xr.open_dataset(Q['fn'])
    if Q['dom'] == 'full':
        Q['aa'] = pfun.get_aa(ds)
    aa = Q['aa']
    
    vn = Q['vn']
    if Q['bot']:
        nlev = 0
        tstr = 'Bottom'
    else:
        nlev = -1
        tstr = 'Surface'
        
    px, py = pfun.get_plon_plat(ds['lon_rho'].values, ds['lat_rho'].values)
    if vn == 'speed':
        fld = dm_pfun.get_speed(ds, nlev)
    elif vn == 'ARAG':
        px, py, fld = dm_pfun.get_arag(ds, Q, aa, nlev)
        # we get px, py because ARAG is automatically only calulated over
        # a limited domain (aa)
    else:
        fld = ds[vn][0,nlev,:,:].values*pinfo.fac_dict[vn]
        
    if Q['emask']:
        fld = dm_pfun.mask_edges(ds, fld, Q)
    if Q['avl']:
        # set vmax and vmin if needed
        dm_pfun.get_vlims(ds, fld, Q)
        
    # MAP FIELD
    ax = plt.subplot2grid((7,1), (0,0), rowspan=6)
    cs = ax.pcolormesh(px, py, fld,
        cmap=pinfo.cmap_dict[vn], vmin=Q['vmin'], vmax=Q['vmax'])
    ax.text(.95, .99,'%s %s %s' % (tstr, pinfo.tstr_dict[vn],pinfo.units_dict[vn]),
        transform=ax.transAxes, ha='right', va='top', weight='bold')
    
    if Q['dom'] == 'full':
        dm_pfun.add_bathy_contours(ax, ds, depth_levs=[200])
    elif Q['dom'] == 'nshelf':
        dm_pfun.add_bathy_contours(ax, ds, depth_levs=[100, 200], c='c', lw=1)
        
    if vn == 'speed':
        dm_pfun.add_velocity_vectors(ax, aa, ds, Q['fn'], v_scl=Q['v_scl'])
        
    pfun.add_coast(ax, color='k')
    ax.axis(aa)
    pfun.dar(ax)
    dm_pfun.add_f_stamp(ax, Q)
        
    # Inset colorbar
    cbaxes = inset_axes(ax, width="40%", height="4%", loc='upper right', borderpad=2) 
    cb = fig.colorbar(cs, cax=cbaxes, orientation='horizontal')
    
    # Mooring location
    ax.plot(M['lon'], M['lat'],'ok', ms=5)
    
    # Wind vector
    T = zrfun.get_basic_info(Q['fn'], only_T=True)
    dm_pfun.add_wind(ax, M, T)
    dm_pfun.add_wind_text(ax, aa, M, fs)
    
    if Q['tracks']:
        tr_ds = xr.open_dataset(Q['tr_fn'], decode_times=False)
        tracks_ot = tr_ds['ot'].values
        tracks_lon = tr_ds.lon.values
        tracks_lat = tr_ds.lat.values
        iot = zfun.find_nearest_ind(tracks_ot, T['ocean_time'])
        if iot > 2:
            ax.plot(tracks_lon[0,:], tracks_lat[0,:],'og', ms=5)
        ax.plot(tracks_lon[:iot+1,:], tracks_lat[:iot+1,:],'-r', alpha=.5, lw=1)
        ax.plot(tracks_lon[iot,:], tracks_lat[iot,:],'o', mec='k', mfc='r')
        tr_ds.close()
        
    # axes labeling
    ax.set_xticks(Q['xtl'])
    ax.set_yticks(Q['ytl'])
    ax.tick_params(labelsize=.7*fs)
    
    # MOORING TIME SERIES
    ax = plt.subplot2grid((7,1), (6,0), rowspan=1)
    dm_pfun.plot_time_series(ax, M, T)
    
    fig.tight_layout()
    
    # FINISH
    ds.close()
    if len(str(Q['fn_out'])) > 0:
        plt.savefig(Q['fn_out'])
        plt.close()
    else:
        plt.show()
    plt.rcdefaults()
    
def Phab(Q, M):
    # This is a modified version of P1 that is designed for the HAB Bulletin.
    # Adds two panels to the right that are close-ups of selected regions
    fig = plt.figure(figsize=(11.5,12))
    fs=18
    plt.rc('font', size=fs)
    
    ds = xr.open_dataset(Q['fn'])
    if Q['dom'] == 'full':
        Q['aa'] = pfun.get_aa(ds)
    aa = Q['aa']
    
    vn = Q['vn']
    if Q['bot']:
        nlev = 0
        tstr = 'Bottom'
    else:
        nlev = -1
        tstr = 'Surface'
        
    px, py = pfun.get_plon_plat(ds['lon_rho'].values, ds['lat_rho'].values)
    if vn == 'speed':
        fld = dm_pfun.get_speed(ds, nlev)
    elif vn == 'ARAG':
        px, py, fld = dm_pfun.get_arag(ds, Q, aa, nlev)
        # we get px, py because ARAG is automatically only calulated over
        # a limited domain (aa)
    else:
        fld = ds[vn][0,nlev,:,:].values*pinfo.fac_dict[vn]
        
    if Q['emask']:
        fld = dm_pfun.mask_edges(ds, fld, Q)
    if Q['avl']:
        # set vmax and vmin if needed
        dm_pfun.get_vlims(ds, fld, Q)
        
    # MAP FIELD
    ax = plt.subplot2grid((7,2), (0,0), rowspan=6)
    cs = ax.pcolormesh(px, py, fld,
        cmap=pinfo.cmap_dict[vn], vmin=Q['vmin'], vmax=Q['vmax'])
    ax.text(.95, .99,'%s %s %s' % (tstr, pinfo.tstr_dict[vn],pinfo.units_dict[vn]),
        transform=ax.transAxes, ha='right', va='top', weight='bold')
    
    if Q['dom'] == 'full':
        dm_pfun.add_bathy_contours(ax, ds, txt=False, depth_levs=[200])
        
    if vn == 'speed':
        dm_pfun.add_velocity_vectors(ax, aa, ds, Q['fn'], v_scl=Q['v_scl'])
        
    pfun.add_coast(ax, color='k')
    ax.axis(aa)
    pfun.dar(ax)
    dm_pfun.add_f_stamp(ax, Q)
    
    # Inset colorbar
    cbaxes = inset_axes(ax, width="40%", height="4%", loc='upper right', borderpad=2) 
    cb = fig.colorbar(cs, cax=cbaxes, orientation='horizontal')
    
    # Mooring location
    ax.plot(M['lon'], M['lat'],'ok', ms=5)
    
    # Wind vector
    T = zrfun.get_basic_info(Q['fn'], only_T=True)
    dm_pfun.add_wind(ax, M, T)
    dm_pfun.add_wind_text(ax, aa, M, fs)
    
    if Q['tracks']:
        tr_ds = xr.open_dataset(Q['tr_fn'], decode_times=False)
        tracks_ot = tr_ds['ot'].values
        tracks_lon = tr_ds.lon.values
        tracks_lat = tr_ds.lat.values
        iot = zfun.find_nearest_ind(tracks_ot, T['ocean_time'])
        if iot > 2:
            ax.plot(tracks_lon[0,:], tracks_lat[0,:],'og', ms=5)
        ax.plot(tracks_lon[:iot+1,:], tracks_lat[:iot+1,:],'-r', alpha=.5, lw=1)
        ax.plot(tracks_lon[iot,:], tracks_lat[iot,:],'o', mec='k', mfc='r')
        tr_ds.close()
        
    # axes labeling
    ax.set_xticks(Q['xtl'])
    ax.set_yticks(Q['ytl'])
    ax.tick_params(labelsize=.7*fs)
    
    # MOORING TIME SERIES
    axm = plt.subplot2grid((7,2), (6,0), rowspan=1)
    dm_pfun.plot_time_series(axm, M, T)
    
    def add_focus_tracks(ax, iot):
        # fancy tracks with narrowing tails
        if iot > 2:
            ax.plot(tracks_lon[0,:], tracks_lat[0,:],'o',mec='gold', mfc='gold', ms=3)
        ax.plot(tracks_lon[:iot+1,:], tracks_lat[:iot+1,:],'-r', alpha=.5, lw=1)
        iiot = 0
        while iiot < iot:
            if (iot - iiot) <= 12:
                iims = 7 - (iot - iiot)/2
                ax.plot(tracks_lon[iiot,:], tracks_lat[iiot,:],'o', mec='r', mfc='r', ms=iims, alpha=.5)
            iiot += 1
        ax.plot(tracks_lon[iot,:], tracks_lat[iot,:],'o', mec='k', mfc='r', ms=8)
    
    # Focus plot 1
    ax1 = plt.subplot2grid((2,2), (0,1))
    aa1 = [-127, -124, 47.2, 49.8]
    dm_pfun.draw_box(ax, aa1, linestyle='-', color='c', alpha=1, linewidth=3)
    dm_pfun.draw_box(ax1, aa1, linestyle='-', color='c', alpha=1, linewidth=5, inset=.01)
    ax1.set_xticks([ -126, -125])
    ax1.set_yticks([48, 49])
    ax1.tick_params(labelsize=.7*fs)
    pfun.add_coast(ax1, linewidth=1.5)
    pfun.add_bathy_contours(ax1, ds, txt=False, depth_levs=[200])
    if Q['tracks']:
        add_focus_tracks(ax1, iot)
    ax1.axis(aa1)
    pfun.dar(ax1)
    
    # Focus plot 2
    ax2 = plt.subplot2grid((2,2), (1,1))
    aa2 = [-126.5, -123.5, 43.2, 45.8]
    dm_pfun.draw_box(ax, aa2, linestyle='-', color='purple', alpha=1, linewidth=3)
    dm_pfun.draw_box(ax2, aa2, linestyle='-', color='purple', alpha=1, linewidth=5, inset=.01)
    ax2.set_xticks([-126, -125, -124])
    ax2.set_yticks([44, 45])
    ax2.tick_params(labelsize=.7*fs)
    pfun.add_coast(ax2, linewidth=1.5)
    dm_pfun.add_bathy_contours(ax2, ds, txt=False, depth_levs=[200])
    if Q['tracks']:
        add_focus_tracks(ax2, iot)
    ax2.axis(aa2)
    pfun.dar(ax2)
    
    plt.tight_layout()
    plt.subplots_adjust(left=.03, bottom=.03, right=.97, top=.97, wspace=0, hspace=None)
    
    # FINISH
    ds.close()
    if len(str(Q['fn_out'])) > 0:
        plt.savefig(Q['fn_out'])
        plt.close()
    else:
        plt.show()
    plt.rcdefaults()
    
def P2(Q, M):
    # modified from P1 to be more square, for the wcvi domain
    fig = plt.figure(figsize=(10,12))
    fs=18
    plt.rc('font', size=fs)
    
    ds = xr.open_dataset(Q['fn'])
    if Q['dom'] == 'full':
        Q['aa'] = pfun.get_aa(ds)
    aa = Q['aa']
    
    vn = Q['vn']
    if Q['bot']:
        nlev = 0
        tstr = 'Bottom'
    else:
        nlev = -1
        tstr = 'Surface'
        
    px, py = pfun.get_plon_plat(ds['lon_rho'].values, ds['lat_rho'].values)
    if vn == 'speed':
        fld = dm_pfun.get_speed(ds, nlev)
    elif vn == 'ARAG':
        px, py, fld = dm_pfun.get_arag(ds, Q, aa, nlev)
        # we get px, py because ARAG is automatically only calulated over
        # a limited domain (aa)
    else:
        fld = ds[vn][0,nlev,:,:].values*pinfo.fac_dict[vn]
        
    if Q['emask']:
        fld = dm_pfun.mask_edges(ds, fld, Q)
    if Q['avl']:
        # set vmax and vmin if needed
        dm_pfun.get_vlims(ds, fld, Q)
        
    # MAP FIELD
    ax = plt.subplot2grid((7,1), (0,0), rowspan=6)
    cs = ax.pcolormesh(px, py, fld,
        cmap=pinfo.cmap_dict[vn], vmin=Q['vmin'], vmax=Q['vmax'])
    ax.text(.95, .99,'%s %s %s' % (tstr, pinfo.tstr_dict[vn],pinfo.units_dict[vn]),
        transform=ax.transAxes, ha='right', va='top', weight='bold')
    
    if Q['dom'] == 'full':
        dm_pfun.add_bathy_contours(ax, ds, depth_levs=[200])
    elif Q['dom'] == 'nshelf':
        dm_pfun.add_bathy_contours(ax, ds, depth_levs=[100, 200], c='c', lw=1)
        
    if vn == 'speed':
        dm_pfun.add_velocity_vectors(ax, aa, ds, Q['fn'], v_scl=Q['v_scl'])
        
    pfun.add_coast(ax, color='k')
    ax.axis(aa)
    pfun.dar(ax)
    dm_pfun.add_f_stamp(ax, Q)
        
    # Inset colorbar
    cbaxes = inset_axes(ax, width="40%", height="4%", loc='upper right', borderpad=2) 
    cb = fig.colorbar(cs, cax=cbaxes, orientation='horizontal')
    
    # Mooring location
    ax.plot(M['lon'], M['lat'],'ok', ms=5)
    
    # Wind vector
    T = zrfun.get_basic_info(Q['fn'], only_T=True)
    dm_pfun.add_wind(ax, M, T)
    dm_pfun.add_wind_text(ax, aa, M, fs)
    
    if Q['tracks']:
        tr_ds = xr.open_dataset(Q['tr_fn'], decode_times=False)
        tracks_ot = tr_ds['ot'].values
        tracks_lon = tr_ds.lon.values
        tracks_lat = tr_ds.lat.values
        iot = zfun.find_nearest_ind(tracks_ot, T['ocean_time'])
        if iot > 2:
            ax.plot(tracks_lon[0,:], tracks_lat[0,:],'og', ms=5)
        ax.plot(tracks_lon[:iot+1,:], tracks_lat[:iot+1,:],'-r', alpha=.5, lw=1)
        ax.plot(tracks_lon[iot,:], tracks_lat[iot,:],'o', mec='k', mfc='r')
        tr_ds.close()
        
    # axes labeling
    ax.set_xticks(Q['xtl'])
    ax.set_yticks(Q['ytl'])
    ax.tick_params(labelsize=.7*fs)
    
    # MOORING TIME SERIES
    ax = plt.subplot2grid((7,1), (6,0), rowspan=1)
    dm_pfun.plot_time_series(ax, M, T)
    
    fig.tight_layout()
    
    # FINISH
    ds.close()
    if len(str(Q['fn_out'])) > 0:
        plt.savefig(Q['fn_out'])
        plt.close()
    else:
        plt.show()
    plt.rcdefaults()
