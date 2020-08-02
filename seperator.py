import unittest

def get_yAxis_unified_range(datas):
    yAxis = [[0,0]]
    for data in datas:
        # y saved lower - y saved higher
        ySl = data[0]
        ySh = data[1]
        trial_count = 1
        for pair in yAxis:
            # y current lower - y current higher
            yCl, yCh = pair[0], pair[1]
            if (( ySl <= yCl <= ySh ) or ( ySl <= yCh <= ySh )):
                pair[0] = min(yCl, ySl)
                pair[1] = max(yCh, ySh)
                items_to_del = list(filter(lambda x: pair[0] <= x[0] and pair[1] >= x[1], yAxis))
                items_to_del.remove(pair)
                for item in items_to_del:
                    yAxis.remove(item)
                break
            elif (trial_count == len(yAxis)):
                yAxis.append([ ySl, ySh ])
                break
            elif pair == [0, 0]:
                pass
            trial_count += 1
    yAxis.remove([0,0])
    return yAxis

def get_seperator_line(datas):
    yAxis = get_yAxis_unified_range(datas)
    yAxis = eliminate_small_areas(yAxis)
    if len(yAxis) > 1:
        prev_item_higher = yAxis[0][1]
        line_val = 0
        space = 0
        for axis in yAxis[1:]:
            new_space = axis[0] - prev_item_higher
            if (new_space > space):
                space = new_space
                line_val = prev_item_higher + space / 2
            prev_item_higher = axis[1]
        return line_val, space
    return 0, 0

def eliminate_small_areas(axis_array):
    return list(filter(lambda x: x[1] - x[0] > 20, axis_array))


# TESTS
sampleData = [[100, 120], [120, 150], [50, 130], [250, 300], [290, 350]]
sampleData2 = [[100, 120], [120, 150], [50, 130], [250, 300], [290, 350], [500, 600]]
sampleData3 = [[113, 122], [247, 390], [393, 405], [408, 608], [731, 859], [248, 608], [731, 859], [509, 521], [524, 535], [538, 608], [731, 859], [248, 318], [321, 361], [364, 608]]

class TestSeperator(unittest.TestCase):
    def test_yAxis_vals(self):
        self.assertEqual(get_yAxis_unified_range(sampleData), [[50,150], [250,350]])
        self.assertEqual(get_yAxis_unified_range(sampleData3), [[113, 122], [247, 608], [731, 859]])
    
    def test_seperator_line(self):
        self.assertEqual(get_seperator_line(sampleData), (200, 100))
        self.assertEqual(get_seperator_line(sampleData2), (425, 150))
        self.assertEqual(get_seperator_line(sampleData3), (669.5, 123))
    
    def test_small_area(self):
        self.assertEqual(eliminate_small_areas(sampleData), [[120, 150], [50, 130], [250, 300], [290, 350]])

if __name__ == '__main__':
    unittest.main()
