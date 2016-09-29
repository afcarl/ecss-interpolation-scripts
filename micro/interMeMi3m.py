from math import *
import os
print("\033[32mPLEASE FOLLOW THE PROMPTS. THIS IS THE SCRIPT THAT INTERPOLATES MESO-LEVEL DISPLACEMENTS ONTO THE MICRO LEVEL MODEL.\033[0m")

Xmeso_filename = str(input("\033[32mInput the MESO file name with the .inp extension: \033[0m: "))

Xmeso_deformname = str(input("\033[32mInput the MESO displacemnets file name with .rpt extension: \033[0m: "))

Xmicro_filename = str(input("\033[32mInput the MICRO file name with the .inp extension: \033[0m: "))

Xmicro_DUMP = str(input("\033[32mPlease indicate the name of the new file including the .inp extesion. Note that you cannot use the same name as a file above... \033[0m: "))



Xcmdfilename = "interp2.py" + ".cmd"

Xcmdfile = open(Xcmdfilename, 'w');

Xwhoami = os.popen("whoami").read()[:-1]

XTHISISTHESCRIPT = "interp2.py"

Xdfile = open(XTHISISTHESCRIPT, 'w')

Xcmdfile.write("""#!/bin/csh -f
#  {0}.cmd
#
#  SGE job for only-tensionZ.py built Mon Nov 21 15:35:12 PST 2011
#
#  The following items pertain to this script
#  Use current working directory
#$ -cwd
#  input           = /dev/null
#  output          = {1}.joblog.$JOB_ID
#$ -o {1}.joblog.$JOB_ID
#  error           = Merged with joblog
#$ -j y
#  The following items pertain to the user program
#  user program    = {1}
#  arguments       = 
#  program input   = Specified by user program
#  program output  = Specified by user program
#  Resources requested
#$ -pe shared 2
#$ -l h_data=2048M,h_rt=24:00:00
#
#  Name of application for log
#$ -v QQAPP=job
#  Email address to notify
#$ -M {2}@mail
#  Notify at beginning and end of job
#$ -m bea
#  Job is not rerunable
#$ -r n
#  Uncomment the next line to have your environment variables used by SGE
# #$ -V
#
# Initialization for serial execution
#
  unalias *
  set qqversion = 
  set qqapp     = "job serial"
  set qqidir    = {3}
  set qqjob     = {0}
  set qqodir    = {3}
  cd     {3}
  source /u/local/bin/qq.sge/qr.runtime
  if ($status != 0) exit (1)
#
  echo "SGE job for only-tensionZ.py built Mon Nov 21 15:35:12 PST 2011"
  echo ""
  echo "  {0} directory:"
  echo "    "{3}
  echo "  Submitted to SGE:"
  echo "    "$qqsubmit
  echo "  SCRATCH directory:"
  echo "    "$qqscratch
#
  echo ""
  echo "{0} started on:   "` hostname -s `
  echo "{0} started at:   "` date `
  echo ""
#
# Run the user program
#

  source /u/local/Modules/default/init/modules.csh
  module load intel/11.1
  module load python/3.1

  echo {0} "" \>\& {0}.output.$JOB_ID
  echo ""
  time python3 {1}  >& {1}.output.$JOB_ID
#
  echo ""
  echo "{0} finished at:  "` date `
#
# Cleanup after serial execution
#
  source /u/local/bin/qq.sge/qr.runtime
#
  echo "-------- {1}.joblog.$JOB_ID --------" >> /u/local/apps/queue.logs/job.log.serial
 if (`wc -l {1}.joblog.$JOB_ID  | awk '{{print $1}}'` >= 1000) then
	head -50 {1}.joblog.$JOB_ID >> /u/local/apps/queue.logs/job.log.serial
	echo " "  >> /u/local/apps/queue.logs/job.log.serial
	tail -10 {1}.joblog.$JOB_ID >> /u/local/apps/queue.logs/job.log.serial
  else
	cat {1}.joblog.$JOB_ID >> /u/local/apps/queue.logs/job.log.serial
  endif
#  cat            {1}.joblog.$JOB_ID           >> /u/local/apps/queue.logs/job.log.serial
  exit (0)
""".format(XTHISISTHESCRIPT, os.getcwd()+"/"+XTHISISTHESCRIPT, Xwhoami, os.getcwd()+"/"))

Xcmdfile.close()


