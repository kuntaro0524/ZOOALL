from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import wx
import wx.lib.newevent
import time
import threading

EventAppendShika, EVT_APPEND_SHIKA = wx.lib.newevent.NewEvent()

class kuma_xmlrpc_server(SimpleXMLRPCServer):
    def __init__ (self, addr, my_interface):
        self.my_interface = my_interface
        SimpleXMLRPCServer.__init__(self, addr, logRequests=0, allow_none=True)
    # __init__()

    def _dispatch (self, method, params):
        if not self.my_interface.enable_xmlrpc:
            return 

        func = None

        print "method=", method
        print "params=", params

        if hasattr(self.my_interface, method):
            func = getattr(self.my_interface, method)

        if not hasattr(func, "__call__") :
            print "%s is not a callable object!" % method
        else:
            return func(*params)

    # _dispatch()
# class kuma_xmlrpc_server

class kuma_shika_interface:
    def __init__ (self, parent, port=1920):
        self.parent = parent
        self.enable_xmlrpc = True
        self.xmlrpc_server = None
        self.thread = None

        # start XML-RPC server
        try:
            self.xmlrpc_server = kuma_xmlrpc_server(("", port), self)
            self.xmlrpc_server.socket.settimeout(0.01)
        except Exception, e:
            print "Error starting XML-RPC server:"
            print str(e)
        else:
            self.thread = threading.Thread(None, self.run)
            self.thread.daemon = True
            self.thread.start()
            print "xml-rpc server running on port %d" % port

    # __init__()

    def run(self, *args) :
        while self.xmlrpc_server is not None:
            self.xmlrpc_server.handle_request()
            time.sleep(.2)
    # run()
    
    def stop(self):
        self.xmlrpc_server = None
        if self.thread is not None and self.thread.is_alive():
            self.thread.join()
    # stop()

    def append_coords(self, gonio_xyz_phi, comment):
        print "Catch!", gonio_xyz_phi, comment
        wx.PostEvent(self.parent, EventAppendShika(gonio_phi=gonio_xyz_phi[3],
                                                   gonio_xyz=gonio_xyz_phi[:3],
                                                   comment=comment))
    # run_scmfile()

# class kuma_shika_interface
