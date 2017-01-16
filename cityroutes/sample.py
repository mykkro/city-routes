import cityroutes as cr

pa = cr.Position(10, 10)
pb = cr.Position(180, 180)
gr = cr.Graph()
na = gr.addNode(position=pa)
nb = gr.addNode(position=pb)
e1 = gr.addEdge(start=na, end=nb)

r1 = cr.Road(alongEdge=e1, ways=[
    # forward way
    cr.Way(segments=[
        cr.WaySegment(length=100, lanes=[
            cr.BasicLane(width=3.0, annotations=[

            ]),
            cr.BasicLane(width=3.0, annotations=[

            ])
        ], annotations=[
            cr.ParkingStripForward(length=50, position=20, side=cr.AnnotationSide.Right, boxAngle=90, boxLength=5, boxWidth=3),
            cr.Sign(name="P1", position=10, side=cr.AnnotationSide.Right)
        ]),
        cr.WaySegment(length=20, lanes=[
            cr.SplitLane(number=2),
            cr.BasicLane(width=3.0, annotations=[

            ])
        ], annotations=[
        ]),
        cr.WaySegment(lanes=[
            cr.BasicLane(width=3.0, annotations=[
            ]),
            cr.BasicLane(width=3.0, annotations=[
            ]),
            cr.BasicLane(width=3.0, annotations=[

            ])
        ], annotations=[
            cr.Sign(name="A4", position=30, side=cr.AnnotationSide.Right)
        ])
    ], annotations=[
        cr.Sign(name="B02", position=100, side=cr.AnnotationSide.Right)
    ]),
    cr.Way(reversed=True, segments=[
        cr.WaySegment(length=80, lanes=[
            cr.BasicLane(width=3.0, annotations=[
                # lane annotations go here...
            ]),
            cr.BasicLane(width=3.0, annotations=[
                # lane annotations go here...
            ])
        ], annotations=[
            cr.ParkingStripParallel(width=2.5, length=40, position=30),
            cr.Sign(name="IP06", position=30, side=cr.AnnotationSide.Right),
            cr.Sign(name="A11", position=75, side=cr.AnnotationSide.Right)
        ]),
        cr.WaySegment(length=30, lanes=[
            cr.JoinLane(number=2, annotations=[], side=cr.AnnotationSide.Left)
        ], annotations=[
        ]),
        cr.WaySegment(lanes=[
            cr.BasicLane(width=3.0, annotations=[
                # lane annotations go here...
            ])
        ], annotations=[
            cr.ParkingStripParallel(width=2.5, length=80, position=30)
        ])
    ])
], annotations=[
    cr.Crossing(position=110, width=6.0),
    cr.Crossing(position=230, width=8.0)
])
