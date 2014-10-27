#!/usr/bin/python

import os
import sys
import ROOT
import tempfile

testdir = os.path.dirname(os.path.realpath(__file__))
srcdir = os.path.dirname(testdir)
cfgdir = os.path.join(srcdir,'config')


# work around an incredibly stupid ROOT interface
def capture_stdout(callable):
    '''Call a callable and capture any stdout it may produce.  

    Return tuple: (ret, out, err) where: 

     - <ret> :: what is returned by callable
     - <out> :: any stdout printed in the course of calling callable
     - <err> :: any stderr printed in the course of calling callable
    '''

    out_fd,out_fname = tempfile.mkstemp()
    os.close(out_fd)
    err_fd,err_fname = tempfile.mkstemp()
    os.close(err_fd)

    # don't use this, it's too fucky
    #ROOT.gSystem.RedirectOutput(fname) 
    # instead do it in Python following:
    # http://root.cern.ch/phpBB3/viewtopic.php?t=10131    
    old_stdout = os.dup(sys.stdout.fileno())
    new_stdout = open(out_fname, 'w')
    old_stderr = os.dup(sys.stderr.fileno())
    new_stderr = open(err_fname, 'w')

    os.dup2( new_stdout.fileno(), sys.stdout.fileno() )
    os.dup2( new_stderr.fileno(), sys.stderr.fileno() )

    def restore_stdouterr():
        os.dup2( old_stdout, sys.stdout.fileno() )
        os.dup2( old_stderr, sys.stderr.fileno() )

    try:
        ret = callable()
    except:
        restore_stdouterr()
        raise
    else:
        restore_stdouterr()
    
    new_stdout.close()
    new_stderr.close()
    out_text = open(out_fname).read()
    err_text = open(err_fname).read()
    os.remove(out_fname)
    os.remove(err_fname)

    return (ret, out_text, err_text)

def make_gegede_geom(cfgfile):
    base = os.path.splitext(os.path.basename(cfgfile))[0]
    gdmlfile = base + '.gdml'

    import gegede.main
    geom = gegede.main.generate(cfgfile)

    from gegede.export import Exporter
    exporter = Exporter('gdml')
    exporter.convert(geom)
    exporter.output(gdmlfile)

    tgeo,out,err = capture_stdout(lambda : ROOT.TGeoManager.Import(gdmlfile))
    for line in out.split('\n'):
        assert not 'Not Yet Defined' in line, line

    return tgeo

def check_overlaps(tgeo):
    _,out,err = capture_stdout(tgeo.CheckOverlaps)
    if not 'Number of illegal overlaps/extrusions : 0' in err:
        print err
        overlaps = tgeo.GetListOfOverlaps();
        print 'Overlaps:'
        for o in overlaps:
            print '"%s" <--> "%s" %f' % (o.GetFirstVolume().GetName(),
                                         o.GetSecondVolume().GetName(), 
                                         o.GetOverlap())
            o.Print()
            print '-'*60
            print

        raise RuntimeError, 'Overlaps found'
    # weirdest fscking interface
    loo = tgeo.GetListOfOverlaps()
    overlaps = [loo.At(ind) for ind in range(loo.GetSize()) if loo.At(ind)]
    assert len(overlaps)==0, 'Found %d overlaps: %s' % (len(overlaps),str(overlaps))

def test_overlaps_35ton():
    cfgfile = os.path.join(cfgdir,'35ton.cfg')
    tgeo = make_gegede_geom(cfgfile)
    check_overlaps(tgeo)
    print 'Done...'

if '__main__' == __name__:
    test_overlaps_35ton()

