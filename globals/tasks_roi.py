from pyqtgraph.Qt import QtCore
from states import DepthLevels

old_task_rect_and_depth = []

old_task_01_rect_and_depth = [[QtCore.QRect(139, 614, 819, 114), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(171, 614, 753, 120), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(204, 637, 679, 98), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(231, 646, 627, 87), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(255, 659, 583, 79), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(275, 664, 542, 71), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(292, 669, 507, 71), DepthLevels.DEPTH_LEVEL_7]]

old_task_02_rect_and_depth = [[QtCore.QRect(63, 452, 161, 123), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(100, 478, 148, 117), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(145, 505, 129, 103), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(174, 524, 120, 93), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(203, 542, 110, 85), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(227, 558, 104, 77), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(249, 570, 92, 74), DepthLevels.DEPTH_LEVEL_7]]

old_task_03_rect_and_depth = [[QtCore.QRect(223, 367, 137, 133), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(252, 398, 123, 125), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(275, 431, 115, 112), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(297, 458, 105, 103), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(311, 479, 102, 96), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(334, 500, 88, 88), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(347, 518, 81, 83), DepthLevels.DEPTH_LEVEL_7]]

old_task_04_rect_and_depth = [[QtCore.QRect(388, 449, 166, 119), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(401, 476, 152, 107), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(415, 502, 136, 99), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(425, 521, 126, 91), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(434, 538, 118, 87), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(444, 553, 107, 82), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(446, 564, 104, 79), DepthLevels.DEPTH_LEVEL_7]]

old_task_05_rect_and_depth = [[QtCore.QRect(564, 342, 128, 167), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(564, 380, 113, 149), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(559, 415, 105, 136), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(558, 442, 97, 127), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(558, 465, 92, 119), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(559, 484, 83, 114), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(558, 500, 78, 106), DepthLevels.DEPTH_LEVEL_7]]

old_task_06_rect_and_depth = [[QtCore.QRect(858, 84, 190, 530), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(831, 140, 171, 486), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(801, 198, 158, 437), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(780, 244, 147, 402), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(767, 283, 132, 370), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(753, 313, 124, 349), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(740, 340, 116, 328), DepthLevels.DEPTH_LEVEL_7]]

old_task_07_rect_and_depth = [[QtCore.QRect(84, 235, 65, 90), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(123, 284, 59, 75), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(159, 326, 54, 72), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(190, 359, 49, 66), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(219, 386, 43, 64), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(241, 414, 43, 58), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(259, 434, 40, 53), DepthLevels.DEPTH_LEVEL_7]]

old_task_08_rect_and_depth = [[QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(300, 0, 124, 445), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(311, 44, 123, 422), DepthLevels.DEPTH_LEVEL_7]]

old_task_09_rect_and_depth = [[QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(367, 0, 518, 395), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(382, 55, 473, 370), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(393, 107, 441, 343), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(406, 153, 411, 320), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(415, 191, 380, 296), DepthLevels.DEPTH_LEVEL_7]]

old_task_10_rect_and_depth = [[QtCore.QRect(25, 7, 124, 163), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(71, 73, 105, 147), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(111, 139, 102, 131), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(145, 185, 92, 123), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(175, 228, 86, 115), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(204, 265, 76, 106), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(222, 294, 75, 101), DepthLevels.DEPTH_LEVEL_7]]

old_task_11_rect_and_depth = [[QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(137, 41, 112, 98), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(169, 92, 100, 93), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(196, 142, 94, 82), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(215, 177, 89, 80), DepthLevels.DEPTH_LEVEL_7]]

old_task_12_rect_and_depth = [[QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(206, 11, 99, 87), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(227, 55, 91, 80), DepthLevels.DEPTH_LEVEL_7]]

old_task_13_rect_and_depth = [[QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(414, 27, 440, 125), DepthLevels.DEPTH_LEVEL_7]]

