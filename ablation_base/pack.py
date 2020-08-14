
def pack(pore_vol,tt):

    ##############################################################
    # Read from packing data
    # import data1 and create arrays

    import numpy as np
    import pickle as pk


    data1 = np.loadtxt('ellipse_positions' + '.txt',skiprows=2)
    #print (data1)
    ctr = np.zeros(shape=(len(data1),3))
    pt1 = np.zeros(shape=(len(data1),3))
    pt2 = np.zeros(shape=(len(data1),3))
    ang = np.zeros(shape=(len(data1),1))

    for i in range(len(data1)):
        ctr[i]=data1[i][0:3]
        pt1[i]=data1[i][3:6]
        pt2[i]=data1[i][6:9]
        ang[i]=data1[i][9]




    data2 = np.loadtxt('packing_info' + '.txt',skiprows=0)
    #print (data2)
    N_fiber = int(data2[0])
    N_pore = int(data2[2])
    N=N_fiber+N_pore
    print ('N fiber = ', N_fiber)
    print ('N pore = ', N_pore)



    ################################################3
    # Calculate the aspect ratios of any one pore

    k=N_fiber+1
    a=((ctr[k][0]-pt1[k][0])**2+(ctr[k][1]-pt1[k][1])**2)**0.5
    b=((ctr[k][0]-pt2[k][0])**2+(ctr[k][1]-pt2[k][1])**2)**0.5

    R=a/b

    print 'The aspect ratio is =',R
    ######################################
    # calculate the present volume fraction
    pr_vol_frac_pore=N_pore*(np.pi*a*b)

    print ('pore vol frac', pr_vol_frac_pore)

    ####################################3

    # desired vol fraction is pore_vol

    print ('New volume of the pores is',pore_vol)

    a_new_mod=(pore_vol*R/(N_pore*np.pi))**0.5    # change here for switching test 1.0
    b_new_mod=a_new_mod/R

    print ('a is' ,a_new_mod )
    print ('b is' ,b_new_mod )

    f=open('asp_ch','a')
    f.write(str(tt)+' '+str(a_new_mod)+"\n")
    f.close()

    f=open('axis%d'%tt,'wb')
    pk.dump(a_new_mod,f,protocol=2)
    f.close()

    ######################################
    # calculate the angles of each ellipse
    ang_calc=[]

    for i in range(N_fiber,N):
        ang_calc.append(np.arctan((pt1[k][2]-ctr[k][2])/pt1[k][1]-ctr[k][1]))


    ## Create new pore positions
    fin_a_x=[]
    fin_a_y=[]
    fin_b_x=[]
    fin_b_y=[]


    for k in range(N_fiber,N):
        fin_a_x.append(a_new_mod*np.cos(ang[k])+ctr[k][0])
        fin_a_y.append(a_new_mod*np.sin(ang[k])+ctr[k][1])
        fin_b_x.append(-b_new_mod*np.sin(ang[k])+ctr[k][0])
        fin_b_y.append(b_new_mod*np.cos(ang[k])+ctr[k][1])


    #print(fin_a_y)
    #print(fin_b_y)

    yay=np.zeros((N_pore,4))

    for i in range(N_pore):
        yay[i][0]=fin_a_x[i]

    for i in range(N_pore):
        yay[i][1]=fin_a_y[i]

    for i in range(N_pore):
        yay[i][2]=fin_b_x[i]

    for i in range(N_pore):
        yay[i][3]=fin_b_y[i]


    np.savetxt('yy%d'%tt,yay)   #where is it used? everywhere.




    # dump everything in binaries


#     f=open('ax%d' %tt,'wb')
#     pk.dump(fin_a_x,f,protocol=2)
#     f.close()

#     f=open('ay%d' %tt,'wb')
#     pk.dump(fin_a_y,f,protocol=2)
#     f.close()

#     f=open('bx%d' %tt,'wb')
#     pk.dump(fin_b_x,f,protocol=2)
#     f.close()

#     f=open('by%d' %tt,'wb')
#     pk.dump(fin_b_y,f,protocol=2)
#     f.close()
