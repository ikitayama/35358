import sys

from neuron import h, gui
#from matplotlib import pyplot
h.load_file('stdrun.hoc')
h.load_file("rinzelnrn.hoc")

def test_direct_memory_transfer():
    #h('''create soma''')
    cell=h.rinzelnrn()
    #h.psection()
    #dir(h)
    #h.soma.L=5.6419
    #h.soma.diam=5.6419
    #h.soma.insert("rinzelnrn")
    gc=2.1
    pp=0.5

    cell.soma.Ra = 1
    cell.dend.Ra = 1
    global_Ra = (1e-6/(gc/pp * (h.area(0.5)*1e-8) * 1e-3))/(2*h.ri(0.5))
    cell.soma.Ra = global_Ra  
    cell.soma.cm = 3 
    cell.dend.Ra = global_Ra
    cell.dend.cm = 3 

     # soma
    cell.soma.insert("pas")
    cell.soma.insert("kdr")
    cell.soma.insert("nafPR")
    
    cell.soma.gmax_nafPR = 30e-3
    cell.soma.gmax_kdr = 15e-3
    cell.soma.g_pas = 0.1e-3
    cell.soma.e_pas = -60
 
    # dend
    cell.dend.insert("pas")
    cell.dend.insert("rcadecay")
    cell.dend.insert("cal")
    cell.dend.insert("kcRT03")
    cell.dend.insert("rkq")
   
    cell.dend.g_pas=0.1e-3
    cell.dend.e_pas=-60
    cell.dend.phi_rcadecay = 130
    cell.dend.gmax_cal = 00010e-3
    cell.dend.erev_cal = 80
    cell.dend.gmax_kcRT03= 00015e-3
    cell.dend.gmax_rkq=0000.8e-3
    cell.dend.ek=-75
     
    ic = h.IClamp(cell.soma(.5))
    ic.delay = .5
    ic.dur = 0.1
    ic.amp = 0.3

    #for testing external mod file
    #h.soma.insert("hh")

    h.cvode.use_fast_imem(1)
    h.cvode.cache_efficient(1)

    h.tstop = 50
    h.celsius = 37.0
    h.v_init = -60
    v = h.Vector()
    v.record(cell.soma(.5)._ref_v, sec = cell.soma)
    i_mem = h.Vector()
    i_mem.record(cell.soma(.5)._ref_i_membrane_, sec = cell.soma)
    tv = h.Vector()
    tv.record(h._ref_t, sec=cell.soma)
    h.run()
    vstd = v.cl()
    tvstd = tv.cl()
    i_memstd = i_mem.cl()
    # Save current (after run) value to compare with transfer back from coreneuron
    #tran_std = [h.t, cell.soma(.5).v, cell.soma(.5).hh.m]

    from neuron import coreneuron
    coreneuron.enable = True

    pc = h.ParallelContext()
    h.stdinit()
    pc.psolve(h.tstop)
    #tran = [h.t, cell.soma(.5).v, cell.soma(.5).hh.m]

    assert(tv.eq(tvstd))
    #assert(v.cl().sub(vstd).abs().max() < 1e-10)
    assert(i_mem.cl().sub(i_memstd).abs().max() < 1e-10)
    #assert(h.Vector(tran_std).sub(h.Vector(tran)).abs().max() < 1e-10)

    f = open('v.dat', 'w')
    for i in range(tv.size()):
       print('{} {}'.format(tv[i], v[i]), file=open("v.dat","a"))

if __name__ == "__main__":
    test_direct_memory_transfer()
