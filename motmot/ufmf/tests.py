import pkg_resources
import unittest
import motmot.ufmf.ufmf as ufmf
import numpy
import tempfile, os

class TestUfmf(unittest.TestCase):

    def test_a(self):
        w = 640
        h = 480

        frame1 = numpy.zeros( (h,w), dtype = numpy.uint8 )
        frame1[20:30,30:32] = 255
        frame1[20:30,30:32] = 255

        timestamp1 = 1e-20

        filename = tempfile.mkstemp()[1]
        try:
            us = ufmf.UfmfSaver( filename,
                                 frame1,
                                 timestamp1,
                                 image_radius=5 )


            frame2 = numpy.zeros( (h,w), dtype = numpy.uint8 )


            frame2[20:30,30:40] = 1
            frame2[21,31] = 8
            frame2[60:70, 80:90] = 100
            frame2[61,81] = 7
            timestamp2 = 1

            pts = [ (35,25), # x,y
                    (85,65),
                    ]

            us.add_frame( frame2, timestamp2, pts )

            us.close()

            us2 = ufmf.Ufmf(filename)
            test_frame1, test_timestamp1 = us2.get_bg_image()
            assert numpy.allclose( test_frame1, frame1 )
            assert test_timestamp1 == timestamp1
            us2.close()
        finally:
            os.unlink(filename)

    def test_b_seek(self):
        self._do_test_b( True )

    def test_b_no_seek(self):
        self._do_test_b( False )

    def _do_test_b(self,seek_ok):
        w = 752
        h = 240

        frame1 = numpy.zeros( (h,w), dtype = numpy.uint8 )
        frame1[20:30,30:32] = 255
        frame1[20:30,30:32] = 255

        timestamp = 1
        radius = 15

        filename = tempfile.mkstemp()[1]
        try:
            us = ufmf.UfmfSaver( filename,
                                 frame1,
                                 timestamp,
                                 image_radius=radius )

            frame2 = numpy.zeros( (h,w), dtype = numpy.uint8 )
            frame2[:,0::2] = range(0, w, 2) # clips (broadcast)
            for i in range(h):
                frame2[i,1::2] = i

            ll_pts = [
                [ (345, 144),
                  (521, 118),
                  ],
                [ (347, 144),
                  (522, 119),
                  (367, 229),
                  ],
                [(349,145),
                 (522,120),
                 (369,229),
                 ],
                ]
            all_pts = [ [(x+radius,y+radius) for (x,y) in pts ] for pts in ll_pts ]
            for pts in all_pts:
                timestamp += 1
                us.add_frame( frame2, timestamp, pts )
            us.close()

            us2 = ufmf.Ufmf(filename,seek_ok=seek_ok)
            test_frame1, test_timestamp1 = us2.get_bg_image()
            assert numpy.allclose( test_frame1, frame1 )
            assert test_timestamp1 == 1

            test_timestamp = 2
            for i, (timestamp, regions) in enumerate(us2.readframes()):
                progress = us2.get_progress()
                test_ll_pts = ll_pts[i]
                assert timestamp == test_timestamp
                test_timestamp += 1
                for test_ll,region in zip(test_ll_pts,regions):
                    xmin,ymin, bufim = region
                    assert xmin==test_ll[0]
                    assert ymin==test_ll[1]

                    # x
                    tj0 = test_ll[0]
                    tj1 = test_ll[0]+2*radius
                    # y
                    ti0 = test_ll[1]
                    ti1 = test_ll[1]+2*radius

                    testbuf = frame2[ti0:ti1,tj0:tj1]
                    assert testbuf.shape == bufim.shape
                    assert numpy.allclose( testbuf, bufim )
            us2.close()
        finally:
            os.unlink(filename)

def get_test_suite():
    ts=unittest.TestSuite([unittest.makeSuite(TestUfmf),
                           ])
    return ts

if __name__=='__main__':
    get_test_suite().debug()
