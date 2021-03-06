import shapefile
import pngcanvas

# Open shapefile with Python Shapefile Library
filename='Vindhya algo testDXF_segmentedCenterLines.shp'

def Conversion(filename):
    shapefile_name =filename # e.g. england_oa_2001
    r = shapefile.Reader(shapefile_name)

    # Determine bounding box x and y distances and then calculate an xyratio
    # that can be used to determine the size of the generated PNG file. A xyratio
    # of greater than one means that PNG is to be a landscape type image whereas
    # an xyratio of less than one means the PNG is to be a portrait type image.
    xdist = r.bbox[2] - r.bbox[0]
    ydist = r.bbox[3] - r.bbox[1]
    xyratio = xdist/ydist
    image_max_dimension = 600 # Change this to desired max dimension of generated PNG
    if (xyratio >= 1):
        iwidth  = image_max_dimension
        iheight = int(image_max_dimension/xyratio)
    else:
        iwidth  = int(image_max_dimension/xyratio)
        iheight = image_max_dimension

    # Iterate through all the shapes within the shapefile and draw polyline
    # representations of them onto the PNGCanvas before saving the resultant canvas
    # as a PNG file
    xratio = iwidth/xdist
    yratio = iheight/ydist
    pixels = []
    c = pngcanvas.PNGCanvas(iwidth,iheight)
    for shape in r.shapes():
        for x,y in shape.points:
            px = int(iwidth - ((r.bbox[2] - x) * xratio))
            py = int((r.bbox[3] - y) * yratio)
            pixels.append([px,py])
        c.polyline(pixels)
        pixels = []
    f = file("%s.png" % shapefile_name,"wb")
    f.write(c.dump())
    f.close()

    # Create a world file
    wld = file("%s.pgw" % shapefile_name, "w")
    wld.write("%s\n" % (xdist/iwidth))
    wld.write("0.0\n")
    wld.write("0.0\n")
    wld.write("-%s\n" % (ydist/iheight))
    wld.write("%s\n" % r.bbox[0])
    wld.write("%s\n" % r.bbox[3])
    wld.close

Conversion(filename)
