# This file optimizes the chair after a bunch of manipulation that resembled the chair

import numpy as np
import mixer.util as util
from parser.parser import SimpleObj
from mixer.change_leg import find_pieces

# optimize leg
def optimize_leg( component ):
    print( 'optimizing legs...' )
    legs = component['result_obj']['legs']

    # get other parts except for legs, and merge them for the convenience of optimizing legs
    others = []
    others.append( component['result_obj']['seat'] )
    others.append( component['result_obj']['back'] )
    for a in component['result_obj']['arm_rests']:
        others.append( a )
    others = SimpleObj.merge_objs( others )
    others_verts = util.get_verts( others )
    others_size = util.get_size( others_verts )

    # temporary get the whole leg to do a global optimization
    whole_leg = SimpleObj.merge_objs( legs )
    whole_leg_verts = util.get_verts( whole_leg )
    whole_leg_top = util.get_top_verts( whole_leg_verts )
    whole_leg_top_size = util.get_size( whole_leg_top )


#---------- scale whole leg by x and z ----------#


    # if leg top is wider than other parts in x axis
    if( whole_leg_top_size[0] > others_size[0] ):
        print( 'optimizing the width of leg...' )
        ratio = others_size[0] / whole_leg_top_size[0]
        for l in legs:
            for v in l.verts:
                v[0] *= ratio 

    # if leg top is wider than other parts in z axis
    if( whole_leg_top_size[2] > others_size[2] ):
        print( 'optimizing the depth of leg...' )
        ratio = others_size[2] / whole_leg_top_size[2]
        for l in legs:
            for v in l.verts:
                v[2] *= ratio 


#---------- transform leg pieces by y ----------#


    # if the leg is one piece, try to split it into pieces
    if( len( legs ) == 1 ):
        legs = find_pieces( legs[0], component['center']['legs'][0] )

    # get the top vertices of the legs
    legs_top = [ util.get_top_verts( util.get_verts( l ) ) for l in legs ]
    
    # if the leg is still one piece, then attach the leg to the bottom of the seat
    if( len( legs ) == 1 ):
        # get seat min and leg max, and calculate the distance between them in y axis
        seat_min = np.amin( util.get_verts( component['result_obj']['seat'] ), axis = 0 )
        leg_top_max = np.amax( legs_top[0], axis = 0 )
        dist = seat_min[1] - leg_top_max[1]

        # translate the leg in y axis
        for v in legs[0].verts:
            v[1] += dist
    
    # else there are more than one leg piece, then attach each leg piece to the bottom of the seat
    else:
        for leg, leg_top in zip( legs, legs_top ):
            #get leg top min and max
            leg_top_min = np.amin( leg_top, axis = 0 )
            leg_top_max = np.amax( leg_top, axis = 0 )

            # construct range to retrieved vertices from other parts and get the min
            range_min = np.copy( leg_top_min )
            range_max = np.copy( leg_top_max )
            range_min[1] = np.NINF
            range_max[1] = np.inf
            others_relative_verts = util.get_range_verts( others_verts, range_min, range_max )
            others_relative_min = np.amin( others_relative_verts, axis = 0 )

            # calculate the distance between the leg top and whatever that's directly above it (y axis)
            dist = others_relative_min[1] - leg_top_max[1]

            # calculate the scaling ratio in y axis
            leg_size = util.get_size( util.get_verts( leg ) )
            ratio = ( leg_size[1] + dist ) / leg_size[1]

            # calculate the translation offset in y axis
            offset = leg_top_max[1] - leg_top_max[1] * ratio + dist

            # translate the leg in y axis
            for v in leg.verts:
                v[1] = v[1] * ratio + offset 
    
    component['result_obj']['legs'] = legs
    return



# optimize the chair
def optimize( component ):
    optimize_leg( component )
    return component
