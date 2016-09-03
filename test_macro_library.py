import numpy as np
from macro_library import rotate_displacements_back

def test_rotate_displacements_back():
    U = [[
            [0.000105271, -0.001192500, -0.000542663],
            [0.000134346, -0.001328850, -0.000708393],
        ]]
    expected_rotated_U = [[
            [-0.000333761,    -0.001192500,    -0.000440646],
            [-0.000437744,    -0.001328850,    -0.000572930],
        ]]
    rotated_U = rotate_displacements_back(-48.12, U)

    for each_expected_rotated_U, each_rotated_U in zip(expected_rotated_U[0], rotated_U[0]):
        assert np.allclose(each_expected_rotated_U, each_rotated_U)


if __name__ == "__main__":
    test_rotate_displacements_back()
