import unittest

import support
from rf433.errors import Rf433Error
from rf433.receive.ook import parse_ook
from rf433.signal.cluster import clean_code, clean_codes, cluster_values
from rf433.signal.frames import extract_frame, split_frames


class ClusterTest(unittest.TestCase):
    def test_groups_map_to_most_frequent_value(self):
        mapping = cluster_values([300, 300, 310, 290, 900, 880, 900, 9300], 0.25)
        self.assertEqual(mapping, {290: 300, 300: 300, 310: 300, 880: 900, 900: 900, 9300: 9300})

    def test_group_is_a_chain_of_neighbours(self):
        # each value is within 25 % of the previous one, so all form one group
        self.assertEqual(set(cluster_values([100, 120, 145, 175, 175], 0.25).values()), {175})
        self.assertEqual(len(set(cluster_values([100, 126], 0.25).values())), 2)

    def test_clean_restores_jittered_frame(self):
        ideal = support.frame("0110100101")
        self.assertEqual(clean_code(support.jitter(ideal), 0.25), ideal)

    def test_pulses_and_pauses_are_grouped_separately(self):
        # a pulse of 400 must not be merged with pauses of 350
        self.assertEqual(clean_code([400, 350, 400, 350, 410, 9000], 0.25), [400, 350, 400, 350, 400, 9000])

    def test_clean_codes_share_the_groups(self):
        first, second = clean_codes([[300, 900, 300, 9300], [310, 880, 310, 9300]], 0.25)
        self.assertEqual(first, second)


class FramesTest(unittest.TestCase):
    def test_split_frames(self):
        self.assertEqual(split_frames([300, 900, 300, 9300, 300, 900, 300], 5000),
                         [([300, 900, 300, 9300], True), ([300, 900], False)])

    def test_extract_frame_from_repeats(self):
        ideal = support.frame("0110")
        # noise in front, five repeats with jitter, the last pause is cut by the end of the recording
        package = [150, 6000]
        for index in range(5):
            package += support.jitter(ideal[:-1] + [ideal[-1] + index * 10])
        package[-1] = 20000
        result = extract_frame([package], 5000, last_pause_reliable=False)
        self.assertEqual((result.frames, result.matches), (6, 5))
        self.assertEqual(len(result.values), len(ideal))
        # pauses 9300, 9310, 9320, 9330 are reliable, the median is taken
        self.assertEqual(result.values[-1], 9320)
        self.assertEqual(clean_code(result.values, 0.25), ideal[:-1] + [9320])

    def test_last_pause_counts_if_reliable(self):
        package = [300, 900, 300, 9000, 300, 900, 300, 20000]
        self.assertEqual(extract_frame([package], 5000, False).values[-1], 9000)
        self.assertEqual(extract_frame([package], 5000, True).values[-1], 20000)

    def test_frames_of_several_packages(self):
        ideal = support.frame("01")
        result = extract_frame([ideal + ideal, ideal], 5000, False)
        self.assertEqual((result.frames, result.matches, result.values), (3, 3, ideal))

    def test_no_frames(self):
        with self.assertRaises(Rf433Error):
            extract_frame([], 5000, False)


class OokTest(unittest.TestCase):
    def test_parse(self):
        text = "\n".join([
            ";pulse data",
            ";version 1",
            ";timescale 1us",
            ";ook 2 pulses",
            ";freq1 433920000",
            "300 900",
            "300 9300",
            ";end",
            ";fsk 1 pulses",
            "120 5000",
            ";end",
            ";ook 0 pulses",
            ";end",
            "999 999",
        ])
        self.assertEqual(parse_ook(text), [[300, 900, 300, 9300], [120, 5000]])


if __name__ == "__main__":
    unittest.main()
