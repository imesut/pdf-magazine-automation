import unittest, operator

def clean_single_footer_items(footer_items, unique_items):
    for item in footer_items:
        if item in unique_items:
            unique_items.remove(item)
            footer_items.remove(item)
            clean_single_footer_items(footer_items, unique_items)

# Receives an array from tuples like [(yL, yH, 'text'), (yL, yH, 'text') ...]
def get_repeating_footer_items(footer_items):
    print(footer_items)
    uniques_a = list(set(footer_items))
    clean_single_footer_items(footer_items, uniques_a)
    footer_items = list(set(footer_items))
    return footer_items


# TESTS
sample_data_from_lezzet = [(686, 727, 'N e v'), (702, 722, 'çorbasını yapın'), (738, 745, 'facebook.com/le'), (738, 745, 'lezzet_dergisi'), (739, 745, 'www.lezzet.com.'), (738, 745, '@Lezzet_Dergisi'), (772, 780, 'NİSAN | MAYIS  '), (739, 758, 'www.dbabone.com'), (701, 731, 'güçlendirsin...'), (719, 741, '  RAMAZAN ÖZEL '), (735, 745, 'SAĞLIKLI SAHUR'), (772, 780, '  LEZZET • NİSA'), (697, 745, 'VEGAN TARİFLERA'), (730, 752, '  ASTROLOJİ'), (690, 701, 'Haydi mutfağa!'), (772, 780, '  LEZZET • NİSA'), (686, 695, '•   çay bardağı'), (696, 705, 'zeytinyağı'), (706, 725, '•   su bardağı '), (726, 735, 'nane'), (736, 745, '•  Tuz'), (772, 780, ' NİSAN | MAYIS '), (690, 699, '•   Hepsini haz'), (700, 729, 'anda limonla ov'), (696, 705, 'soğan'), (706, 725, '•   adet limon '), (726, 735, 'kadar tuz'), (772, 780, '  LEZZET • NİSA'), (772, 780, ' NİSAN | MAYIS '), (697, 724, 'DENİZ ORHUNZIRA'), (728, 747, '@denizorhunklem'), (768, 776, '  LEZZET • NİSA'), (689, 749, 'Eskiden bir sav'), (772, 780, 'NİSAN | MAYIS  '), (768, 776, ' LEZZET • NİSAN'), (772, 780, 'NİSAN | MAYIS  '), (768, 776, ' LEZZET • NİSAN'), (772, 780, '  LEZZET • NİSA'), (685, 694, 'şekeri'), (695, 724, '•   g süt•   ta'), (725, 744, '(Beyazları ve s'), (745, 754, '•   g bitter çi'), (685, 754, ' Yağ ve unu bir'), (772, 780, ' NİSAN | MAYIS '), (726, 735, ' paket toz vani'), (736, 745, '•  - adet orta '), (772, 780, '  LEZZET • NİSA'), (731, 740, ' paket toz vani'), (772, 780, ' NİSAN | MAYIS '), (715, 724, ' paket toz vani'), (725, 744, '•   g çilek (Ay'), (772, 780, '  LEZZET • NİSA'), (684, 693, '(Yıkanmış, ayık'), (694, 703, '•   çay bardağı'), (704, 713, 'fındık '), (724, 753, 'SOS IÇIN•   yem'), (772, 780, ' NİSAN | MAYIS '), (772, 780, '  LEZZET • NİSA'), (772, 780, ' NİSAN  | MAYIS')]
expected_output_of_lezzet = [(772, 780, ' NİSAN | MAYIS '), (772, 780, '  LEZZET • NİSA'), (768, 776, ' LEZZET • NİSAN'), (772, 780, 'NİSAN | MAYIS  ')]

class TestSeperator(unittest.TestCase):
    def test_footer_items(self):
        self.assertListEqual(sorted(get_repeating_footer_items(sample_data_from_lezzet)), sorted(expected_output_of_lezzet))

if __name__ == '__main__':
    unittest.main()