old_task_14_rect_and_depth = [[QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_1],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_2],
                              [QtCore.QRect(0, 0, 0, 0), DepthLevels.DEPTH_LEVEL_3],
                              [QtCore.QRect(785, 27, 96, 80), DepthLevels.DEPTH_LEVEL_4],
                              [QtCore.QRect(767, 84, 92, 69), DepthLevels.DEPTH_LEVEL_5],
                              [QtCore.QRect(750, 131, 84, 64), DepthLevels.DEPTH_LEVEL_6],
                              [QtCore.QRect(742, 167, 75, 59), DepthLevels.DEPTH_LEVEL_7]]


old_task_rect_and_depth.append(old_task_01_rect_and_depth)
old_task_rect_and_depth.append(old_task_02_rect_and_depth)
old_task_rect_and_depth.append(old_task_03_rect_and_depth)
old_task_rect_and_depth.append(old_task_04_rect_and_depth)
old_task_rect_and_depth.append(old_task_05_rect_and_depth)
old_task_rect_and_depth.append(old_task_06_rect_and_depth)
old_task_rect_and_depth.append(old_task_07_rect_and_depth)
old_task_rect_and_depth.append(old_task_08_rect_and_depth)
old_task_rect_and_depth.append(old_task_09_rect_and_depth)
old_task_rect_and_depth.append(old_task_10_rect_and_depth)
old_task_rect_and_depth.append(old_task_11_rect_and_depth)
old_task_rect_and_depth.append(old_task_12_rect_and_depth)
old_task_rect_and_depth.append(old_task_13_rect_and_depth)
old_task_rect_and_depth.append(old_task_14_rect_and_depth)

# ================================================================================

recorded_1_task_rect_and_depth = []

recorded_1_task_01_rect_and_depth = [[QtCore.QRect(133, 660, 823, 97), DepthLevels.DEPTH_LEVEL_1],
                                      [QtCore.QRect(133, 660, 823, 97), DepthLevels.DEPTH_LEVEL_2],
                                      [QtCore.QRect(133, 660, 823, 97), DepthLevels.DEPTH_LEVEL_3],
                                      [QtCore.QRect(133, 660, 823, 97), DepthLevels.DEPTH_LEVEL_4],
                                      [QtCore.QRect(133, 660, 823, 97), DepthLevels.DEPTH_LEVEL_5],
                                      [QtCore.QRect(133, 660, 823, 97), DepthLevels.DEPTH_LEVEL_6],
                                      [QtCore.QRect(133, 660, 823, 97), DepthLevels.DEPTH_LEVEL_7]]

recorded_1_task_02_rect_and_depth = [[QtCore.QRect(0, 568, 823, 97), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(0, 568, 823, 97), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(0, 568, 823, 97), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(0, 568, 823, 97), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(0, 568, 823, 97), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(0, 568, 823, 97), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(0, 568, 823, 97), DepthLevels.DEPTH_LEVEL_7]]

recorded_1_task_03_rect_and_depth = [[QtCore.QRect(55, 359, 104, 107), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(55, 359, 104, 107), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(55, 359, 104, 107), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(55, 359, 104, 107), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(55, 359, 104, 107), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(55, 359, 104, 107), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(55, 359, 104, 107), DepthLevels.DEPTH_LEVEL_7]]

recorded_1_task_04_rect_and_depth = [[QtCore.QRect(711, 324, 104, 107), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(711, 324, 104, 107), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(711, 324, 104, 107), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(711, 324, 104, 107), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(711, 324, 104, 107), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(711, 324, 104, 107), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(711, 324, 104, 107), DepthLevels.DEPTH_LEVEL_7]]

recorded_1_task_05_rect_and_depth = [[QtCore.QRect(241, 170, 197, 416), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(241, 170, 197, 416), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(241, 170, 197, 416), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(241, 170, 197, 416), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(241, 170, 197, 416), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(241, 170, 197, 416), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(241, 170, 197, 416), DepthLevels.DEPTH_LEVEL_7]]

recorded_1_task_06_rect_and_depth = [[QtCore.QRect(908, 155, 182, 407), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(908, 155, 182, 407), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(908, 155, 182, 407), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(908, 155, 182, 407), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(908, 155, 182, 407), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(908, 155, 182, 407), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(908, 155, 182, 407), DepthLevels.DEPTH_LEVEL_7]]