Xdfile.write(r"""from math import *

ALL_meso_nodes11 = []


def pull_meso_nodes11(meso):
    running = False
    node_numb = ""
    x_hat = ""
    y_hat = ""
    z_hat = ""
    count = 0
    prev_coma = 0
    for line in meso:

        node_numb = ""
        x_hat = ""
        y_hat = ""
        z_hat = ""
        count = 0
        prev_coma = 0
        if running:
            for letter in range(len(line)):
                if line[0] == "*":
                    break
                if line[letter] == " ":
                    prev_coma = letter

                if count == 3 and running:##ONLY NEED RUNNING IF NOT RUNNING OFF DUMPED FILE
                    z_hat = float(line[(prev_coma + 1):])##:end of line, not letter
                    #print(str(z_hat) + "<---- Z")
                    count +=1

                if line[letter] == "," and count == 2 and running:
                    y_hat = float(line[(prev_coma + 1):letter])
                    #print(str(y_hat) + "<---- Y")
                    count +=1

                if line[letter] == "," and count == 1 and running:
                    x_hat = float(line[(prev_coma + 1):letter])
                    #print(str(x_hat) + "<---- X")
                    count +=1

                if line[letter] == "," and count == 0 and running:
                    node_numb = int(line[0:(letter)])
                    #print(str(node_numb) + " <-- NODE")
                    count += 1
        if "*" in line:
            if "Node" in line:
                running = True
                #print("Node hit")
            else:
                running = False
        if node_numb != "":
            ALL_meso_nodes11.append([node_numb, x_hat, y_hat, z_hat])

    meso.seek(0)




ALL_eight_bricks11 = []
ALL_wedge_elms11 = []
ALL_brick_elms11 = []

def pull_elm_info11(sourcefile):
    count = 0
    temp_set = []
    prev_coma = 0
    running_wedge = False
    running_eight = False
    next_line = False
    next_line_hit = False
    running_brix = False
    for line in sourcefile:

        if running_eight and "E" not in line:
            for letter in range(len(line)):

                if line[letter] == "," and count > 0:
                    temp_set.append(int(line[(prev_coma + 1):letter]))
                    prev_coma = letter

                if line[letter] == "\n" and count > 0:
                    temp_set.append(int(line[(prev_coma + 1):letter]))
                    prev_coma = letter

                if line[letter] == "," and count == 0:
                    temp_set.append(int(line[0:(letter)]))
                    prev_coma = letter
                    #print(str(elm_numb) + " <-- elm")
                    count += 1


            ALL_eight_bricks11.append(temp_set)
            temp_set = []
            count = 0
            prev_coma = 0

        if running_wedge and "E" not in line and "*" not in line:
            for letter in range(len(line)):

                if line[letter] == "," and count > 0:
                    temp_set.append(int(line[(prev_coma + 1):letter]))
                    prev_coma = letter

                if line[letter] == "\n" and count > 0:
                    temp_set.append(int(line[(prev_coma + 1):letter]))
                    prev_coma = letter

                if line[letter] == "," and count == 0:
                    temp_set.append(int(line[0:(letter)]))
                    prev_coma = letter
                    #print(str(elm_numb) + " <-- elm")
                    count += 1


            ALL_wedge_elms11.append(temp_set)
            temp_set = []
            count = 0
            prev_coma = 0


        if running_brix and "E" not in line:
            if next_line:
                next_line_hit = True
                for letter in range(len(line)):
                    if line[letter] == "," and count > 0:
                        temp_set.append(int(line[(prev_coma + 1):letter]))
                        prev_coma = letter
                    if line[letter] == "\n" and count > 0 and line[(letter - 1)] != ",":
                        temp_set.append(int(line[(prev_coma + 1):letter]))
                        prev_coma = letter

                    if line[letter] == "," and count == 0:
                        temp_set.append(int(line[0:(letter)]))
                        prev_coma = letter
                        #print(str(elm_numb) + " <-- elm")
                        count += 1

                ALL_brick_elms11.append(temp_set)
                count =  0
                temp_set = []
                prev_coma = 0
                next_line = False



            if next_line_hit == False:
                for letter in range(len(line)):

                    if line[letter] == "," and count > 0:
                        temp_set.append(int(line[(prev_coma + 1):letter]))
                        prev_coma = letter
                        next_line = True

                    if line[letter] == "\n" and count > 0 and line[(letter - 1)] != ",":
                        temp_set.append(int(line[(prev_coma + 1):letter]))
                        prev_coma = letter

                    if line[letter] == "," and count == 0:
                        temp_set.append(int(line[0:(letter)]))
                        prev_coma = letter
                        #print(str(elm_numb) + " <-- elm")
                        count += 1

            prev_coma = 0
            count = 0
            next_line_hit = False


        if "*" in line:
            if "Element" in line and "C3D2" in line:
                running_brix = True
                running_wedge = False
                running_eight = False

            elif "Element" in line and "C3D6" in line:
                running_wedge = True
                running_brix = False
                running_eight = False

            elif "Element" in line and "C3D8" in line:
                running_eight = True
                running_brix = False
                running_wedge = False

            else:
                running_wedge = False
                running_brix = False
                running_eight = False




    sourcefile.seek(0)



Xmesofile = open("{0}")

Xdump = open("useelms.inp", 'w')

pull_meso_nodes11(Xmesofile)

pull_elm_info11(Xmesofile)


minx = 800
miny = 800
minz = 999
maxx = 1500
maxy = 1500
maxz = 1501

goodnodes = []

goodelms = []

for i in range(len(ALL_meso_nodes11)):
    if ALL_meso_nodes11[i][1] > minx and ALL_meso_nodes11[i][1] < maxx:
        if ALL_meso_nodes11[i][2] > miny and ALL_meso_nodes11[i][2] < maxy:
            if ALL_meso_nodes11[i][3] > minz and ALL_meso_nodes11[i][3] < maxz:
                goodnodes.append(ALL_meso_nodes11[i][0])




for i in range(len(goodnodes)):
    if goodnodes[i]%100 == 0:
        print(goodnodes[i])
    for elm in ALL_eight_bricks11:
        if goodnodes[i] in elm[1:] and elm[0] not in goodelms:
            goodelms.append(elm[0])
    for elm in ALL_wedge_elms11:
        if goodnodes[i] in elm[1:] and elm[0] not in goodelms:
            goodelms.append(elm[0])
    for elm in ALL_brick_elms11:
        if goodnodes[i] in elm[1:] and elm[0] not in goodelms:
            goodelms.append(elm[0])


for i in range(len(goodelms)):
    Xdump.write(str(goodelms[i])+"\n");

Xdump.close()

print(len(ALL_brick_elms11), len(ALL_eight_bricks11), "USEELM.inp done")

ALL_eight_bricks11 = []
ALL_wedge_elms11 = []
ALL_brick_elms11 = []
ALL_meso_nodes11 = []




def distance_point_to_line(m,n,pt1,pt2):
    x1,y1 = pt1
    x2,y2 = pt2

    if (x2 - x1) == 0:
        #print("Vert")
        return (m - x2)
    elif (y2 - y1) == 0:
        #print("horiz")
        return (n - y2)
    else:
        slope = (y2 - y1)/(x2 - x1)
        dist = abs(slope*slope + 1)

        return (abs((-1 * slope)*m + n + slope*x1 - y1)/sqrt(dist))


##a = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[0], polygon_2D[1], polygon_2D[5]])
##b = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[0], polygon_2D[5], polygon_2D[7]])
##c = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[7], polygon_2D[5], polygon_2D[3]])
##d = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[3], polygon_2D[5], polygon_2D[2]])
##if a or b:
##    in_hit = True
##    g_hat,h_hat,r_hat = interpolate_brick_ab(x_hat, y_hat, z_hat, polygon_2D, z_min, z_max,a_meso_ELEMENT[0],node_numb)
##    #print("Ran AB")
##
##if c or d:
##    in_hit = True
##    g_hat,h_hat,r_hat = interpolate_brick_cd(x_hat, y_hat, z_hat, polygon_2D, z_min, z_max, a_meso_ELEMENT[0],node_numb)
##    #print("CD ran one")


def interpolat_eight_node(x_n, y_n, z_n, polygon, z_mini, z_maxi,elm_num,node_num):

    g = 0
    h = 0
    z_mid = (z_maxi + z_mini)/2
    r = (z_n - z_mid)/(z_maxi - z_mid)

    temp_g1 = distance_point_to_line(x_n,y_n,polygon[0],polygon[3])##line for g = -1
    temp_g2 = distance_point_to_line(x_n,y_n,polygon[1],polygon[2])##line for g = +1

    total = (temp_g1 + temp_g2)/2

    if temp_g1 == temp_g2:
        g = 0

    else:
        if temp_g1 == min(temp_g1, temp_g2):##if temp g1 is shorter, it means it's negative
            g = -1 + (temp_g1/total)
        elif temp_g2 == min(temp_g1, temp_g2):
            g = 1 - (temp_g2/total)

    temp_h1 = distance_point_to_line(x_n,y_n,polygon[0],polygon[1])##line for h = -1
    temp_h2 = distance_point_to_line(x_n,y_n,polygon[2],polygon[3])##line for h = 0

    total = (temp_h1 + temp_h2)/2

##    if temp_h1 == temp_h2:
##        h = 0
##        print("H was 0")
##        print(
    
    if temp_h1 == min(temp_h1, temp_h2):##if temp g1 is shorter, it means it's negative
        h = -1 + (temp_h1/total)
    elif temp_h2 == min(temp_h1, temp_h2):
        h = 1 - (temp_h2/total)

##    if h == 0:
##        if distance_point_to_line(x_n,y_n,polygon[5],polygon[7]


    if g > 1:
        g = 1
    if g < -1:
        g = -1

    if h > 1:
        h = 1
    if h < -1:
        h = -1
    

    if g > 1 or g < -1:
        print("G PROBLEM!!!!")
        print(x_n, y_n, z_n)
        print(g)
        print(elm_num)
        print(node_num)

    if h > 1 or h < -1:
        print("H PROBLEM!!!!")
        print(x_n, y_n, z_n)
        print(h)
        print(elm_num)
        print(node_num)


    return g,h,r




def interpolate_brick_ab(x_n, y_n, z_n, polygon, z_mini, z_maxi,elm_num,node_num):

    g = 0
    h = 0
    z_mid = (z_maxi + z_mini)/2
    r = (z_n - z_mid)/(z_maxi - z_mid)

    temp_g1 = distance_point_to_line(x_n,y_n,polygon[0],polygon[7])##line for g = -1
    temp_g2 = distance_point_to_line(x_n,y_n,polygon[1],polygon[5])##line for g = +1

    total = (temp_g1 + temp_g2)/2

    if temp_g1 == temp_g2:
        g = 0

    else:
        if temp_g1 == min(temp_g1, temp_g2):##if temp g1 is shorter, it means it's negative
            g = -1 + (temp_g1/total)
        elif temp_g2 == min(temp_g1, temp_g2):
            g = 1 - (temp_g2/total)

    temp_h1 = distance_point_to_line(x_n,y_n,polygon[0],polygon[1])##line for h = -1
    temp_h2 = distance_point_to_line(x_n,y_n,polygon[2],polygon[3])##line for h = 0

    total = (temp_h1 + temp_h2)/2

##    if temp_h1 == temp_h2:
##        h = 0
##        print("H was 0")
##        print(
    
    if temp_h1 == min(temp_h1, temp_h2):##if temp g1 is shorter, it means it's negative
        h = -1 + (temp_h1/total)
    elif temp_h2 == min(temp_h1, temp_h2):
        h = 1 - (temp_h2/total)

##    if h == 0:
##        if distance_point_to_line(x_n,y_n,polygon[5],polygon[7]


    if g > 1:
        g = 1
    if g < -1:
        g = -1

    if h > 1:
        h = 1
    if h < -1:
        h = -1
    

    if g > 1 or g < -1:
        print("G PROBLEM!!!!")
        print(x_n, y_n, z_n)
        print(g)
        print(elm_num)
        print(node_num)

    if h > 1 or h < -1:
        print("H PROBLEM!!!!")
        print(x_n, y_n, z_n)
        print(h)
        print(elm_num)
        print(node_num)


    return g,h,r


def interpolate_brick_cd(x_n, y_n, z_n, polygon, z_mini, z_maxi,elm_num,node_num):
    g = 0
    h = 0
    z_mid = (z_maxi + z_mini)/2
    r = (z_n - z_mid)/(z_maxi - z_mid)

    temp_g1 = distance_point_to_line(x_n,y_n,polygon[7],polygon[3])##line for g = -1
    temp_g2 = distance_point_to_line(x_n,y_n,polygon[2],polygon[5])##line for g = +1

    total = (temp_g1 + temp_g2)/2

    if temp_g1 == temp_g2:
        g = 0

    else:
        if temp_g1 == min(temp_g1, temp_g2):##if temp g1 is shorter, it means it's negative
            g = -1 + (temp_g1/total)
        elif temp_g2 == min(temp_g1, temp_g2):
            g = 1 - (temp_g2/total)



    temp_h1 = distance_point_to_line(x_n,y_n,polygon[0],polygon[1])##line for h = -1
    temp_h2 = distance_point_to_line(x_n,y_n,polygon[2],polygon[3])##line for h = 0

    total = (temp_h1 + temp_h2)/2

##    if temp_h1 == temp_h2:
##        h = 0

    if temp_h1 == min(temp_h1, temp_h2):##if temp g1 is shorter, it means it's negative
        h = -1 + (temp_h1/total)
    elif temp_h2 == min(temp_h1, temp_h2):
        h = 1 - (temp_h2/total)

    if g > 1:
        g = 1
    if g < -1:
        g = -1

    if h > 1:
        h = 1
    if h < -1:
        h = -1


    if g > 1 or g < -1:
        print("G PROBLEM!!!!")
        print(x_n, y_n, z_n)
        print(g)
        print(elm_num)
        print(node_num)

    if h > 1 or h < -1:
        print("H PROBLEM!!!!")
        print(x_n, y_n, z_n)
        print(h)
        print(elm_num)
        print(node_num)

    if r > 1 or r < -1:
        print("H PROBLEM!!!!")
        print(x_n, y_n, z_n)
        print(r)


    return g,h,r





def pull_deformations(source_file):###This generates the deformations

    source = open(source_file)##TO READ

    node_number = 0
    holder = ""
    full_count = 0
    running_M = False
    hit_M = False

    for line in source:
        count = 0
        prev_coma = 0

        count_M = 0

        if "Minimum" in line:
            break


        if running_M:
            try:
                nodes_to_deform.append([int(line[0:17]), float(line[33:51]), float(line[51:67]), float(line[67:-1])])

            except:
                pass
        if "---------------------------------------------" in line:
            running_M = True


    source.seek(0)
    source.close()

def pull_meso_nodes(meso):
    running = False
    node_numb = ""
    x_hat = ""
    y_hat = ""
    z_hat = ""
    count = 0
    prev_coma = 0
    for line in meso:

        node_numb = ""
        x_hat = ""
        y_hat = ""
        z_hat = ""
        count = 0
        prev_coma = 0
        if running:
            for letter in range(len(line)):
                if line[0] == "*":
                    break
                if line[letter] == " ":
                    prev_coma = letter

                if count == 3 and running:##ONLY NEED RUNNING IF NOT RUNNING OFF DUMPED FILE
                    z_hat = float(line[(prev_coma + 1):])##:end of line, not letter
                    #print(str(z_hat) + "<---- Z")
                    count +=1

                if line[letter] == "," and count == 2 and running:
                    y_hat = float(line[(prev_coma + 1):letter])
                    #print(str(y_hat) + "<---- Y")
                    count +=1

                if line[letter] == "," and count == 1 and running:
                    x_hat = float(line[(prev_coma + 1):letter])
                    #print(str(x_hat) + "<---- X")
                    count +=1

                if line[letter] == "," and count == 0 and running:
                    node_numb = int(line[0:(letter)])
                    #print(str(node_numb) + " <-- NODE")
                    count += 1
        if "*" in line:
            if "Node" in line:
                running = True
                #print("Node hit")
            else:
                running = False
        if node_numb != "":
            ALL_meso_nodes.append([node_numb, x_hat, y_hat, z_hat])

    meso.seek(0)


def pull_micro_nodes(meso):
    running = False
    partCYL_micro_nodes = []
    partCYLC_micro_nodes = []
    partbox_micro_nodes = []
    n_count = 0
    node_numb = ""
    x_hat = ""
    y_hat = ""
    z_hat = ""
    count = 0
    prev_coma = 0
    for line in meso:
        node_numb = ""
        x_hat = ""
        y_hat = ""
        z_hat = ""
        count = 0
        prev_coma = 0
        if running:
            for letter in range(len(line)):
                if line[0] == "*":
                    break
                if line[letter] == " ":
                    prev_coma = letter

                if count == 3 and running:##ONLY NEED RUNNING IF NOT RUNNING OFF DUMPED FILE
                    z_hat = float(line[(prev_coma + 1):])##:end of line, not letter
                    #print(str(z_hat) + "<---- Z")
                    count +=1

                if line[letter] == "," and count == 2 and running:
                    y_hat = float(line[(prev_coma + 1):letter])
                    #print(str(y_hat) + "<---- Y")
                    count +=1

                if line[letter] == "," and count == 1 and running:
                    x_hat = float(line[(prev_coma + 1):letter])
                    #print(str(x_hat) + "<---- X")
                    count +=1

                if line[letter] == "," and count == 0 and running:
                    node_numb = int(line[0:(letter)])
                    #print(str(node_numb) + " <-- NODE")
                    count += 1
        if node_numb != "" and n_count == 2:
            ##ONLY WILL APPEND MICRO NODES ON THE EDGES OF THE MICRO CUBE
            if ((z_hat + zs) <= 1000.1) or ((z_hat + zs) >= 1497.9) or ((x_hat + xs) <= 879.9) or ((x_hat + xs) >= 1379.7) or ((y_hat + ys) <= 881.6) or ((y_hat + ys) >= 1381):
                partCYL_micro_nodes.append([node_numb, x_hat, y_hat, z_hat])

        if node_numb != "" and n_count == 3:
            ##ONLY WILL APPEND MICRO NODES ON THE EDGES OF THE MICRO CUBE
            if ((z_hat + zs) <= 1000.1) or ((z_hat + zs) >= 1497.9) or ((x_hat + xs) <= 879.9) or ((x_hat + xs) >= 1379.7) or ((y_hat + ys) <= 881.6) or ((y_hat + ys) >= 1381):
                partCYLC_micro_nodes.append([node_numb, x_hat, y_hat, z_hat])

        if node_numb != "" and n_count == 1:
            ##ONLY WILL APPEND MICRO NODES ON THE EDGES OF THE MICRO CUBE
            if ((z_hat + zs) <= 1000.1) or ((z_hat + zs) >= 1497.9) or ((x_hat + xs) <= 879.9) or ((x_hat + xs) >= 1379.7) or ((y_hat + ys) <= 881.6) or ((y_hat + ys) >= 1381):
                partbox_micro_nodes.append([node_numb, x_hat + 1000, y_hat + 1000, z_hat + 1000])
        if "*" in line:
            if "Node" in line:
                running = True
                n_count = n_count + 1
                #print("Node hit")
            else:
                running = False

##We need to generate the instances because there are 2 instances for every part

    part_C1 = []
    part_C2 = []
    part_CC1 = []
    part_CC2 = []

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##CHANGE THIS: This is where the instance information is hardcoded


    for elm in part_C1:
        if elm[3] == -1:
            part_C1.remove(elm)

    for elm in part_C2:
        if elm[3] == -1:
            part_C2.remove(elm)
    for elm in part_CC1:
        if elm[3] == -1:
            part_CC1.remove(elm)
    for elm in part_CC2:
        if elm[3] == -1:
            part_CC2.remove(elm)

    for elm in partCYLC_micro_nodes:
        if elm[3] == -1:
            partCYLC_micro_nodes.remove(elm)

    for elm in partCYL_micro_nodes:
        if elm[3] == -1:
            partCYL_micro_nodes.remove(elm)


    for elmnt in partCYLC_micro_nodes:
        part_C1.append([elmnt[0], (elmnt[1] + 1028.3), (elmnt[2] + 1239.1), (elmnt[3] + 1001)])
        part_C2.append([elmnt[0], (elmnt[1] + 1243.5), (elmnt[2] + 1029.2), (elmnt[3] + 1001)])

    for elmnt in partCYL_micro_nodes:
        part_CC1.append([elmnt[0], (elmnt[1] + 1000), (elmnt[2] + 1000), (elmnt[3] + 1001)])
        part_CC2.append([elmnt[0], (elmnt[1] + 1267.3), (elmnt[2] + 1262), (elmnt[3] + 1001)])

    for elm in part_C1:
        if elm[3] == 999 or elm[3] == 1000 or elm[3] == 1001:
            part_C1.remove(elm)

    for elm in part_C2:
        if elm[3] == 999 or elm[3] == 1000 or elm[3] == 1001:
            part_C2.remove(elm)
    for elm in part_CC1:
        if elm[3] == 999 or elm[3] == 1000 or elm[3] == 1001:
            part_CC1.remove(elm)
    for elm in part_CC2:
        if elm[3] == 999 or elm[3] == 1000 or elm[3] == 1001:
            part_CC2.remove(elm)

    ALL_micro_nodes.append(part_C1)
    ALL_micro_nodes.append(part_C2)
    ALL_micro_nodes.append(part_CC1)
    ALL_micro_nodes.append(part_CC2)
    ALL_micro_nodes.append(partbox_micro_nodes)
    print(len(part_C1))
    print(len(part_C2))
    print(len(part_CC1))
    print(len(part_CC2))
    print(len(partbox_micro_nodes));

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    meso.seek(0)

global ALL_eight_bricks
ALL_eight_bricks = []

def pull_elm_info(sourcefile):
    count = 0
    temp_set = []
    prev_coma = 0
    running_wedge = False
    running_eight = False
    next_line = False
    next_line_hit = False
    running_brix = False
    for line in sourcefile:

        if running_eight and "E" not in line:
            for letter in range(len(line)):

                if line[letter] == "," and count > 0:
                    temp_set.append(int(line[(prev_coma + 1):letter]))
                    prev_coma = letter

                if line[letter] == "\n" and count > 0:
                    temp_set.append(int(line[(prev_coma + 1):letter]))
                    prev_coma = letter

                if line[letter] == "," and count == 0:
                    temp_set.append(int(line[0:(letter)]))
                    prev_coma = letter
                    #print(str(elm_numb) + " <-- elm")
                    count += 1


            ALL_eight_bricks.append(temp_set)
            temp_set = []
            count = 0
            prev_coma = 0

        if running_wedge and "E" not in line and "*" not in line:
            for letter in range(len(line)):

                if line[letter] == "," and count > 0:
                    temp_set.append(int(line[(prev_coma + 1):letter]))
                    prev_coma = letter

                if line[letter] == "\n" and count > 0:
                    temp_set.append(int(line[(prev_coma + 1):letter]))
                    prev_coma = letter

                if line[letter] == "," and count == 0:
                    temp_set.append(int(line[0:(letter)]))
                    prev_coma = letter
                    #print(str(elm_numb) + " <-- elm")
                    count += 1


            ALL_wedge_elms.append(temp_set)
            temp_set = []
            count = 0
            prev_coma = 0


        if running_brix and "E" not in line:
            if next_line:
                next_line_hit = True
                for letter in range(len(line)):
                    if line[letter] == "," and count > 0:
                        temp_set.append(int(line[(prev_coma + 1):letter]))
                        prev_coma = letter
                    if line[letter] == "\n" and count > 0 and line[(letter - 1)] != ",":
                        temp_set.append(int(line[(prev_coma + 1):letter]))
                        prev_coma = letter

                    if line[letter] == "," and count == 0:
                        temp_set.append(int(line[0:(letter)]))
                        prev_coma = letter
                        #print(str(elm_numb) + " <-- elm")
                        count += 1

                ALL_brick_elms.append(temp_set)
                count =  0
                temp_set = []
                prev_coma = 0
                next_line = False



            if next_line_hit == False:
                for letter in range(len(line)):

                    if line[letter] == "," and count > 0:
                        temp_set.append(int(line[(prev_coma + 1):letter]))
                        prev_coma = letter
                        next_line = True

                    if line[letter] == "\n" and count > 0 and line[(letter - 1)] != ",":
                        temp_set.append(int(line[(prev_coma + 1):letter]))
                        prev_coma = letter

                    if line[letter] == "," and count == 0:
                        temp_set.append(int(line[0:(letter)]))
                        prev_coma = letter
                        #print(str(elm_numb) + " <-- elm")
                        count += 1

            prev_coma = 0
            count = 0
            next_line_hit = False


        if "*" in line:
            if "Element" in line and "C3D2" in line:
                running_brix = True
                running_wedge = False
                running_eight = False

            elif "Element" in line and "C3D6" in line:
                running_wedge = True
                running_brix = False
                running_eight = False

            elif "Element" in line and "C3D8" in line:
                running_eight = True
                running_brix = False
                running_wedge = False

            else:
                running_wedge = False
                running_brix = False
                running_eight = False




    sourcefile.seek(0)



def interpolate_6wedge(x_n, y_n, z_n, g_hat, h_hat, r_hat, node_one):
    p_vector = (x_n - node_one[1], y_n - node_one[2])##X,Y need the 1000 translation


    ##Cramer's rule
    u = (p_vector[0]*h_hat[1] - p_vector[1]*h_hat[0])/(g_hat[0]*h_hat[1] - g_hat[1]*h_hat[0])

    v = (p_vector[1]*g_hat[0] - p_vector[0]*g_hat[1])/(g_hat[0]*h_hat[1] - g_hat[1]*h_hat[0])

    w = (z_n - r_hat[0])/(r_hat[1] - r_hat[0])##Z_hat needs the translation of 1000


    ##In case we don't meet the theory restrictions on g,h...
    if u > 1 or v > 1 or w > 1:
        print("TOO LARGE!!!!! u,v,w  ---> (" + str(u) + ", " + str(v) + ", " + str(w) + ") x,y,z below")
        print(x_n, y_n, z_n, node_n)

    if (u+v) > 1:
        print("ADDS BADLY!!!! u,v,w  ---> (" + str(u) + ", " + str(v) + ", " + str(w) + ") x,y,z below")
        print(x_n, y_n, z_n, node_n)


    return (u, v, w)

def inverse_interpolate_6wedge(g_n, h_n, r_n, g_hat, h_hat, r_hat, node_one):
    ##Cramer's rule

    x = g_n*g_hat[0] + h_n*h_hat[0] + node_one[1]
    y = g_n*g_hat[1] + h_n*h_hat[1] + node_one[2]
    z = (r_n)*(r_hat[1] - r_hat[0]) + r_hat[0]##Z_hat needs the translation of 1000
    ##Recall r_hat defined as (z_min, z_max)....

    return (x, y, z)



def point_on_line(query_x, query_y, pt_1, pt_2):
    x_1,y_1 = pt_1
    x_2,y_2 = pt_2

    vector_1 = (x_2 - x_1, y_2 - y_1)
    vector_2 = (query_x - x_1, query_y - y_1)

    if (((x_2 - x_1) * (query_y - y_1)) - ((y_2 - y_1) * (query_x - x_1))) == 0:
        if (query_x <= max(x_1,x_2)) and (query_x >= min(x_1,x_2)):
            if (query_y <= max(y_1,y_2)) and (query_y >= min(y_1,y_2)):
                return True


    return False


def point_inside_polygon(x,y,poly):##Can this be applied to 20 node bricks?
    if point_on_line(x,y,poly[0], poly[1]):
        return True
    if point_on_line(x,y,poly[0], poly[2]):
        return True
    if point_on_line(x,y,poly[1], poly[2]):
        return True

    n = len(poly)
    inside =False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
## CODE FROM http://www.ariel.com.au/a/python-point-int-poly.html
    return inside


def function_final():
    global in_hit
    global running_node
    global hit_M
    global ALL_micro_nodes
    global nodes_to_deform##HOLDS the nodes to be deformed
    global ALL_meso_nodes
    global ALL_wedge_elms
    global ALL_brick_elms
    global meso_node_set
    global final_def_set
    global FULL_meso_elset
    global xs
    global ys
    global zs
    FULL_meso_elset = []
    global micro_part_count
    micro_part_count = 0

    file_elms = open("useelms.inp")
    prev_cma = 0
    for line in file_elms:
        try:
            FULL_meso_elset.append(int(line))
        except:
            pass;
    
    print("FULL MESO ELSE:" , FULL_meso_elset)
    final_def_set = []

    running_node = False
    hit_M = False

    nodes_to_deform = []##HOLDS the nodes to be deformed
    ALL_micro_nodes = []
    ALL_meso_nodes = []
    ALL_wedge_elms = []
    ALL_brick_elms = []
    (xs, ys, zs) = (0,0,0)
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##CHANGE THIS: This is where all the file names are coded.
    deformations = "{1}"
    print("pulling deformation info......")
    mes = "{0}"
    mic = "{2}"
    pull_deformations(deformations)

    micro_file = open(mic, "r")
    micro_file_lines = micro_file.readlines()
    hit_1 = False
    for line in micro_file_lines:
        if hit_1:
            line_entries = line.strip("\n").split(",")
            xs = float(line_entries[0])
            ys = float(line_entries[1])
            zs = float(line_entries[2])
            break
        if "*Instance, name=BOXCNOCANL-1" in line:
            hit_1 = True

    meso = open(mes)
    micro = open(mic)
    print("Pulling element info")
    pull_elm_info(meso)
    print("pulling meso nodes")
    pull_meso_nodes(meso)
    print("pulling micro nodes")
    pull_micro_nodes(micro)

####    global neal_dx
####    global neal_dy
####    global neal_dz
####
####    global n_maxdx
####    global n_maxdy
####    global n_maxdz
####    global n_mindx
####    global n_mindy
####    global n_mindz
####
####    n_mindx = 999999999999
####    n_mindy = 999999999999
####    n_mindz = 999999999999
####    n_maxdx = -9999999999
####    n_maxdy = -9999999999
####    n_maxdz = -9999999999
####
####    neal_dx = 0
####    neal_dy = 0
####    neal_dz = 0
####    neal_count = 0
####
####    temp_s = []
####
####    print(ALL_eight_bricks[0])
####    s_hit = False
####    for elm in FULL_meso_elset:
####        #print("MOO")
####        for lmnt in ALL_eight_bricks:
####            if lmnt[0] == elm:
####                temp_s.append(lmnt[1:])
######                print("HIT")
####        for lmnt in ALL_wedge_elms:
####            if lmnt[0] == elm:
####                temp_s.append(lmnt[1:])
####        for lmnt in ALL_brick_elms:
####            if lmnt[0] == elm:
####                temp_s.append(lmnt[1:])
####
####        print("TEMPS: ", temp_s)
####
####        for m in range(len(temp_s)):
####            neal_count = neal_count + 1
####            neal_dx = neal_dx + nodes_to_deform[temp_s[m]-1][1]
####            neal_dy = neal_dy + nodes_to_deform[temp_s[m]-1][2]
####            neal_dz = neal_dz + nodes_to_deform[temp_s[m]-1][3]
####            if (nodes_to_deform[m-1][1] > n_maxdx):
####                n_maxdx = nodes_to_deform[temp_s[m]-1][1]
####            if (nodes_to_deform[m-1][1] < n_mindx):
####                n_mindx = nodes_to_deform[temp_s[m]-1][1]
####                
####            if (nodes_to_deform[m-1][2] > n_maxdy):
####                n_maxdy = nodes_to_deform[temp_s[m]-1][2]
####            if (nodes_to_deform[m-1][2] < n_mindy):
####                n_mindy = nodes_to_deform[temp_s[m]-1][2]
####
####            if (nodes_to_deform[m-1][3] > n_maxdz):
####                n_maxdz = nodes_to_deform[temp_s[m]-1][3]
####            if (nodes_to_deform[m-1][3] < n_mindz):
####                n_mindz = nodes_to_deform[temp_s[m]-1][3]
####
####    neal_dx = neal_dx/neal_count
####    neal_dy = neal_dy/neal_count
####    neal_dz = neal_dz/neal_count
####
####
####    print(neal_dx, neal_dy, neal_dz, "NEALDXDYDZ")


    deform_matrix_wedge = []##will hold all deformation for a wedge
    ##initialize deformation x,y,z
    for number in range(6):
        temp_matrix = []
        for numb in range(3):
            temp_matrix.append(0)

        deform_matrix_wedge.append(temp_matrix)


    deform_matrix_brick = []##will hold all deformations for a brick
    ##initialize
    for number in range(20):
        temp_matrix = []
        for numb in range(3):
            temp_matrix.append(0)

        deform_matrix_brick.append(temp_matrix)

    running = False
    z_min = 30000 ###RESET TO 1650?
    z_max = 0
    x_min = 30000
    x_max = 0
    y_min = 30000
    y_max = 0
    node_numb = ""
    x_hat = 0
    y_hat = 0
    z_hat = 0
    count = 0
    prev_coma = 0
    meso_node_set = []
    node_set = []
    polygon_2D = []
    polygon_3D = []
    interpol_set = []

    elm_is_a_brick = False
    elm_is_a_wedge = False
    elm_is_a_eightbrick = False
    ##These sets will hold the final deformations on the nodes.
    global def_C1
    global def_C2
    global def_CC1
    global def_CC2
    global def_box
    
    def_C1 = []
    def_C2 = []
    def_CC1 = []
    def_CC2 = []
    def_box = []

    micro_part_count = 0

#####MAKE THIS 8 node bricks
    for a_meso_ELEMENT in ALL_eight_bricks:
        micro_part_count = 0
        node_set = a_meso_ELEMENT[1:]
        elm_is_a_brick = True


        if a_meso_ELEMENT[0] % 10000 == 0:
            print(a_meso_ELEMENT[0])

        elm_run = a_meso_ELEMENT[0] in FULL_meso_elset

        
        if elm_run == False:
            pass
        else:
            for elm in node_set:
                for elmnt in ALL_meso_nodes:
                    if elmnt[0] == elm:
                        meso_node_set.append(elmnt)
                        break
            node_set = []
            if elm_is_a_brick:
            
                z_min = meso_node_set[0][3]
                z_max = meso_node_set[5][3]

##        
##                print(a_meso_ELEMENT)
##                print(meso_node_set)
##                
##                print(z_min)
##                print(z_max)

                for elm in meso_node_set:
                    if elm[1] <= x_min:
                        x_min = elm[1]
                    if elm[1] >= x_max:
                        x_max = elm[1]

                for elm in meso_node_set:
                    if elm[2] <= y_min:
                        y_min = elm[2]
                    if elm[2] >= y_max:
                        y_max = elm[2]

                for elm in meso_node_set:
                    if z_min == elm[3]:
                        polygon_2D.append((elm[1], elm[2]))
                        polygon_3D.append([elm[0], elm[1], elm[2], elm[3]])



                ##We need to pull the deformation info:

                for i in range(len(nodes_to_deform)):
                    for j in range(len(meso_node_set)):
                        if meso_node_set[j][0] == nodes_to_deform[i][0]:
                            #print(meso_node_set[j][0])
                            #print(nodes_to_deform[i][0])
                            deform_matrix_brick[j][0] = nodes_to_deform[i][1]
                            deform_matrix_brick[j][1] = nodes_to_deform[i][2]
                            deform_matrix_brick[j][2] = nodes_to_deform[i][3]


                ##now we have to determine whether a point is in the polygon
                global in_hit
                in_hit = False
                for a_list in ALL_micro_nodes:

                    micro_part_count = micro_part_count + 1
                    #print(micro_part_count)

                    for an_elm in a_list:
                        in_hit = False##will be needed so interpolation will not run twice
                        deform_i = 0
                        deform_j = 0
                        deform_k = 0
                        node_numb = an_elm[0]
                        g_hat = 0
                        h_hat = 0
                        r_hat = 0
                        a = False
                        b = False
                        c = False
                        d = False
                        x_hat = an_elm[1]
                        y_hat = an_elm[2]
                        z_hat = an_elm[3]
                        if (z_hat >= z_min) and (z_hat <= z_max):
                            #print("we hit z")
                            if (x_hat >= x_min) and (x_hat <= x_max) and (y_hat >= y_min) and (y_hat <= y_max):
                                #print("We hit xy")
                                a = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[0], polygon_2D[1], polygon_2D[2]])
                                b = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[0], polygon_2D[3], polygon_2D[2]])

                                ##IF a or b, then g in [-1,1] but h in [-1, 0] |||||| if c or d, g in [-1,1] but h in [0,1]
                                if a or b:
                                    in_hit = True
                                    g_hat,h_hat,r_hat = interpolat_eight_node(x_hat, y_hat, z_hat, polygon_2D, z_min, z_max,a_meso_ELEMENT[0],node_numb)
                                    #print("Ran AB")



                                if in_hit:
##                                    print("inhit")
##                                    print(micro_part_count)
                                    ##these are double checked and written out correctly
                                    deform_i = 1/8*(1-g_hat)*(1-h_hat)*(1-r_hat)*deform_matrix_brick[0][0] +\
                                               1/8*(1+g_hat)*(1-h_hat)*(1-r_hat)*deform_matrix_brick[1][0] +\
                                               1/8*(1+g_hat)*(1+h_hat)*(1-r_hat)*deform_matrix_brick[2][0] +\
                                               1/8*(1-g_hat)*(1+h_hat)*(1-r_hat)*deform_matrix_brick[3][0] +\
                                               1/8*(1-g_hat)*(1-h_hat)*(1+r_hat)*deform_matrix_brick[4][0] +\
                                               1/8*(1+g_hat)*(1-h_hat)*(1+r_hat)*deform_matrix_brick[5][0] +\
                                               1/8*(1+g_hat)*(1+h_hat)*(1+r_hat)*deform_matrix_brick[6][0] +\
                                               1/8*(1-g_hat)*(1+h_hat)*(1+r_hat)*deform_matrix_brick[7][0]

                                    deform_j = 0 - 1/8*(1-g_hat)*(1-h_hat)*(1-r_hat)*deform_matrix_brick[0][1] +\
                                               1/8*(1+g_hat)*(1-h_hat)*(1-r_hat)*deform_matrix_brick[1][1] +\
                                               1/8*(1+g_hat)*(1+h_hat)*(1-r_hat)*deform_matrix_brick[2][1] +\
                                               1/8*(1-g_hat)*(1+h_hat)*(1-r_hat)*deform_matrix_brick[3][1] +\
                                               1/8*(1-g_hat)*(1-h_hat)*(1+r_hat)*deform_matrix_brick[4][1] +\
                                               1/8*(1+g_hat)*(1-h_hat)*(1+r_hat)*deform_matrix_brick[5][1] +\
                                               1/8*(1+g_hat)*(1+h_hat)*(1+r_hat)*deform_matrix_brick[6][1] +\
                                               1/8*(1-g_hat)*(1+h_hat)*(1+r_hat)*deform_matrix_brick[7][1]

                                    deform_k = 0 - 1/8*(1-g_hat)*(1-h_hat)*(1-r_hat)*deform_matrix_brick[0][2] +\
                                               1/8*(1+g_hat)*(1-h_hat)*(1-r_hat)*deform_matrix_brick[1][2] +\
                                               1/8*(1+g_hat)*(1+h_hat)*(1-r_hat)*deform_matrix_brick[2][2] +\
                                               1/8*(1-g_hat)*(1+h_hat)*(1-r_hat)*deform_matrix_brick[3][2] +\
                                               1/8*(1-g_hat)*(1-h_hat)*(1+r_hat)*deform_matrix_brick[4][2] +\
                                               1/8*(1+g_hat)*(1-h_hat)*(1+r_hat)*deform_matrix_brick[5][2] +\
                                               1/8*(1+g_hat)*(1+h_hat)*(1+r_hat)*deform_matrix_brick[6][2] +\
                                               1/8*(1-g_hat)*(1+h_hat)*(1+r_hat)*deform_matrix_brick[7][2]


                                    if micro_part_count == 1:
##                                        print("def_c1 appended")
                                        def_C1.append([node_numb, deform_i, deform_j, deform_k])
                                    if micro_part_count == 2:
##                                        print("def_                         C2 appened")
                                        def_C2.append([node_numb, deform_i, deform_j, deform_k])
                                    if micro_part_count == 3:
##                                        print("appended")
                                        def_CC1.append([node_numb, deform_i, deform_j, deform_k])
                                    if micro_part_count == 4:
##                                        print("APPENED")
                                        def_CC2.append([node_numb, deform_i, deform_j, deform_k])
                                    if micro_part_count == 5:
##                                        print("box append")
                                        def_box.append([node_numb, deform_i, deform_j, deform_k])
                                    


                                    #dump.write(str(node_numb).rjust(15) + "," + str(g_hat).rjust(17) + "," + str(h_hat).rjust(17) + "," + str(r_hat).rjust(17) + "\n")
                                    #dump.write(str(an_elm[0]).rjust(15) + "," + str(an_elm[1]+1000).rjust(17) + "," + str(an_elm[2]+1000).rjust(17) + "," + str(an_elm[3]+1000).rjust(17) + "\n")
                                    #dump.write(str(deform_i).rjust(15+17) + "," + str(deform_j).rjust(17) + "," + str(deform_k).rjust(17) + "\n")

        meso_node_set = []
        polygon_2D = []
        polygon_3D = []
        z_min = 213432
        z_max = 0
        x_min = 123512
        x_max = 0
        y_min = 161237
        y_max = 0
        node_numb = ""
        x_hat = 0
        y_hat = 0
        z_hat = 0
        count = 0
        prev_coma = 0

        deform_matrix_brick = []##will hold all deformations for a brick
        ##initialize
        for number in range(20):
            temp_matrix = []
            for numb in range(3):
                temp_matrix.append(0)

            deform_matrix_brick.append(temp_matrix)

    micro_part_count = 0
    print("done with 8_brix")


    micro_part_count = 0


    for a_meso_ELEMENT in ALL_brick_elms:
        micro_part_count = 0
        node_set = a_meso_ELEMENT[1:]
        elm_is_a_brick = True

##    for member in ALL_wedge_elms:
##        if elm_toquery == member[0]:
##            node_set = member[1:]
##            elm_is_a_wedge = True
##            print("WEDGE HIT!!!")
##            break

        if a_meso_ELEMENT[0] % 10000 == 0:
            print(a_meso_ELEMENT[0])

        elm_run = a_meso_ELEMENT[0] in FULL_meso_elset

        
        if elm_run == False:
            pass
        else:
            for elm in node_set:
                for elmnt in ALL_meso_nodes:
                    if elmnt[0] == elm:
                        meso_node_set.append(elmnt)
                        break
            node_set = []
            if elm_is_a_brick:
            
                z_min = meso_node_set[0][3]
                z_max = meso_node_set[5][3]

##        
##                print(a_meso_ELEMENT)
##                print(meso_node_set)
##                
##                print(z_min)
##                print(z_max)

                for elm in meso_node_set:
                    if elm[1] <= x_min:
                        x_min = elm[1]
                    if elm[1] >= x_max:
                        x_max = elm[1]

                for elm in meso_node_set:
                    if elm[2] <= y_min:
                        y_min = elm[2]
                    if elm[2] >= y_max:
                        y_max = elm[2]

                for elm in meso_node_set:
                    if z_min == elm[3]:
                        polygon_2D.append((elm[1], elm[2]))
                        polygon_3D.append([elm[0], elm[1], elm[2], elm[3]])



                ##We need to pull the deformation info:

                for i in range(len(nodes_to_deform)):
                    for j in range(len(meso_node_set)):
                        if meso_node_set[j][0] == nodes_to_deform[i][0]:
                            #print(meso_node_set[j][0])
                            #print(nodes_to_deform[i][0])
                            deform_matrix_brick[j][0] = nodes_to_deform[i][1]
                            deform_matrix_brick[j][1] = nodes_to_deform[i][2]
                            deform_matrix_brick[j][2] = nodes_to_deform[i][3]


                ##now we have to determine whether a point is in the polygon
                in_hit = False
                for a_list in ALL_micro_nodes:

                    micro_part_count = micro_part_count + 1
                    #print(micro_part_count)

                    for an_elm in a_list:
                        in_hit = False##will be needed so interpolation will not run twice
                        deform_i = 0
                        deform_j = 0
                        deform_k = 0
                        node_numb = an_elm[0]
                        g_hat = 0
                        h_hat = 0
                        r_hat = 0
                        a = False
                        b = False
                        c = False
                        d = False
                        x_hat = an_elm[1]
                        y_hat = an_elm[2]
                        z_hat = an_elm[3]
                        if (z_hat >= z_min) and (z_hat <= z_max):
                            #print("we hit z")
                            if (x_hat >= x_min) and (x_hat <= x_max) and (y_hat >= y_min) and (y_hat <= y_max):
                                #print("We hit xy")
                                a = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[0], polygon_2D[1], polygon_2D[5]])
                                b = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[0], polygon_2D[5], polygon_2D[7]])
                                c = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[7], polygon_2D[5], polygon_2D[3]])
                                d = point_inside_polygon((an_elm[1]), (an_elm[2]), [polygon_2D[3], polygon_2D[5], polygon_2D[2]])

                                ##IF a or b, then g in [-1,1] but h in [-1, 0] |||||| if c or d, g in [-1,1] but h in [0,1]
                                if a or b:
                                    in_hit = True
                                    g_hat,h_hat,r_hat = interpolate_brick_ab(x_hat, y_hat, z_hat, polygon_2D, z_min, z_max,a_meso_ELEMENT[0],node_numb)
                                    #print("Ran AB")

                                if c or d:
                                    in_hit = True
                                    g_hat,h_hat,r_hat = interpolate_brick_cd(x_hat, y_hat, z_hat, polygon_2D, z_min, z_max, a_meso_ELEMENT[0],node_numb)
                                    #print("CD ran one")



                                if in_hit:
##                                    print("inhit")
##                                    print(micro_part_count)
                                    ##these are double checked and written out correctly
                                    deform_i = 0 - 1/8*(1-g_hat)*(1-h_hat)*(1-r_hat)*(2+g_hat+h_hat+r_hat)*deform_matrix_brick[0][0] -\
                                               1/8*(1+g_hat)*(1-h_hat)*(1-r_hat)*(2-g_hat+h_hat+r_hat)*deform_matrix_brick[1][0] -\
                                               1/8*(1+g_hat)*(1+h_hat)*(1-r_hat)*(2-g_hat-h_hat+r_hat)*deform_matrix_brick[2][0] -\
                                               1/8*(1-g_hat)*(1+h_hat)*(1-r_hat)*(2+g_hat-h_hat+r_hat)*deform_matrix_brick[3][0] -\
                                               1/8*(1-g_hat)*(1-h_hat)*(1+r_hat)*(2+g_hat+h_hat-r_hat)*deform_matrix_brick[4][0] -\
                                               1/8*(1+g_hat)*(1-h_hat)*(1+r_hat)*(2-g_hat+h_hat-r_hat)*deform_matrix_brick[5][0] -\
                                               1/8*(1+g_hat)*(1+h_hat)*(1+r_hat)*(2-g_hat-h_hat-r_hat)*deform_matrix_brick[6][0] -\
                                               1/8*(1-g_hat)*(1+h_hat)*(1+r_hat)*(2+g_hat-h_hat-r_hat)*deform_matrix_brick[7][0] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1-h_hat)*(1-r_hat)*deform_matrix_brick[8][0] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1+g_hat)*(1-r_hat)*deform_matrix_brick[9][0] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1+h_hat)*(1-r_hat)*deform_matrix_brick[10][0] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1-g_hat)*(1-r_hat)*deform_matrix_brick[11][0] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1-h_hat)*(1+r_hat)*deform_matrix_brick[12][0] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1+g_hat)*(1+r_hat)*deform_matrix_brick[13][0] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1+h_hat)*(1+r_hat)*deform_matrix_brick[14][0] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1-g_hat)*(1+r_hat)*deform_matrix_brick[15][0] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1-g_hat)*(1-h_hat)*deform_matrix_brick[16][0] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1+g_hat)*(1-h_hat)*deform_matrix_brick[17][0] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1+g_hat)*(1+h_hat)*deform_matrix_brick[18][0] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1-g_hat)*(1+h_hat)*deform_matrix_brick[19][0]

                                    deform_j = 0 - 1/8*(1-g_hat)*(1-h_hat)*(1-r_hat)*(2+g_hat+h_hat+r_hat)*deform_matrix_brick[0][1] -\
                                               1/8*(1+g_hat)*(1-h_hat)*(1-r_hat)*(2-g_hat+h_hat+r_hat)*deform_matrix_brick[1][1] -\
                                               1/8*(1+g_hat)*(1+h_hat)*(1-r_hat)*(2-g_hat-h_hat+r_hat)*deform_matrix_brick[2][1] -\
                                               1/8*(1-g_hat)*(1+h_hat)*(1-r_hat)*(2+g_hat-h_hat+r_hat)*deform_matrix_brick[3][1] -\
                                               1/8*(1-g_hat)*(1-h_hat)*(1+r_hat)*(2+g_hat+h_hat-r_hat)*deform_matrix_brick[4][1] -\
                                               1/8*(1+g_hat)*(1-h_hat)*(1+r_hat)*(2-g_hat+h_hat-r_hat)*deform_matrix_brick[5][1] -\
                                               1/8*(1+g_hat)*(1+h_hat)*(1+r_hat)*(2-g_hat-h_hat-r_hat)*deform_matrix_brick[6][1] -\
                                               1/8*(1-g_hat)*(1+h_hat)*(1+r_hat)*(2+g_hat-h_hat-r_hat)*deform_matrix_brick[7][1] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1-h_hat)*(1-r_hat)*deform_matrix_brick[8][1] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1+g_hat)*(1-r_hat)*deform_matrix_brick[9][1] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1+h_hat)*(1-r_hat)*deform_matrix_brick[10][1] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1-g_hat)*(1-r_hat)*deform_matrix_brick[11][1] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1-h_hat)*(1+r_hat)*deform_matrix_brick[12][1] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1+g_hat)*(1+r_hat)*deform_matrix_brick[13][1] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1+h_hat)*(1+r_hat)*deform_matrix_brick[14][1] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1-g_hat)*(1+r_hat)*deform_matrix_brick[15][1] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1-g_hat)*(1-h_hat)*deform_matrix_brick[16][1] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1+g_hat)*(1-h_hat)*deform_matrix_brick[17][1] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1+g_hat)*(1+h_hat)*deform_matrix_brick[18][1] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1-g_hat)*(1+h_hat)*deform_matrix_brick[19][1]

                                    deform_k = 0 - 1/8*(1-g_hat)*(1-h_hat)*(1-r_hat)*(2+g_hat+h_hat+r_hat)*deform_matrix_brick[0][2] -\
                                               1/8*(1+g_hat)*(1-h_hat)*(1-r_hat)*(2-g_hat+h_hat+r_hat)*deform_matrix_brick[1][2] -\
                                               1/8*(1+g_hat)*(1+h_hat)*(1-r_hat)*(2-g_hat-h_hat+r_hat)*deform_matrix_brick[2][2] -\
                                               1/8*(1-g_hat)*(1+h_hat)*(1-r_hat)*(2+g_hat-h_hat+r_hat)*deform_matrix_brick[3][2] -\
                                               1/8*(1-g_hat)*(1-h_hat)*(1+r_hat)*(2+g_hat+h_hat-r_hat)*deform_matrix_brick[4][2] -\
                                               1/8*(1+g_hat)*(1-h_hat)*(1+r_hat)*(2-g_hat+h_hat-r_hat)*deform_matrix_brick[5][2] -\
                                               1/8*(1+g_hat)*(1+h_hat)*(1+r_hat)*(2-g_hat-h_hat-r_hat)*deform_matrix_brick[6][2] -\
                                               1/8*(1-g_hat)*(1+h_hat)*(1+r_hat)*(2+g_hat-h_hat-r_hat)*deform_matrix_brick[7][2] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1-h_hat)*(1-r_hat)*deform_matrix_brick[8][2] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1+g_hat)*(1-r_hat)*deform_matrix_brick[9][2] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1+h_hat)*(1-r_hat)*deform_matrix_brick[10][2] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1-g_hat)*(1-r_hat)*deform_matrix_brick[11][2] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1-h_hat)*(1+r_hat)*deform_matrix_brick[12][2] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1+g_hat)*(1+r_hat)*deform_matrix_brick[13][2] +\
                                               1/4*(1-g_hat)*(1+g_hat)*(1+h_hat)*(1+r_hat)*deform_matrix_brick[14][2] +\
                                               1/4*(1-h_hat)*(1+h_hat)*(1-g_hat)*(1+r_hat)*deform_matrix_brick[15][2] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1-g_hat)*(1-h_hat)*deform_matrix_brick[16][2] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1+g_hat)*(1-h_hat)*deform_matrix_brick[17][2] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1+g_hat)*(1+h_hat)*deform_matrix_brick[18][2] +\
                                               1/4*(1-r_hat)*(1+r_hat)*(1-g_hat)*(1+h_hat)*deform_matrix_brick[19][2]


                                    if micro_part_count == 1:
##                                        print("def_c1 appended")
                                        def_C1.append([node_numb, deform_i, deform_j, deform_k])
                                    if micro_part_count == 2:
##                                        print("def_                         C2 appened")
                                        def_C2.append([node_numb, deform_i, deform_j, deform_k])
                                    if micro_part_count == 3:
##                                        print("appended")
                                        def_CC1.append([node_numb, deform_i, deform_j, deform_k])
                                    if micro_part_count == 4:
##                                        print("APPENED")
                                        def_CC2.append([node_numb, deform_i, deform_j, deform_k])
                                    if micro_part_count == 5:
##                                        print("box append")
                                        def_box.append([node_numb, deform_i, deform_j, deform_k])
                                    


                                    #dump.write(str(node_numb).rjust(15) + "," + str(g_hat).rjust(17) + "," + str(h_hat).rjust(17) + "," + str(r_hat).rjust(17) + "\n")
                                    #dump.write(str(an_elm[0]).rjust(15) + "," + str(an_elm[1]+1000).rjust(17) + "," + str(an_elm[2]+1000).rjust(17) + "," + str(an_elm[3]+1000).rjust(17) + "\n")
                                    #dump.write(str(deform_i).rjust(15+17) + "," + str(deform_j).rjust(17) + "," + str(deform_k).rjust(17) + "\n")

        meso_node_set = []
        polygon_2D = []
        polygon_3D = []
        z_min = 213432
        z_max = 0
        x_min = 123512
        x_max = 0
        y_min = 161237
        y_max = 0
        node_numb = ""
        x_hat = 0
        y_hat = 0
        z_hat = 0
        count = 0
        prev_coma = 0

        deform_matrix_brick = []##will hold all deformations for a brick
        ##initialize
        for number in range(20):
            temp_matrix = []
            for numb in range(3):
                temp_matrix.append(0)

            deform_matrix_brick.append(temp_matrix)

    micro_part_count = 0
    print("done with brix")
    for a_meso_ELEMENT in ALL_wedge_elms:
        micro_part_count = 0
        node_set = a_meso_ELEMENT[1:]
        elm_is_a_wedge = True

##    for member in ALL_wedge_elms:
##        if elm_toquery == member[0]:
##            node_set = member[1:]
##            elm_is_a_wedge = True
##            print("WEDGE HIT!!!")
##            break

        
        if a_meso_ELEMENT[0] % 10000 == 0:
            print(a_meso_ELEMENT[0])


        elm_run = a_meso_ELEMENT[0] in FULL_meso_elset
        
        if elm_run == False:
            pass
        else:

            for elm in node_set:
                for elmnt in ALL_meso_nodes:
                    if elmnt[0] == elm:
                        meso_node_set.append(elmnt)
                        break

            node_set = []
    
            if elm_is_a_wedge:
            ##We need to know the max and min values that x,y,z hold for each element
                for elm in meso_node_set:
                    if elm[3] <= z_min:
                        z_min = elm[3]
                    if elm[3] >= z_max:
                        z_max = elm[3]

                for elm in meso_node_set:
                    if elm[1] <= x_min:
                        x_min = elm[1]
                    if elm[1] >= x_max:
                        x_max = elm[1]

                for elm in meso_node_set:
                    if elm[2] <= y_min:
                        y_min = elm[2]
                    if elm[2] >= y_max:
                        y_max = elm[2]

                for elm in meso_node_set:
                    if z_min == elm[3]:
                        polygon_2D.append((elm[1], elm[2]))
                        polygon_3D.append([elm[0], elm[1], elm[2], elm[3]])

                #print(polygon_3D)
                node_1 = polygon_3D[0]
                node_2 = polygon_3D[1]
                node_3 = polygon_3D[2]
                node_4 = []
                node_5 = []
                node_6 = []

                for elm in meso_node_set:
                    if round(elm[1],1) == round(node_1[1],1) and round(elm[2],1) == round(node_1[2],1) and round(elm[3],1) == round(z_max,1):
                        node_4 = elm
                    if round(elm[1],1) == round(node_2[1],1) and round(elm[2],1) == round(node_2[2],1) and round(elm[3],1) == round(z_max,1):
                        node_5 = elm

                    if round(elm[1],1) == round(node_3[1],1) and round(elm[2],1) == round(node_3[2],1) and round(elm[3],1) == round(z_max,1):
                        node_6 = elm

                #We now define the g,h axis as vectors in the x,y coordinate planes
                #the r axis doesn't need to be defined because it is fairly
                #straight forward

                ##These are written badly. Node1 should be subtracted which is why it's written funny
                g_axis = (0 - node_1[1] + polygon_3D[1][1], 0 - node_1[2] + polygon_3D[1][2])
                h_axis = (0 - node_1[1] + polygon_3D[2][1], 0 - node_1[2] + polygon_3D[2][2])
                r_axis = (z_min, z_max)##NOT IN FROM dx,dy





        ##        dump.write("All Meso nodes of element " + str(elm_toquery) + ":\n")
        ##        for elm in meso_node_set:
        ##            dump.write(str(elm[0]).rjust(15) + "," + str(elm[1]).rjust(17) + "," + str(elm[2]).rjust(17) + "," + str(elm[3]).rjust(17) + "\n")
        ##        dump.write("G_Vector = <" + str(g_axis)[1:-1] + "> in form (dx,dy)\n")
        ##        dump.write("H_Vector = <" + str(h_axis)[1:-1] + "> in form (dx,dy)\n")
        ##        dump.write("R_Vector = <" + str(r_axis)[1:-1] + "> in form (zmin, zmax)\n")
        ##
        ##        dump.write("All Micro nodes contained within the meso element:\n")

            ##WE populate the deformation matrix with the correct deformations
                for i in range(len(nodes_to_deform)):
                    if node_1[0] == nodes_to_deform[i][0]:
                        deform_matrix_wedge[0][0] = deform_matrix_wedge[0][0] + nodes_to_deform[i][1]
                        deform_matrix_wedge[0][1] = deform_matrix_wedge[0][1] + nodes_to_deform[i][2]
                        deform_matrix_wedge[0][2] = deform_matrix_wedge[0][2] + nodes_to_deform[i][3]
                    if node_2[0] == nodes_to_deform[i][0]:
                        deform_matrix_wedge[1][0] = deform_matrix_wedge[1][0] + nodes_to_deform[i][1]
                        deform_matrix_wedge[1][1] = deform_matrix_wedge[1][1] + nodes_to_deform[i][2]
                        deform_matrix_wedge[1][2] = deform_matrix_wedge[1][2] + nodes_to_deform[i][3]
                    if node_3[0] == nodes_to_deform[i][0]:
                        deform_matrix_wedge[2][0] = deform_matrix_wedge[2][0] + nodes_to_deform[i][1]
                        deform_matrix_wedge[2][1] = deform_matrix_wedge[2][1] + nodes_to_deform[i][2]
                        deform_matrix_wedge[2][2] = deform_matrix_wedge[2][2] + nodes_to_deform[i][3]
                    if node_4[0] == nodes_to_deform[i][0]:
                        deform_matrix_wedge[3][0] = deform_matrix_wedge[3][0] + nodes_to_deform[i][1]
                        deform_matrix_wedge[3][1] = deform_matrix_wedge[3][1] + nodes_to_deform[i][2]
                        deform_matrix_wedge[3][2] = deform_matrix_wedge[3][2] + nodes_to_deform[i][3]
                    if node_5[0] == nodes_to_deform[i][0]:
                        deform_matrix_wedge[4][0] = deform_matrix_wedge[4][0] + nodes_to_deform[i][1]
                        deform_matrix_wedge[4][1] = deform_matrix_wedge[4][1] + nodes_to_deform[i][2]
                        deform_matrix_wedge[4][2] = deform_matrix_wedge[4][2] + nodes_to_deform[i][3]
                    if node_6[0] == nodes_to_deform[i][0]:
                        deform_matrix_wedge[5][0] = deform_matrix_wedge[5][0] + nodes_to_deform[i][1]
                        deform_matrix_wedge[5][1] = deform_matrix_wedge[5][1] + nodes_to_deform[i][2]
                        deform_matrix_wedge[5][2] = deform_matrix_wedge[5][2] + nodes_to_deform[i][3]
                #print(deform_matrix_wedge)
            ##deformation matrix now holds [x,y,z] deformations
            ##for every node 1 - 6 where index+1 = node_number



                for an_elm in ALL_micro_nodes[-1]:
                    node_numb = an_elm[0]
                    x_hat = an_elm[1]
                    y_hat = an_elm[2]
                    z_hat = an_elm[3]
                    if (z_hat >= z_min) and (z_hat <= z_max):
                        if (x_hat >= x_min) and (x_hat <= x_max) and (y_hat >= y_min) and (y_hat <= y_max):
                            if point_inside_polygon(x_hat, y_hat, polygon_2D):
                                ##If a micro node is found to be within the meso node,
                                ##We interpolate it:

                                x_hat,y_hat,z_hat = interpolate_6wedge(x_hat, y_hat, z_hat, g_axis, h_axis, r_axis, node_1)

                                ##X_hat, y_hat, z_hat are now in (g,h,r) form.
                                ##We then calculate the deformation. \\ are needed to
                                ##escape the newline character so the equation can span
                                ##more than one line so it looks neat....
                                deform_i = 0.5*(1 - x_hat - y_hat)*(1 - z_hat)*deform_matrix_wedge[0][0] + \
                                    0.5 * x_hat * (1 - z_hat) * deform_matrix_wedge[1][0] + \
                                    0.5 * y_hat * (1 - z_hat) * deform_matrix_wedge[2][0] + \
                                    0.5 * (1 - x_hat - y_hat) * (1 + z_hat) * deform_matrix_wedge[3][0] + \
                                    0.5 * x_hat * (1 + z_hat) * deform_matrix_wedge[4][0] + \
                                    0.5 * y_hat * (1 + z_hat) * deform_matrix_wedge[5][0]

                                deform_j = 0.5*(1 - x_hat - y_hat)*(1 - z_hat)*deform_matrix_wedge[0][1] + \
                                    0.5 * x_hat * (1 - z_hat) * deform_matrix_wedge[1][1] + \
                                    0.5 * y_hat * (1 - z_hat) * deform_matrix_wedge[2][1] + \
                                    0.5 * (1 - x_hat - y_hat) * (1 + z_hat) * deform_matrix_wedge[3][1] + \
                                    0.5 * x_hat * (1 + z_hat) * deform_matrix_wedge[4][1] + \
                                    0.5 * y_hat * (1 + z_hat) * deform_matrix_wedge[5][1]

                                deform_k = 0.5*(1 - x_hat - y_hat)*(1 - z_hat)*deform_matrix_wedge[0][2] + \
                                    0.5 * x_hat * (1 - z_hat) * deform_matrix_wedge[1][2] + \
                                    0.5 * y_hat * (1 - z_hat) * deform_matrix_wedge[2][2] + \
                                    0.5 * (1 - x_hat - y_hat) * (1 + z_hat) * deform_matrix_wedge[3][2] + \
                                    0.5 * x_hat * (1 + z_hat) * deform_matrix_wedge[4][2] + \
                                    0.5 * y_hat * (1 + z_hat) * deform_matrix_wedge[5][2]

                                
                                def_box.append([node_numb, deform_i, deform_j, deform_k])
##
##                                ##Apply the deformation:
##  DEPRECIATED
##                                x_hat = x_hat + deform_i
##                                y_hat = y_hat + deform_j
##                                z_hat = z_hat + deform_k
##
##                                ##Inverse_interpolate them. x_hat,y_hat,z_hat are now in x,y,z form, not g,h,r form
##                                x_hat,y_hat,z_hat = inverse_interpolate_6wedge(x_hat, y_hat, z_hat, g_axis, h_axis, r_axis, node_1)
##                                #dump.write(str(node_numb).rjust(15) + "," + str(x_hat).rjust(17) + "," + str(y_hat).rjust(17) + "," + str(z_hat).rjust(17) + "\n")




    ##reset variables for looping.... don't touch this for now
        elm_is_a_brick = False
        elm_is_a_wedge = False
        meso_node_set = []
        polygon_2D = []
        polygon_3D = []
        z_min = 432432
        z_max = 0
        x_min = 324532
        x_max = 0
        y_min = 234523
        y_max = 0
        node_numb = ""
        x_hat = 0
        y_hat = 0
        z_hat = 0
        count = 0
        prev_coma = 0

        deform_matrix_wedge = []##will hold all deformation
        ##initialize deformation x,y,z
        for number in range(6):
            temp_matrix = []
            for numb in range(3):
                temp_matrix.append(0)

            deform_matrix_wedge.append(temp_matrix)
##
##        deform_matrix_brick = []##will hold all deformations for a brick
##        ##initialize
##        for number in range(20):
##            temp_matrix = []
##            for numb in range(3):
##                temp_matrix.append(0)
##
##            deform_matrix_brick.append(temp_matrix)


    meso.seek(0)
    micro.seek(0)
    meso.close()
    #dump.close()
        
        
    print(len(def_C1))
    print(len(ALL_micro_nodes[0]))
    print(len(def_C2))
    print(len(ALL_micro_nodes[1]))
    print(len(def_CC1))
    print(len(ALL_micro_nodes[2]))
    print(len(def_CC2))
    print(len(ALL_micro_nodes[3]))
    print(len(def_box))
    print(len(ALL_micro_nodes[4]))


    foundit = False
##    global mindx
##    global mindy
##    global mindz
##    mindx = neal_dx
##    mindy = neal_dy
##    mindz = neal_dz

#    thesumx = 0
#    thesumy = 0
#    thesumz = 0

#    for elm in nodes_to_deform:
#        thesumx = elm[1] + thesumx
#        thesumy = elm[2] + thesumy
#        thesumz = elm[3] + thesumz
#
#    mindx = thesumx/len(nodes_to_deform)
#    mindy = thesumy/len(nodes_to_deform)
#    mindz = thesumz/len(nodes_to_deform)


    
    final_def_set.append(def_C1)
    final_def_set.append(def_C2)
    final_def_set.append(def_CC1)
    final_def_set.append(def_CC2)
    final_def_set.append(def_box)

    ##lets reclaim some memory....
    def_C1 = []
    def_C2 = []
    def_CC1 = []
    def_CC2 = []
    def_box = []

    
    dump_bakup = open("DEF_backupCORRECT.txt", 'w')
    for a_lst in final_def_set:
        dump_bakup.write("INSTANCE\n")
        for elm in a_lst:
            dump_bakup.write(str(elm) + "\n")

    dump_bakup.close()




##    print(len(def_C1))
##    print(len(ALL_micro_nodes[0]))
##    print(len(def_C2))
##    print(len(ALL_micro_nodes[1]))
##    print(len(def_CC1))
##    print(len(ALL_micro_nodes[2]))
##    print(len(def_CC2))
##    print(len(ALL_micro_nodes[3]))
##    print(len(def_box))
##    print(len(ALL_micro_nodes[4]))

    ##Reclaim some memory
    del running_node
    del hit_M
    del ALL_micro_nodes
    del nodes_to_deform##HOLDS the nodes to be deformed
    del ALL_meso_nodes
    del ALL_wedge_elms
    del ALL_brick_elms
    del meso_node_set
    del final_def_set
    del FULL_meso_elset
    del micro_part_count
    del def_C1
    del def_C2
    del def_CC1
    del def_CC2
    del def_box
##    del in_hit




    


function_final()



print("DONE with first script!")

##SCRIPT 2
def func():
    source = open("DEF_backupCORRECT.txt")

    global def_setC1
    global def_setC2
    global def_setCC1
    global def_setCC2
    global def_setbox
    global final_defset
    global final_defsetr
    def_setC1 = []
    def_setC2 = []
    def_setCC1 = []
    def_setCC2 = []
    def_setbox = []
    final_defset = []
    final_defsetr = []


    global defr_setC1
    global defr_setC2
    global defr_setCC1
    global defr_setCC2
    global defr_setbox

    defr_setC1 = []
    defr_setC2 = []
    defr_setCC1 = []
    defr_setCC2 = []
    defr_setbox = []

    node_numb = ""
    x_hat = ""
    y_hat = ""
    z_hat = ""
    prev_coma = 0
    count = 0
    instance_count = 0
    for line in source:
        line = line[1:]
        count = 0
        if "NST" in line:
            instance_count = instance_count + 1
            print(instance_count)
        else:
            for ltr in range(len(line)):

                if line[ltr] == "]" and count == 3:
                    z_hat = float(line[prev_coma:-2])
                    count = 0

                if line[ltr] == "," and count == 2:
                    y_hat = float(line[prev_coma:ltr])
                    count = count + 1

                if line[ltr] == "," and count == 1:
                    x_hat = float(line[prev_coma:ltr])
                    count = count + 1

                if line[ltr] == "," and count == 0:
                    node_numb = int(line[0:ltr])
                    count = count + 1


                if line[ltr] == ",":
                    prev_coma = ltr + 1






            if instance_count == 1:
                def_setC1.append([node_numb,x_hat,y_hat,z_hat])

            if instance_count == 2:
                def_setC2.append([node_numb,x_hat,y_hat,z_hat])

            if instance_count == 3:
                def_setCC1.append([node_numb,x_hat,y_hat,z_hat])

            if instance_count == 4:
                def_setCC2.append([node_numb,x_hat,y_hat,z_hat])

            if instance_count == 5:
                def_setbox.append([node_numb,x_hat,y_hat,z_hat])

    final_defset.append(def_setC1)
    final_defset.append(def_setC2)
    final_defset.append(def_setCC1)
    final_defset.append(def_setCC2)
    final_defset.append(def_setbox)

    print("C1")

    for indx in range(len(def_setC1)):
        defr_setC1.append(def_setC1[indx])
        for ind_ex in range(len(def_setC1)):
            if (indx < ind_ex) and def_setC1[indx][0] == def_setC1[ind_ex][0]:
                defr_setC1.remove(def_setC1[indx])
                break
    print("C2")
    for indx in range(len(def_setC2)):
        defr_setC2.append(def_setC2[indx])
        for ind_ex in range(len(def_setC2)):
            if (indx < ind_ex) and def_setC2[indx][0] == def_setC2[ind_ex][0]:
                defr_setC2.remove(def_setC2[indx])
                break
    print("CC1")
    for indx in range(len(def_setCC1)):
        defr_setCC1.append(def_setCC1[indx])
        for ind_ex in range(len(def_setCC1)):
            if (indx < ind_ex) and def_setCC1[indx][0] == def_setCC1[ind_ex][0]:
                defr_setCC1.remove(def_setCC1[indx])
                break
    print("CC2")
    for indx in range(len(def_setCC2)):
        defr_setCC2.append(def_setCC2[indx])
        for ind_ex in range(len(def_setCC2)):
            if (indx < ind_ex) and def_setCC2[indx][0] == def_setCC2[ind_ex][0]:
                defr_setCC2.remove(def_setCC2[indx])
                break
    print("box")
    for indx in range(len(def_setbox)):
        defr_setbox.append(def_setbox[indx])
        for ind_ex in range(len(def_setbox)):
            if (indx < ind_ex) and def_setbox[indx][0] == def_setbox[ind_ex][0]:
                defr_setbox.remove(def_setbox[indx])
                break

    final_defsetr.append(defr_setC1)
    final_defsetr.append(defr_setC2)
    final_defsetr.append(defr_setCC1)
    final_defsetr.append(defr_setCC2)
    final_defsetr.append(defr_setbox)


    r_dump = open("Dump duplicates-removed.txt", 'w')
    print("now writing backup dump with dupes removed...")
    for lst in final_defsetr:
        r_dump.write("INSTANCE!!\n")
        for elm in lst:
            r_dump.write(str(elm) + "\n")


    ##Reclaim memory...
    del defr_setC1
    del defr_setC2
    del defr_setCC1
    del defr_setCC2
    del defr_setbox
    del def_setC1
    del def_setC2
    del def_setCC1
    del def_setCC2
    del def_setbox
    del final_defset
    del final_defsetr



func()

##SCRIPT 3
def dstnc(x1, y1, x2, y2):
    return (sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)))

def Pull_micro_nodes(meso):
    running = False
    partCYL_micro_nodes = []
    partCYLC_micro_nodes = []
    partbox_micro_nodes = []
    n_count = 0
    node_numb = ""
    x_hat = ""
    y_hat = ""
    z_hat = ""
    count = 0
    prev_coma = 0
    for line in meso:
        node_numb = ""
        x_hat = ""
        y_hat = ""
        z_hat = ""
        count = 0
        prev_coma = 0
        if running:
            for letter in range(len(line)):
                if line[0] == "*":
                    break
                if line[letter] == " ":
                    prev_coma = letter

                if count == 3 and running:##ONLY NEED RUNNING IF NOT RUNNING OFF DUMPED FILE
                    z_hat = float(line[(prev_coma + 1):])##:end of line, not letter
                    #print(str(z_hat) + "<---- Z")
                    count +=1

                if line[letter] == "," and count == 2 and running:
                    y_hat = float(line[(prev_coma + 1):letter])
                    #print(str(y_hat) + "<---- Y")
                    count +=1

                if line[letter] == "," and count == 1 and running:
                    x_hat = float(line[(prev_coma + 1):letter])
                    #print(str(x_hat) + "<---- X")
                    count +=1

                if line[letter] == "," and count == 0 and running:
                    node_numb = int(line[0:(letter)])
                    #print(str(node_numb) + " <-- NODE")
                    count += 1
        if node_numb != "" and n_count == 2:
            ##ONLY WILL APPEND MICRO NODES ON THE EDGES OF THE MICRO CUBE
            if ((z_hat + zs) <= 1000.1) or ((z_hat + zs) >= 1497.9) or ((x_hat + xs) <= 879.9) or ((x_hat + xs) >= 1379.7) or ((y_hat + ys) <= 881.6) or ((y_hat + ys) >= 1381):
                partCYL_micro_nodes.append([node_numb, x_hat, y_hat, z_hat])

        if node_numb != "" and n_count == 3:
            ##ONLY WILL APPEND MICRO NODES ON THE EDGES OF THE MICRO CUBE
            if ((z_hat + zs) <= 1000.1) or ((z_hat + zs) >= 1497.9) or ((x_hat + xs) <= 879.9) or ((x_hat + xs) >= 1379.7) or ((y_hat + ys) <= 881.6) or ((y_hat + ys) >= 1381):
                partCYLC_micro_nodes.append([node_numb, x_hat, y_hat, z_hat])

        if node_numb != "" and n_count == 1:
            ##ONLY WILL APPEND MICRO NODES ON THE EDGES OF THE MICRO CUBE
            if ((z_hat + zs) <= 1000.1) or ((z_hat + zs) >= 1497.9) or ((x_hat + xs) <= 879.9) or ((x_hat + xs) >= 1379.7) or ((y_hat + ys) <= 881.6) or ((y_hat + ys) >= 1381):
                partbox_micro_nodes.append([node_numb, x_hat + 1000, y_hat + 1000, z_hat + 1000])
        if "*" in line:
            if "Node" in line:
                running = True
                n_count = n_count + 1
                #print("Node hit")
            else:
                running = False

##We need to generate the instances because there are 2 instances for every part

    part_C1 = []
    part_C2 = []
    part_CC1 = []
    part_CC2 = []

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##CHANGE THIS: This is where the instance information is hardcoded


    for elm in part_C1:
        if elm[3] == -1:
            part_C1.remove(elm)

    for elm in part_C2:
        if elm[3] == -1:
            part_C2.remove(elm)
    for elm in part_CC1:
        if elm[3] == -1:
            part_CC1.remove(elm)
    for elm in part_CC2:
        if elm[3] == -1:
            part_CC2.remove(elm)

    for elm in partCYLC_micro_nodes:
        if elm[3] == -1:
            partCYLC_micro_nodes.remove(elm)

    for elm in partCYL_micro_nodes:
        if elm[3] == -1:
            partCYL_micro_nodes.remove(elm)


    for elmnt in partCYLC_micro_nodes:
        part_C1.append([elmnt[0], (elmnt[1] + 1028.3), (elmnt[2] + 1239.1), (elmnt[3] + 1001)])
        part_C2.append([elmnt[0], (elmnt[1] + 1243.5), (elmnt[2] + 1029.2), (elmnt[3] + 1001)])

    for elmnt in partCYL_micro_nodes:
        part_CC1.append([elmnt[0], (elmnt[1] + 1000), (elmnt[2] + 1000), (elmnt[3] + 1001)])
        part_CC2.append([elmnt[0], (elmnt[1] + 1267.3), (elmnt[2] + 1262), (elmnt[3] + 1001)])

    for elm in part_C1:
        if elm[3] == 999 or elm[3] == 1000 or elm[3] == 1001:
            part_C1.remove(elm)

    for elm in part_C2:
        if elm[3] == 999 or elm[3] == 1000 or elm[3] == 1001:
            part_C2.remove(elm)
    for elm in part_CC1:
        if elm[3] == 999 or elm[3] == 1000 or elm[3] == 1001:
            part_CC1.remove(elm)
    for elm in part_CC2:
        if elm[3] == 999 or elm[3] == 1000 or elm[3] == 1001:
            part_CC2.remove(elm)

    ALL_micro_nodes.append(part_C1)
    ALL_micro_nodes.append(part_C2)
    ALL_micro_nodes.append(part_CC1)
    ALL_micro_nodes.append(part_CC2)
    ALL_micro_nodes.append(partbox_micro_nodes)
    print(len(part_C1))
    print(len(part_C2))
    print(len(part_CC1))
    print(len(part_CC2))
    print(len(partbox_micro_nodes));

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    meso.seek(0)


def func3():
##    source = open("DEF_backupCORRECT.txt")
    global ALL_micro_nodes
    ALL_micro_nodes = []
    all_micro_n = []

##CHANGE THIS: This is the micro file name...
    micro = open("{2}")

    Pull_micro_nodes(micro)

    all_micro_n = ALL_micro_nodes
    global def_setC1
    global def_setC2
    global def_setCC1
    global def_setCC2
    global def_setbox
    global final_defset
    global final_defsetr
    def_setC1 = []
    def_setC2 = []
    def_setCC1 = []
    def_setCC2 = []
    def_setbox = []
    final_defset = []
    final_defsetr = []


    global defr_setC1
    global defr_setC2
    global defr_setCC1
    global defr_setCC2
    global defr_setbox

    defr_setC1 = []
    defr_setC2 = []
    defr_setCC1 = []
    defr_setCC2 = []
    defr_setbox = []
    
    new_pull = open("Dump duplicates-removed.txt")
    temp_set = []
    Ncount = 0

    for line in new_pull:
        if "INSTANCE" in line:
            final_defsetr.append(temp_set)
            temp_set = []

        else:
            temp_set.append(eval(line))




    for elm in final_defsetr:
        if elm == []:
            final_defsetr.remove(elm)




    print("starting to add un-deformed micro nodes")

    elm_dne = open("Elms without deformations.txt", 'w')
    
    exists = False
    dist = 0
    min_dist = 10000
    node_number_min = 0
    deformation_exists = False
###THIS NEEDS TO BE CHANGED!!!!!!
##    for indx in range(len(ALL_micro_nodes)):
##        elm_dne.write("INSTANCE\n")
##        if indx == 4:
##            break
##        for lmnt in ALL_micro_nodes[indx]:
##            exists = False
##            min_dist = 10000
##            dist = 0
##            index_ofmin = 0
##            for elm in final_defsetr[indx]:
##                if lmnt[0] == elm[0]:
##                    exists = True
##
##
##            if exists != True:
##                elm_dne.write(str(lmnt) + "\n")
##                break
##
##                
                
    elm_dne.close()

    ##Reclaim some memory
    del defr_setC1
    del defr_setC2
    del defr_setCC1
    del defr_setCC2
    del defr_setbox
    del def_setC1
    del def_setC2
    del def_setCC1
    del def_setCC2
    del def_setbox
    del final_defset
    del final_defsetr



func3()

##Script 4

def is_not_even(node):
    node_s = str(node)

    if ((int(node_s[-3:]) % 2) != 0):
        if ((int(node_s[-6:-3]) % 2) != 0):
            if ((int(node_s[:-6]) % 2) != 0):
                return True

    return False


def is_not_tied_slave_CC(node):
    node_s = str(node)
    
    if (int(node_s[-3:]) == 333) or (int(node_s[-3:]) == 1):
        if (int(node_s[:-6]) >= 53):
            return False

    return True

def is_not_tied_slave_C(node):
    node_s = str(node)
    
    if (int(node_s[-3:]) == 333) or (int(node_s[-3:]) == 1):
        if (int(node_s[:-6]) == 57):
            return False

    return True


def dstnc(x1, y1, x2, y2):
    return (sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)))

def Function_final():

    new_pull = open("Elms without deformations.txt")
    old_pull = open("Dump duplicates-removed.txt")

    temp_set_C1 = []
    temp_set_C2 = []
    temp_set_CC1 = []
    temp_set_CC2 = []
    temp_set_box = []
    global new_defs

    new_defs = []
    Ncount = 0

##    for line in new_pull:
##        if "INSTANCE" in line:
##            Ncount += 1
##
##        else:
##
##            if Ncount == 1:
##                temp_set_C1.append([(eval(line))[0], 0.0013845279987314998, 0.00137403, 0.001487011967650872])
##
##            if Ncount == 2:
##                temp_set_C2.append([(eval(line))[0], 0.0013845206128822772, 0.0013739920435454584, 0.0014867406129507482])
##
##            if Ncount == 3:
##                temp_set_CC1.append([(eval(line))[0], 0.00138456, 0.00137403, 0.0014870200584354955])
##
##            if Ncount == 4:
##                temp_set_CC2.append([(eval(line))[0], 0.00138448, 0.001374, 0.0014867293063841654])
##
##            if Ncount == 5:
##                
##                break

    Ncount = 0
    c1_minX = 100000000
    c1_maxX = -500000
    c2_minX = 100000000
    c2_maxX = -45943043
    cc1_minX = 1000000000
    cc1_maxX = -2389426323
    cc2_minX = 23984723984629
    cc2_maxX = -293842983623
    c1_minY = 100000000
    c1_maxY = -500000
    c2_minY = 100000000
    c2_maxY = -45943043
    cc1_minY = 1000000000
    cc1_maxY = -2389426323
    cc2_minY = 23984723984629
    cc2_maxY = -293842983623
    c1_minZ = 100000000
    c1_maxZ = -500000
    c2_minZ = 100000000
    c2_maxZ = -45943043
    cc1_minZ = 1000000000
    cc1_maxZ = -2389426323
    cc2_minZ = 23984723984629
    cc2_maxZ = -293842983623
    
    for line in old_pull:
        if "INSTANCE" in line:
            Ncount += 1

        else:

            if Ncount == 1:
                temp_set_C1.append(eval(line))

            if Ncount == 2:
                temp_set_C2.append(eval(line))

            if Ncount == 3:
                temp_set_CC1.append(eval(line))

            if Ncount == 4:
                temp_set_CC2.append(eval(line))

            if Ncount == 5:
                temp_set_box.append(eval(line))

##    new_defs.append(temp_set_C1)
##    new_defs.append(temp_set_C2)
##    new_defs.append(temp_set_CC1)
##    new_defs.append(temp_set_CC2)
##    new_defs.append(temp_set_box)

    for elm in temp_set_C1:
        if elm[1] > c1_maxX:
            c1_maxX = elm[1]
        if elm[2] > c1_maxY:
            c1_maxY = elm[2]
        if elm[3] > c1_maxZ:
            c1_maxZ = elm[3]
        if elm[1] < c1_minX:
            c1_minX = elm[1]
        if elm[2] < c1_minY:
            c1_minY = elm[2]
        if elm[3] < c1_minZ:
            c1_minZ = elm[3]

    for elm in temp_set_C2:
        if elm[1] > c2_maxX:
            c2_maxX = elm[1]
        if elm[2] > c2_maxY:
            c1_maxY = elm[2]
        if elm[3] > c2_maxZ:
            c2_maxZ = elm[3]
        if elm[1] < c2_minX:
            c2_minX = elm[1]
        if elm[2] < c2_minY:
            c2_minY = elm[2]
        if elm[3] < c2_minZ:
            c2_minZ = elm[3]

    for elm in temp_set_CC1:
        if elm[1] > cc1_maxX:
            cc1_maxX = elm[1]
        if elm[2] > cc1_maxY:
            cc1_maxY = elm[2]
        if elm[3] > cc1_maxZ:
            cc1_maxZ = elm[3]
        if elm[1] < cc1_minX:
            cc1_minX = elm[1]
        if elm[2] < cc1_minY:
            cc1_minY = elm[2]
        if elm[3] < cc1_minZ:
            cc1_minZ = elm[3]


    for elm in temp_set_CC2:
        if elm[1] > cc2_maxX:
            cc2_maxX = elm[1]
        if elm[2] > cc2_maxY:
            cc1_maxY = elm[2]
        if elm[3] > cc2_maxZ:
            cc2_maxZ = elm[3]
        if elm[1] < cc2_minX:
            cc2_minX = elm[1]
        if elm[2] < cc2_minY:
            cc2_minY = elm[2]
        if elm[3] < cc2_minZ:
            cc2_minZ = elm[3]

#  Minimum                13.0767         4.00027        -8.99973        -14.9997
#         At Node          132703            7645             503             503
#
#  Maximum                18.1931              6.             -5.            -11.
#         At Node             503          125757          132703          132705
#
#           Total     2.05085E+06     665.719E+03    -933.326E+03    -1.69923E+06



    new_defs.append(temp_set_C1)
    new_defs.append(temp_set_C2)
    new_defs.append(temp_set_CC1)
    new_defs.append(temp_set_CC2)
    new_defs.append(temp_set_box)

##    print("Mindx, Mindy, Mindz")
##    print(mindx, mindy, mindz)




##    for l in new_defs:
##        for item in l:
##            if item[1] > n_maxdx or item[1] < n_mindx:
##                item[1] = neal_dx
##            if item[2] > n_maxdy or item [2] < n_mindy:
##                item[2] = neal_dy
##            if item[3] > n_maxdz or item[3] < n_mindz:
##                item[3] = neal_dz




##CHANGE THIS -- uncomment if you need 10^6
##    for elm in new_defs:
##        for st in elm:
##            st[1] = st[1] * 10**6
##            st[2] = st[2] * 10**6
##            st[3] = st[3] * 10**6

##CHANGE THIS: This is the micro file name, also the dump file name.
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    micro = open("{2}")

    dump = open("{3}", 'w')
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print("ATTEMPTING TO WRITE ABAQUS INPUT FILE!!!")
    nsets_written = False
    bounds_written = False
    running = True
    micro_node_count = 0
    skip = False
    for a_line in micro:
        if skip:
            skip = False
            continue
        micro_node_count = 0


        if (a_line[:7] == "*Static") and bounds_written == False:
            print("writing bounds")
            bounds_written = True
            dump.write(a_line)
            dump.write("** BOUNDARY CONDITIONS\n** LOADS\n")
            dump.write("*BOUNDARY, OP=MOD, TYPE=DISPLACEMENT\n")

            for lmnt in new_defs:
                micro_node_count = micro_node_count + 1
                  
                if micro_node_count == 1:
                    for elmt in lmnt:
                        if is_not_even(elmt[0]) and is_not_tied_slave_C(elmt[0]):
                            dump.write("CEFM1." + str(elmt[0]) + ", 1, 1, " + str(elmt[1]) + "\n")
                            dump.write("CEFM1." + str(elmt[0]) + ", 2, 2, " + str(elmt[2]) + "\n")
                            dump.write("CEFM1." + str(elmt[0]) + ", 3, 3, " + str(elmt[3]) + "\n")
                if micro_node_count == 2:
                    for elmt in lmnt:
                        if is_not_even(elmt[0]) and is_not_tied_slave_C(elmt[0]):
                            dump.write("CEFM2." + str(elmt[0]) + ", 1, 1, " + str(elmt[1]) + "\n")
                            dump.write("CEFM2." + str(elmt[0]) + ", 2, 2, " + str(elmt[2]) + "\n")
                            dump.write("CEFM2." + str(elmt[0]) + ", 3, 3, " + str(elmt[3]) + "\n")
                if micro_node_count == 3:
                    for elmt in lmnt:
                        if is_not_even(elmt[0]) and is_not_tied_slave_CC(elmt[0]):
                            dump.write("CODS1." + str(elmt[0]) + ", 1, 1, " + str(elmt[1]) + "\n")
                            dump.write("CODS1." + str(elmt[0]) + ", 2, 2, " + str(elmt[2]) + "\n")
                            dump.write("CODS1." + str(elmt[0]) + ", 3, 3, " + str(elmt[3]) + "\n")
                if micro_node_count == 4:
                    for elmt in lmnt:
                        if is_not_even(elmt[0]) and is_not_tied_slave_CC(elmt[0]):
                            dump.write("CODS2." + str(elmt[0]) + ", 1, 1, " + str(elmt[1]) + "\n")
                            dump.write("CODS2." + str(elmt[0]) + ", 2, 2, " + str(elmt[2]) + "\n")
                            dump.write("CODS2." + str(elmt[0]) + ", 3, 3, " + str(elmt[3]) + "\n")
                if micro_node_count == 5:
                    for elmt in lmnt:
                        dump.write("boxCnocanL-1." + str(elmt[0]) + ", 1, 1, " + str(elmt[1]) + "\n")
                        dump.write("boxCnocanL-1." + str(elmt[0]) + ", 2, 2, " + str(elmt[2]) + "\n")
                        dump.write("boxCnocanL-1." + str(elmt[0]) + ", 3, 3, " + str(elmt[3]) + "\n")
            continue
        


##CHANGE THIS: currently looks for boundary conditions that won't be there
            ##in new iterations. I'm waiting on the maple file to be
            ##changed before I try to mess with this though. But at the
            ##end of the day it needs changing.
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if not bounds_written:
            dump.write(a_line)
        if bounds_written:
            if a_line[:19] == "**1., 1., 1e-05, 1.":
                skip = True
                continue
            if "BOUNDARY CONDITIONS" in a_line:
                skip = True
                continue
            dump.write(a_line)
##            running = not running

##        if "*Boundary" in a_line:
##            running = not running

##        if "** STEP: Step-1" in a_line:
##            running = not running

##        if "** OUTPUT REQUESTS" in a_line:
##            running = not running
            
##        if running:
##            if "1., 1., 1e-05, 1." in a_line:
##                a_line = "** " + a_line
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                
##            dump.write(a_line)



    dump.close()

    



Function_final()
""".format(Xmeso_filename, Xmeso_deformname, Xmicro_filename, Xmicro_DUMP))

Xdfile.close()

print("qsub {0}".format(Xcmdfilename))

os.system("qsub {0}".format(Xcmdfilename));
