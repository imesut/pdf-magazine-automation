import unittest

def get_yAxis_unified_range(datas):
    yAxis = [[0,0]]
    axis_count = 1
    for data in datas:
        # y saved lower - y saved higher
        ySl = data[0]
        ySh = data[1]
        trial_count = 1
        for pair in yAxis:
            # y current lower - y current higher
            yCl = pair[0]
            yCh = pair[1]
            if (( ySl <= yCl <= ySh ) or ( ySl <= yCh <= ySh )):
                pair[0] = min(yCl, ySl)
                pair[1] = max(yCh, ySh)
                break
            elif (trial_count == axis_count):
                yAxis.append([ ySl, ySh ])
                axis_count += 1
                break
            else:
                trial_count += 1
    yAxis.remove([0,0])
    return yAxis

def get_seperetor_line(datas):
    yAxis = get_yAxis_unified_range(datas)
    prev_item_higher = yAxis[0][1]
    line_val = 0
    space = 0
    for axis in yAxis[1:]:
        new_space = axis[0] - prev_item_higher
        if (new_space > space):
            space = new_space
            line_val = prev_item_higher + space / 2
        prev_item_higher = axis[1]
    return line_val

# get_seperetor_line(datas)

sampleData = [[100, 120], [120, 150], [50, 130], [250, 300], [290, 350]]
sampleData2 = [[100, 120], [120, 150], [50, 130], [250, 300], [290, 350], [500, 600]]

class TestSeperator(unittest.TestCase):
    def test_yAxis_vals(self):
        self.assertEqual(get_yAxis_unified_range(sampleData), [[50,150], [250,350]])
    
    def test_seperator_line(self):
        self.assertEqual(get_seperetor_line(sampleData), 200)
        self.assertEqual(get_seperetor_line(sampleData2), 425)

if __name__ == '__main__':
    unittest.main()