recorded_1_task_07_rect_and_depth = [[QtCore.QRect(56, 138, 104, 104), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(56, 138, 104, 104), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(56, 138, 104, 104), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(56, 138, 104, 104), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(56, 138, 104, 104), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(56, 138, 104, 104), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(56, 138, 104, 104), DepthLevels.DEPTH_LEVEL_7]]

recorded_1_task_08_rect_and_depth = [[QtCore.QRect(270, 0, 818, 190), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(270, 0, 818, 190), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(270, 0, 818, 190), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(270, 0, 818, 190), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(270, 0, 818, 190), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(270, 0, 818, 190), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(270, 0, 818, 190), DepthLevels.DEPTH_LEVEL_7]]

recorded_1_task_09_rect_and_depth = [[QtCore.QRect(442, 171, 211, 413), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(442, 171, 211, 413), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(442, 171, 211, 413), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(442, 171, 211, 413), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(442, 171, 211, 413), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(442, 171, 211, 413), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(442, 171, 211, 413), DepthLevels.DEPTH_LEVEL_7]]

recorded_1_task_rect_and_depth.append(recorded_1_task_01_rect_and_depth)
recorded_1_task_rect_and_depth.append(recorded_1_task_02_rect_and_depth)
recorded_1_task_rect_and_depth.append(recorded_1_task_03_rect_and_depth)
recorded_1_task_rect_and_depth.append(recorded_1_task_04_rect_and_depth)
recorded_1_task_rect_and_depth.append(recorded_1_task_05_rect_and_depth)
recorded_1_task_rect_and_depth.append(recorded_1_task_06_rect_and_depth)
recorded_1_task_rect_and_depth.append(recorded_1_task_07_rect_and_depth)
recorded_1_task_rect_and_depth.append(recorded_1_task_08_rect_and_depth)
recorded_1_task_rect_and_depth.append(recorded_1_task_09_rect_and_depth)

# ================================================================================

recorded_2_task_rect_and_depth = []

recorded_2_task_01_rect_and_depth = [[QtCore.QRect(131, 568, 819, 189), DepthLevels.DEPTH_LEVEL_1],
                                      [QtCore.QRect(131, 568, 819, 189), DepthLevels.DEPTH_LEVEL_2],
                                      [QtCore.QRect(131, 568, 819, 189), DepthLevels.DEPTH_LEVEL_3],
                                      [QtCore.QRect(131, 568, 819, 189), DepthLevels.DEPTH_LEVEL_4],
                                      [QtCore.QRect(131, 568, 819, 189), DepthLevels.DEPTH_LEVEL_5],
                                      [QtCore.QRect(131, 568, 819, 189), DepthLevels.DEPTH_LEVEL_6],
                                      [QtCore.QRect(131, 568, 819, 189), DepthLevels.DEPTH_LEVEL_7]]

recorded_2_task_02_rect_and_depth = [[QtCore.QRect(61, 430, 107, 107), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(61, 430, 107, 107), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(61, 430, 107, 107), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(61, 430, 107, 107), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(61, 430, 107, 107), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(61, 430, 107, 107), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(61, 430, 107, 107), DepthLevels.DEPTH_LEVEL_7]]

recorded_2_task_03_rect_and_depth = [[QtCore.QRect(244, 170, 195, 416), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(244, 170, 195, 416), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(244, 170, 195, 416), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(244, 170, 195, 416), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(244, 170, 195, 416), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(244, 170, 195, 416), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(244, 170, 195, 416), DepthLevels.DEPTH_LEVEL_7]]

recorded_2_task_04_rect_and_depth = [[QtCore.QRect(719, 432, 106, 104), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(719, 432, 106, 104), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(719, 432, 106, 104), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(719, 432, 106, 104), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(719, 432, 106, 104), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(719, 432, 106, 104), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(719, 432, 106, 104), DepthLevels.DEPTH_LEVEL_7]]

recorded_2_task_05_rect_and_depth = [[QtCore.QRect(901, 158, 189, 414), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(901, 158, 189, 414), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(901, 158, 189, 414), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(901, 158, 189, 414), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(901, 158, 189, 414), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(901, 158, 189, 414), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(901, 158, 189, 414), DepthLevels.DEPTH_LEVEL_7]]

