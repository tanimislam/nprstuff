base_data( )
    print 'message = %s' % statusdict['message']
    qApp = QApplication( sys.argv )
    lw = LoginWindow( statusdict )
    sys.exit( qApp.exec_() )
