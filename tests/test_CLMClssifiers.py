import unittest

import os

from metesatpy.production.FY4A import FY4NavFile, FY4AAGRIL1FDIDISK4KM, FY4AAGRIL1GEODISK4KM
from metesatpy.algorithms.CloudMask import Ref063Min3x3Day, TStd, RefRatioDay, Ref138Day, NdsiDay, Ref063Day, Bt1185, \
    T11, Btd37511Night, RefStd, TmaxT

from metesatpy.utils.cspp import infer_airmass, infer_scat_angle_short

import numpy as np
import matplotlib.pyplot as plt

data_root_dir = os.getenv('METEPY_DATA_PATH', 'data')


class TestCLMClassifiers(unittest.TestCase):

    def setUp(self) -> None:
        agri_l1_file_name = 'FY4A-_AGRI--_N_DISK_1047E_L1-_FDI-_MULT_' \
                            'NOM_20200101040000_20200101041459_4000M_V0001.HDF'
        agri_l1_file_path = os.path.join(data_root_dir, '20200101', agri_l1_file_name)

        agri_geo_file_name = 'FY4A-_AGRI--_N_DISK_1047E_L1-_GEO-_MULT_' \
                             'NOM_20200101040000_20200101041459_4000M_V0001.HDF'
        agri_geo_file_path = os.path.join(data_root_dir, '20200101', agri_geo_file_name)

        fy4_nav_file_name = 'fygatNAV.FengYun-4A.xxxxxxx.4km_M1.h5'
        fy4_nav_file_path = os.path.join("F:/", fy4_nav_file_name)

        self.fy4_l1 = FY4AAGRIL1FDIDISK4KM(agri_l1_file_path)
        self.fy4_geo = FY4AAGRIL1GEODISK4KM(agri_geo_file_path)
        self.fy4_nav = FY4NavFile(fy4_nav_file_path)

    def test_Ref063Min3x3Day(self):
        lut_file_name = 'Ref_063_Min_3x3_Day.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # obs mask !!!scale 100!!!
        ref_065 = self.fy4_l1.get_band_by_channel('ref_065') * 100
        # day mask (covnert to bool)
        sun_zen = self.fy4_geo.get_sun_zenith()
        # dem mask
        dem = self.fy4_nav.get_dem()
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        # coastal mask
        coastal = self.fy4_nav.get_coastal()
        coastal_mask = coastal > 0
        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)

        ref_063_min_day = Ref063Min3x3Day(lut_file_path=lut_file_path)
        x = ref_063_min_day.prepare_feature(ref_065)
        valid_mask = ref_063_min_day.prepare_valid_mask(ref_065, dem, sft, sun_zen, coastal_mask, space_mask)
        ratio, prob = ref_063_min_day.infer(x, sft, valid_mask, space_mask, prob=True)
        import tifffile as tiff
        tiff.imwrite('t_raw.tif', prob)
        fig, ax = plt.subplots(1, 2, figsize=(10, 10))
        pos = ax[0].imshow(ratio, 'plasma')
        ax[0].set_title(ref_063_min_day.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[0])
        ax[0].axis('off')
        pos = ax[1].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[1].set_title(ref_063_min_day.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[1])
        ax[1].axis('off')
        plt.show()

    def test_Ref063Min3x3Day_5days(self):
        lut_file_name = 'Ref_063_Min_3x3_Day_267.NC'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # obs mask !!!scale 100!!!
        ref_065 = self.fy4_l1.get_band_by_channel('ref_065') * 100
        # day mask (covnert to bool)
        sun_zen = self.fy4_geo.get_sun_zenith()
        # dem mask
        dem = self.fy4_nav.get_dem()
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        # coastal mask
        coastal = self.fy4_nav.get_coastal()
        coastal_mask = coastal > 0
        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)

        ref_063_min_day = Ref063Min3x3Day(lut_file_path=lut_file_path)
        x = ref_063_min_day.prepare_feature(ref_065)
        valid_mask = ref_063_min_day.prepare_valid_mask(ref_065, dem, sft, sun_zen, coastal_mask, space_mask)
        ratio, prob = ref_063_min_day.infer(x, sft, valid_mask, space_mask, prob=True)
        import tifffile as tiff
        tiff.imwrite('t_267.tif', prob)
        fig, ax = plt.subplots(1, 2, figsize=(10, 10))
        pos = ax[0].imshow(ratio, 'plasma')
        ax[0].set_title(ref_063_min_day.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[0])
        ax[0].axis('off')
        pos = ax[1].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[1].set_title(ref_063_min_day.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[1])
        ax[1].axis('off')
        plt.show()

    def test_TStd(self):
        lut_file_name = 'T_Std.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # obs mask
        bt_1080 = self.fy4_l1.get_band_by_channel('bt_1080')
        # dem mask
        dem = self.fy4_nav.get_dem()
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        # coastal mask
        coastal = self.fy4_nav.get_coastal()
        coastal_mask = coastal > 0
        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)

        tstd = TStd(lut_file_path=lut_file_path)
        x = tstd.prepare_feature(bt_1080)
        valid_mask = tstd.prepare_valid_mask(bt_1080, dem, sft, coastal_mask, space_mask)
        ratio, prob = tstd.infer(x, sft, valid_mask, space_mask, prob=True)
        fig, ax = plt.subplots(1, 2, figsize=(10, 10))
        pos = ax[0].imshow(ratio, 'plasma')
        ax[0].set_title(tstd.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[0])
        ax[0].axis('off')
        pos = ax[1].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[1].set_title(tstd.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[1])
        ax[1].axis('off')
        plt.show()

    def test_Bt1185(self):
        lut_file_name = 'Btd_11_85.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # obs mask
        bt_1080 = self.fy4_l1.get_band_by_channel('bt_1080')
        bt_850 = self.fy4_l1.get_band_by_channel('bt_850')
        # dem mask
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)

        bt1185 = Bt1185(lut_file_path=lut_file_path)
        x = bt1185.prepare_feature(bt_1080, bt_850)
        valid_mask = bt1185.prepare_valid_mask(bt_1080, bt_850, space_mask)
        ratio, prob = bt1185.infer(x, sft, valid_mask, space_mask, prob=True)
        fig, ax = plt.subplots(1, 3, figsize=(10, 10))
        ax[0].imshow(valid_mask, 'plasma')
        ax[0].set_title(bt1185.short_name + ' valid mask \n')
        pos = ax[1].imshow(ratio, 'plasma')
        ax[1].set_title(bt1185.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[1])
        pos = ax[2].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[2].set_title(bt1185.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[2])
        plt.show()

    def test_RefRatioDay(self):
        lut_file_name = 'Ref_Ratio_Day.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        ref_065 = self.fy4_l1.get_band_by_channel('ref_065') * 100
        ref_083 = self.fy4_l1.get_band_by_channel('ref_083') * 100
        bt_1080 = self.fy4_l1.get_band_by_channel('bt_1080')
        sun_zen = self.fy4_geo.get_sun_zenith()
        dem = self.fy4_nav.get_dem()
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        sun_glint = self.fy4_geo.get_sun_glint()

        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)
        ref_ratio_day = RefRatioDay(lut_file_path=lut_file_path)
        x = ref_ratio_day.prepare_feature(ref_065, ref_083)
        valid_mask = ref_ratio_day.prepare_valid_mask(ref_065, ref_083, dem, sft, sun_zen, sun_glint, space_mask,
                                                      bt_1080)
        ratio, prob = ref_ratio_day.infer(x, sft, valid_mask, space_mask, prob=True)
        fig, ax = plt.subplots(1, 3, figsize=(10, 10))
        ax[0].imshow(valid_mask, 'plasma')
        ax[0].set_title(ref_ratio_day.short_name + ' valid mask \n')
        pos = ax[1].imshow(ratio, 'plasma')
        ax[1].set_title(ref_ratio_day.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[1])
        pos = ax[2].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[2].set_title(ref_ratio_day.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[2])
        plt.show()

    def test_Ref138Day(self):
        lut_file_name = 'Ref_138_Day.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # obs mask
        ref_137 = self.fy4_l1.get_band_by_channel('ref_137') * 100
        # day mask (covnert to bool)
        sun_zen = self.fy4_geo.get_sun_zenith()
        sat_zen = self.fy4_geo.get_satellite_zenith()
        pix_lat = self.fy4_nav.get_latitude()
        pix_lon = self.fy4_nav.get_longitude()
        sat_lat = 0
        sat_lon = 104.7
        # scatter angle
        scat_ang = infer_scat_angle_short(pix_lat, pix_lon, sat_lat, sat_lon, sun_zen, sat_zen)
        # air mass
        air_mass = infer_airmass(sat_zen, sun_zen)
        # dem mask
        dem = self.fy4_nav.get_dem()
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        # coastal mask
        coastal = self.fy4_nav.get_coastal()
        coastal_mask = coastal > 0
        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)

        ref138day = Ref138Day(lut_file_path=lut_file_path)
        x = ref138day.prepare_feature(ref_137)
        valid_mask = ref138day.prepare_valid_mask(ref_137, dem, sft, sun_zen, scat_ang, air_mass, space_mask)
        ratio, prob = ref138day.infer(x, sft, valid_mask, space_mask, prob=True)
        fig, ax = plt.subplots(1, 3, figsize=(10, 10))
        ax[0].imshow(valid_mask, 'plasma')
        ax[0].set_title(ref138day.short_name + ' valid mask \n')
        pos = ax[1].imshow(ratio, 'plasma')
        ax[1].set_title(ref138day.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[1])
        pos = ax[2].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[2].set_title(ref138day.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[2])
        plt.show()

    def test_NdsiDay(self):
        lut_file_name = 'Ndsi_Day.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # obs mask
        ref_065 = self.fy4_l1.get_band_by_channel('ref_065') * 100
        ref_161 = self.fy4_l1.get_band_by_channel('ref_161') * 100
        bt_1080 = self.fy4_l1.get_band_by_channel('bt_1080')
        # day mask (covnert to bool)
        sun_zen = self.fy4_geo.get_sun_zenith()
        sat_zen = self.fy4_geo.get_satellite_zenith()
        pix_lat = self.fy4_nav.get_latitude()
        pix_lon = self.fy4_nav.get_longitude()
        sun_glint = self.fy4_geo.get_sun_glint()
        sat_lat = 0
        sat_lon = 104.7
        # scatter angle
        scat_ang = infer_scat_angle_short(pix_lat, pix_lon, sat_lat, sat_lon, sun_zen, sat_zen)
        # air mass
        air_mass = infer_airmass(sat_zen, sun_zen)
        # sft
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)
        ndsi = NdsiDay(lut_file_path=lut_file_path)
        x = ndsi.prepare_feature(ref_065, ref_161)
        valid_mask = ndsi.prepare_valid_mask(ref_065, ref_161, sun_glint, sun_zen, scat_ang, air_mass, space_mask,
                                             bt_1080)
        ratio, prob = ndsi.infer(x, sft, valid_mask, space_mask, prob=True)
        fig, ax = plt.subplots(1, 3, figsize=(10, 10))
        ax[0].imshow(valid_mask, 'plasma')
        ax[0].set_title(ndsi.short_name + ' valid mask \n')
        pos = ax[1].imshow(ratio, 'plasma')
        ax[1].set_title(ndsi.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[1])
        pos = ax[2].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[2].set_title(ndsi.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[2])
        plt.show()

    def test_Ref063Day(self):
        lut_file_name = 'Ref_063_Day.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # 063 ref
        import h5py
        from pyresample import image, geometry
        rc_file = os.path.join(data_root_dir, 'LUT', "ref_065_clear_001.h5")
        rc_f = h5py.File(rc_file, 'r')
        ds = rc_f['ref_065_clear']
        ref_065_clear_gll = np.ma.masked_values(ds[...], ds.attrs['fill_value'])
        ref_065_clear_gll = ref_065_clear_gll * ds.attrs['scale_factor']
        ref_lon = rc_f['lon'][...]
        ref_lat = rc_f['lat'][...]
        obj_lat = self.fy4_nav.get_latitude()
        obj_lon = self.fy4_nav.get_longitude()
        obj_swath_def = geometry.SwathDefinition(
            lons=obj_lon,
            lats=obj_lat)
        ref_lon, ref_lat = np.meshgrid(ref_lon, ref_lat)
        ref_swath_def = geometry.SwathDefinition(
            lons=ref_lon,
            lats=ref_lat)
        ref_swath_con = image.ImageContainerNearest(
            ref_065_clear_gll,
            ref_swath_def,
            radius_of_influence=20000,
            fill_value=65535)
        area_con = ref_swath_con.resample(obj_swath_def)
        ref_065_clear_c = area_con.image_data * 100
        # obs mask
        ref_065 = self.fy4_l1.get_band_by_channel('ref_065') * 100
        bt_1080 = self.fy4_l1.get_band_by_channel('bt_1080')
        # day mask (covnert to bool)
        sun_zen = self.fy4_geo.get_sun_zenith()
        sat_zen = self.fy4_geo.get_satellite_zenith()
        pix_lat = self.fy4_nav.get_latitude()
        pix_lon = self.fy4_nav.get_longitude()
        sun_glint = self.fy4_geo.get_sun_glint()
        sat_lat = 0
        sat_lon = 104.7
        # scatter angle
        scat_ang = infer_scat_angle_short(pix_lat, pix_lon, sat_lat, sat_lon, sun_zen, sat_zen)
        # air mass
        air_mass = infer_airmass(sat_zen, sun_zen)
        # dem
        dem = self.fy4_nav.get_dem()
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        # snow mask
        snow_mask = self.fy4_nav.get_snow_mask()
        snow_mask = snow_mask == 3
        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)

        ref063day = Ref063Day(lut_file_path=lut_file_path)
        x = ref063day.prepare_feature(ref_065, ref_065_clear_c)
        valid_mask = ref063day.prepare_valid_mask(ref_065, ref_065_clear_c, dem, sft, sun_glint, sun_zen, scat_ang,
                                                  air_mass, snow_mask, space_mask, bt_1080)
        ratio, prob = ref063day.infer(x, sft, valid_mask, space_mask, prob=True)
        fig, ax = plt.subplots(1, 3, figsize=(10, 10))
        ax[0].imshow(valid_mask, 'plasma')
        ax[0].set_title(ref063day.short_name + ' valid mask \n')
        pos = ax[1].imshow(ratio, 'plasma')
        ax[1].set_title(ref063day.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[1])
        pos = ax[2].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[2].set_title(ref063day.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[2])
        plt.show()

    def test_ref_proj(self):
        import h5py
        from pyresample import image, geometry
        rc_file = r"D:\WorkSpace\20200429\project\data\LUT\ref_065_clear_001.h5"
        rc_f = h5py.File(rc_file, 'r')
        ds = rc_f['ref_065_clear']
        ref_065_clear_gll = np.ma.masked_values(ds[...], ds.attrs['fill_value'])
        ref_065_clear_gll = ref_065_clear_gll * ds.attrs['scale_factor']
        ref_lon = rc_f['lon'][...]
        ref_lat = rc_f['lat'][...]
        obj_lat = self.fy4_nav.get_latitude()
        obj_lon = self.fy4_nav.get_longitude()
        obj_swath_def = geometry.SwathDefinition(
            lons=obj_lon,
            lats=obj_lat)
        ref_lon, ref_lat = np.meshgrid(ref_lon, ref_lat)
        ref_swath_def = geometry.SwathDefinition(
            lons=ref_lon,
            lats=ref_lat)
        ref_swath_con = image.ImageContainerNearest(
            ref_065_clear_gll,
            ref_swath_def,
            radius_of_influence=20000,
            fill_value=65535)
        area_con = ref_swath_con.resample(obj_swath_def)
        ref_065_clear_c = area_con.image_data
        plt.imshow(ref_065_clear_c)
        plt.show()

    def test_T11(self):
        lut_file_name = 'T_11_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # obs mask
        bt_1080 = self.fy4_l1.get_band_by_channel('bt_1080')
        # dem mask
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        import tifffile as tiff
        tiff.imwrite('sft.tif', sft)
        # # space mask
        # space_mask = self.fy4_nav.get_space_mask(b=True)
        #
        # t11 = T11(lut_file_path=lut_file_path)
        # x = t11.prepare_feature(bt_1080)
        # valid_mask = t11.prepare_valid_mask(bt_1080, sft, space_mask)
        # ratio, prob = t11.infer(x, sft, valid_mask, space_mask, prob=True)
        #
        # fig, ax = plt.subplots(1, 3, figsize=(10, 10))
        # ax[0].imshow(valid_mask, 'plasma')
        # ax[0].set_title(t11.short_name + ' valid mask \n')
        # pos = ax[1].imshow(ratio, 'plasma')
        # ax[1].set_title(t11.short_name + ' Ratio \n')
        # fig.colorbar(pos, ax=ax[1])
        # pos = ax[2].imshow(prob, 'plasma', vmin=0, vmax=1)
        # ax[2].set_title(t11.short_name + ' Prob \n')
        # fig.colorbar(pos, ax=ax[2])
        # plt.show()

    # TODO: add btd37511
    def test_Btd37511Night(self):
        lut_file_name = 'T_11_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # obs mask
        bt_1080 = self.fy4_l1.get_band_by_channel('bt_1080')
        # dem mask
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)
        t11 = T11(lut_file_path=lut_file_path)
        x = t11.prepare_feature(bt_1080)
        valid_mask = t11.prepare_valid_mask(bt_1080, sft, space_mask)
        ratio, prob = t11.infer(x, sft, valid_mask, space_mask, prob=True)
        fig, ax = plt.subplots(1, 3, figsize=(10, 10))
        ax[0].imshow(valid_mask, 'plasma')
        ax[0].set_title(t11.short_name + ' valid mask \n')
        pos = ax[1].imshow(ratio, 'plasma')
        ax[1].set_title(t11.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[1])
        pos = ax[2].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[2].set_title(t11.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[2])
        plt.show()

    # TODO: add refstd
    def test_RefStd(self):
        lut_file_name = 'T_11_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        # obs mask
        bt_1080 = self.fy4_l1.get_band_by_channel('bt_1080')
        # dem mask
        sft = self.fy4_nav.prepare_surface_type_to_cspp()
        # space mask
        space_mask = self.fy4_nav.get_space_mask(b=True)
        t11 = T11(lut_file_path=lut_file_path)
        x = t11.prepare_feature(bt_1080)
        valid_mask = t11.prepare_valid_mask(bt_1080, sft, space_mask)
        ratio, prob = t11.infer(x, sft, valid_mask, space_mask, prob=True)
        fig, ax = plt.subplots(1, 3, figsize=(10, 10))
        ax[0].imshow(valid_mask, 'plasma')
        ax[0].set_title(t11.short_name + ' valid mask \n')
        pos = ax[1].imshow(ratio, 'plasma')
        ax[1].set_title(t11.short_name + ' Ratio \n')
        fig.colorbar(pos, ax=ax[1])
        pos = ax[2].imshow(prob, 'plasma', vmin=0, vmax=1)
        ax[2].set_title(t11.short_name + ' Prob \n')
        fig.colorbar(pos, ax=ax[2])
        plt.show()

    def test_Ref063Min3x3Day_plot(self):
        lut_file_name = 'Ref_063_Min_3x3_Day_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        ref063min = Ref063Min3x3Day(lut_file_path=lut_file_path)
        fig = ref063min.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_TStd_plot(self):
        lut_file_name = 'T_Std_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        tstd = TStd(lut_file_path=lut_file_path)
        fig = tstd.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_Bt1185_plot(self):
        lut_file_name = 'Btd_11_85_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        bt1185 = Bt1185(lut_file_path=lut_file_path)
        fig = bt1185.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_RefRatio_plot(self):
        lut_file_name = 'Ref_Ratio_Day_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        ref_ratio = RefRatioDay(lut_file_path=lut_file_path)
        fig = ref_ratio.plot()
        plt.show()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_Ref138_plot(self):
        lut_file_name = 'Ref_138_Day_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        ref_138 = Ref138Day(lut_file_path=lut_file_path)
        fig = ref_138.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_Ndsi_plot(self):
        lut_file_name = 'Ndsi_Day.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        ndsi = NdsiDay(lut_file_path=lut_file_path)
        fig = ndsi.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_Ref063_plot(self):
        lut_file_name = 'Ref_063_Day.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        ref063 = Ref063Day(lut_file_path=lut_file_path)
        fig = ref063.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_T11_plot(self):
        lut_file_name = 'T_11_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        t11 = T11(lut_file_path=lut_file_path)
        fig = t11.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_TmaxT_plot(self):
        lut_file_name = 'Tmax_T_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        tmax_t = TmaxT(lut_file_path=lut_file_path)
        fig = tmax_t.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_Btd37511_plot(self):
        lut_file_name = 'Btd_375_11_Night_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        btd37511 = Btd37511Night(lut_file_path=lut_file_path)
        fig = btd37511.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)

    def test_RefStd_plot(self):
        lut_file_name = 'Ref_Std_60.nc'
        lut_file_path = os.path.join(data_root_dir, 'LUT', lut_file_name)
        ref_std = RefStd(lut_file_path=lut_file_path)
        fig = ref_std.plot()
        fig.savefig(lut_file_name.replace('nc', 'png'), dpi=300)


if __name__ == '__main__':
    unittest.main()