recorded_2_task_06_rect_and_depth = [[QtCore.QRect(717, 231, 106, 104), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(717, 231, 106, 104), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(717, 231, 106, 104), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(717, 231, 106, 104), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(717, 231, 106, 104), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(717, 231, 106, 104), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(717, 231, 106, 104), DepthLevels.DEPTH_LEVEL_7]]

recorded_2_task_07_rect_and_depth = [[QtCore.QRect(449, 171, 189, 416), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(449, 171, 189, 416), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(449, 171, 189, 416), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(449, 171, 189, 416), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(449, 171, 189, 416), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(449, 171, 189, 416), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(449, 171, 189, 416), DepthLevels.DEPTH_LEVEL_7]]

recorded_2_task_08_rect_and_depth = [[QtCore.QRect(64, 43, 104, 104), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(64, 43, 104, 104), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(64, 43, 104, 104), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(64, 43, 104, 104), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(64, 43, 104, 104), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(64, 43, 104, 104), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(64, 43, 104, 104), DepthLevels.DEPTH_LEVEL_7]]

recorded_2_task_09_rect_and_depth = [[QtCore.QRect(275, 0, 816, 190), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(275, 0, 816, 190), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(275, 0, 816, 190), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(275, 0, 816, 190), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(275, 0, 816, 190), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(275, 0, 816, 190), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(275, 0, 816, 190), DepthLevels.DEPTH_LEVEL_7]]

recorded_2_task_rect_and_depth.append(recorded_2_task_01_rect_and_depth)
recorded_2_task_rect_and_depth.append(recorded_2_task_02_rect_and_depth)
recorded_2_task_rect_and_depth.append(recorded_2_task_03_rect_and_depth)
recorded_2_task_rect_and_depth.append(recorded_2_task_04_rect_and_depth)
recorded_2_task_rect_and_depth.append(recorded_2_task_05_rect_and_depth)
recorded_2_task_rect_and_depth.append(recorded_2_task_06_rect_and_depth)
recorded_2_task_rect_and_depth.append(recorded_2_task_07_rect_and_depth)
recorded_2_task_rect_and_depth.append(recorded_2_task_08_rect_and_depth)
recorded_2_task_rect_and_depth.append(recorded_2_task_09_rect_and_depth)

# ================================================================================

training_1_task_rect_and_depth = []

training_1_task_01_rect_and_depth = [[QtCore.QRect(496, 613, 101, 98), DepthLevels.DEPTH_LEVEL_1],
                                      [QtCore.QRect(496, 613, 101, 98), DepthLevels.DEPTH_LEVEL_2],
                                      [QtCore.QRect(496, 613, 101, 98), DepthLevels.DEPTH_LEVEL_3],
                                      [QtCore.QRect(496, 613, 101, 98), DepthLevels.DEPTH_LEVEL_4],
                                      [QtCore.QRect(496, 613, 101, 98), DepthLevels.DEPTH_LEVEL_5],
                                      [QtCore.QRect(496, 613, 101, 98), DepthLevels.DEPTH_LEVEL_6],
                                      [QtCore.QRect(496, 613, 101, 98), DepthLevels.DEPTH_LEVEL_7]]

training_1_task_02_rect_and_depth = [[QtCore.QRect(2, 163, 185, 411), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(2, 163, 185, 411), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(2, 163, 185, 411), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(2, 163, 185, 411), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(2, 163, 185, 411), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(2, 163, 185, 411), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(2, 163, 185, 411), DepthLevels.DEPTH_LEVEL_7]]

training_1_task_03_rect_and_depth = [[QtCore.QRect(346, 281, 397, 195), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(346, 281, 397, 195), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(346, 281, 397, 195), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(346, 281, 397, 195), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(346, 281, 397, 195), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(346, 281, 397, 195), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(346, 281, 397, 195), DepthLevels.DEPTH_LEVEL_7]]

training_1_task_04_rect_and_depth = [[QtCore.QRect(683, 0, 404, 195), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(683, 0, 404, 195), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(683, 0, 404, 195), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(683, 0, 404, 195), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(683, 0, 404, 195), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(683, 0, 404, 195), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(683, 0, 404, 195), DepthLevels.DEPTH_LEVEL_7]]

