import os, sys

from cityroutes import cityroutes as cr

pa = cr.Position(100, 30)
pb = cr.Position(280, 170)

na = cr.Node(position=pa)
nb = cr.Node(position=pb)

e1 = cr.Edge(start=na, end=nb)


r1 = cr.Road(alongEdge=e1, ways=[
    cr.Way(segments=[
        cr.WaySegment(lanes=[
            cr.BasicLane(width=3.0, annotations=[

            ])
        ], annotations=[
            cr.ParkingStripForward(length=50, position=20, side=cr.AnnotationSide.Right, boxAngle=90, boxLength=5, boxWidth=3)
        ])
    ]),
    cr.Way(reversed=True, segments=[
        cr.WaySegment(lanes=[
            cr.BasicLane(width=3.0, annotations=[
                # lane annotations go here...
            ])
        ], annotations=[
            cr.ParkingStripParallel(width=2.5, length=80, position=30)
        ])
    ])
])


print r1, r1.length()

print r1.explain()