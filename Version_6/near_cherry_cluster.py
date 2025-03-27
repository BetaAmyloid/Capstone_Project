import numpy as np

class near_cherry_cluster:
    def __init__(self):
        print("Near Cherry Cluster")

    def point_getter(self, bounding_box):
        ymin = int(max(1, (bounding_box[0] * 720)))
        xmin = int(max(1, (bounding_box[1] * 1280)))
        ymax = int(min(720, (bounding_box[2] * 720)))
        xmax = int(min(1280, (bounding_box[3] * 1280)))
        
        return ymin, xmin, ymax, xmax

    def calculate_distance(self, bounding_box):
        ymin, xmin, ymax, xmax = self.point_getter(bounding_box)

        mid_x = int((xmin + xmax)/2)
        mid_y = int((ymin + ymax)/2)

        distance = np.sqrt((mid_x - 640)**2 + (mid_y - 360)**2)

        return distance, mid_x, mid_y

    def find(self, bounding_box_list, classes_list, score_list):
        '''
        Takes a list of detected objects and
        '''
        most_near = []
        least_distace = 2000.0
        most_mid_x = None
        most_mid_y = None

        for i in range(len(score_list)):
            distance, mid_x, mid_y = self.calculate_distance( bounding_box_list[i])

            # Conditional statement for RIPE ONLY
            # if(score_list[i] > 0.5 and distance < least_distace and classes_list[i] == 1):
            #     # most_near = bounding_box_list[i]
            #     most_mid_x = mid_x
            #     most_mid_y = mid_y

            # Conditional statement for ANYTHING DETECTED
            if(score_list[i] > 0.5 and distance < least_distace):
                # most_near = bounding_box_list[i]
                most_mid_x = mid_x
                most_mid_y = mid_y

        return most_mid_x, most_mid_y
                