training_1_task_05_rect_and_depth = [[QtCore.QRect(210, 0, 201, 190), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(210, 0, 201, 190), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(210, 0, 201, 190), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(210, 0, 201, 190), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(210, 0, 201, 190), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(210, 0, 201, 190), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(210, 0, 201, 190), DepthLevels.DEPTH_LEVEL_7]]

training_1_task_rect_and_depth.append(training_1_task_01_rect_and_depth)
training_1_task_rect_and_depth.append(training_1_task_02_rect_and_depth)
training_1_task_rect_and_depth.append(training_1_task_03_rect_and_depth)
training_1_task_rect_and_depth.append(training_1_task_04_rect_and_depth)
training_1_task_rect_and_depth.append(training_1_task_05_rect_and_depth)

# ================================================================================

training_2_task_rect_and_depth = []

training_2_task_01_rect_and_depth = [[QtCore.QRect(1, 380, 189, 188), DepthLevels.DEPTH_LEVEL_1],
                                      [QtCore.QRect(1, 380, 189, 188), DepthLevels.DEPTH_LEVEL_2],
                                      [QtCore.QRect(1, 380, 189, 188), DepthLevels.DEPTH_LEVEL_3],
                                      [QtCore.QRect(1, 380, 189, 188), DepthLevels.DEPTH_LEVEL_4],
                                      [QtCore.QRect(1, 380, 189, 188), DepthLevels.DEPTH_LEVEL_5],
                                      [QtCore.QRect(1, 380, 189, 188), DepthLevels.DEPTH_LEVEL_6],
                                      [QtCore.QRect(1, 380, 189, 188), DepthLevels.DEPTH_LEVEL_7]]

training_2_task_02_rect_and_depth = [[QtCore.QRect(1000, 474, 90, 91), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(1000, 474, 90, 91), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(1000, 474, 90, 91), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(1000, 474, 90, 91), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(1000, 474, 90, 91), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(1000, 474, 90, 91), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(1000, 474, 90, 91), DepthLevels.DEPTH_LEVEL_7]]

training_2_task_03_rect_and_depth = [[QtCore.QRect(451, 286, 189, 192), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(451, 286, 189, 192), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(451, 286, 189, 192), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(451, 286, 189, 192), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(451, 286, 189, 192), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(451, 286, 189, 192), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(451, 286, 189, 192), DepthLevels.DEPTH_LEVEL_7]]

training_2_task_04_rect_and_depth = [[QtCore.QRect(452, 2, 189, 192), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(452, 2, 189, 192), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(452, 2, 189, 192), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(452, 2, 189, 192), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(452, 2, 189, 192), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(452, 2, 189, 192), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(452, 2, 189, 192), DepthLevels.DEPTH_LEVEL_7]]

training_2_task_05_rect_and_depth = [[QtCore.QRect(0, 13, 192, 391), DepthLevels.DEPTH_LEVEL_1],
                                  [QtCore.QRect(0, 13, 192, 391), DepthLevels.DEPTH_LEVEL_2],
                                  [QtCore.QRect(0, 13, 192, 391), DepthLevels.DEPTH_LEVEL_3],
                                  [QtCore.QRect(0, 13, 192, 391), DepthLevels.DEPTH_LEVEL_4],
                                  [QtCore.QRect(0, 13, 192, 391), DepthLevels.DEPTH_LEVEL_5],
                                  [QtCore.QRect(0, 13, 192, 391), DepthLevels.DEPTH_LEVEL_6],
                                  [QtCore.QRect(0, 13, 192, 391), DepthLevels.DEPTH_LEVEL_7]]

training_2_task_rect_and_depth.append(training_2_task_01_rect_and_depth)
training_2_task_rect_and_depth.append(training_2_task_02_rect_and_depth)
training_2_task_rect_and_depth.append(training_2_task_03_rect_and_depth)
training_2_task_rect_and_depth.append(training_2_task_04_rect_and_depth)
training_2_task_rect_and_depth.append(training_2_task_05_rect_and_depth)
