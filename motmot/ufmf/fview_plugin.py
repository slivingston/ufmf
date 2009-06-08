from __future__ import with_statement, division
import pkg_resources

import motmot.fview.traited_plugin as traited_plugin
import motmot.ufmf.ufmf as ufmf

import enthought.traits.api as traits
from enthought.traits.ui.api import View, Item, Group
import motmot.realtime_image_analysis.trealtime_image_analysis as tra
import motmot.FastImage.FastImage as FastImage
import threading

class UfmfSaver(traits.HasTraits):
    def put_image(self,which_image,data):
        print 'UfmfSaver should save image %s'%which_image

class UFMFFviewSaver(traited_plugin.HasTraits_FViewPlugin):
    plugin_name = 'ufmf saver'
    enabled = traits.Bool(True)

    saving = traits.Bool(False)
    start_saving = traits.Button()
    stop_saving = traits.Button()

    ufmf_saver = traits.Any(transient=True)

    difference_threshold = traits.Float(5.0)

    clear_and_take_BG = traits.Button()
    _clear_take_event = traits.Any(transient=True)
    bg_Nth_frame = traits.Int(100)
    use_roi2 = traits.Bool(True)


    realtime_analyzer = traits.Instance( tra.TraitedRealtimeAnalyzer )

    traits_view = View(Group(Item(name='enabled'),
                             Item(name='start_saving',show_label=False),
                             Item(name='stop_saving',show_label=False),
                             Item(name='bg_Nth_frame'),
                             Item(name='difference_threshold'),
                             Item(name='use_roi2'),
                             Item(name='clear_and_take_BG',show_label=False),
                             Item(name='realtime_analyzer',
                                  style='custom'),
                             )
                       )
    def __init__(self,*args,**kwargs):
        super(UFMFFviewSaver,self).__init__(*args,**kwargs)
        self._clear_take_event = threading.Event()
        self.ufmf_saver = UfmfSaver()

    def _clear_and_take_BG_fired(self):
        self._clear_take_event.set()

    def _start_saving_fired(self):
        print 'saving started'
        self.saving = True
        #self.ufmf_saver.start_saving()

    def _stop_saving_fired(self):
        print 'saving stopped'
        self.saving = False
        #self.ufmf_saver.stop_saving()

    def camera_starting_notification(self,cam_id,
                                     pixel_format=None,
                                     max_width=None,
                                     max_height=None):
        self.realtime_analyzer = tra.TraitedRealtimeAnalyzer(
            max_width=max_width,
            max_height=max_height)

        self.max_frame_size = FastImage.Size( max_width, max_height )
        self.full_frame_live = FastImage.FastImage8u( self.max_frame_size )
        self.running_mean_im = FastImage.FastImage32f( self.max_frame_size)

    def process_frame(self,cam_id,buf,buf_offset,timestamp,framenumber):
        draw_points = []
        draw_linesegs = []

        if self.enabled:
            realtime_analyzer = self.realtime_analyzer
            fibuf = FastImage.asfastimage(buf)
            l,b = buf_offset
            lbrt = l, b, l+fibuf.size.w-1, b+fibuf.size.h-1

            if self._clear_take_event.isSet():
                running_mean8u_im = realtime_analyzer.get_image_view('mean')
                if running_mean8u_im.size == fibuf.size:
                    srcfi = fibuf
                    bg_copy = srcfi.get_8u_copy(self.max_frame_size)
                else:
                    srcfi = FastImage.FastImage8u(self.max_frame_size)
                    srcfi_roi = srcfi.roi(l,b,fibuf.size)
                    fibuf.get_8u_copy_put(srcfi_roi, fibuf.size)
                    bg_copy = srcfi # newly created, no need to copy

                srcfi.get_32f_copy_put( self.running_mean_im,   self.max_frame_size )
                srcfi.get_8u_copy_put(  running_mean8u_im, self.max_frame_size )

                self.ufmf_saver.put_image('bg',bg_copy)
                self._clear_take_event.clear()
                del srcfi, bg_copy # don't pollute namespace

            realtime_analyzer.do_work( fibuf, timestamp, framenumber,
                                       self.use_roi2)
        return draw_points, draw_linesegs