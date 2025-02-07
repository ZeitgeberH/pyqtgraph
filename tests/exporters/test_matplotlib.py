from importlib.metadata import version

import pytest

import pyqtgraph as pg
from pyqtgraph.exporters import MatplotlibExporter

pytest.importorskip("matplotlib")
import matplotlib

app = pg.mkQApp()

skip_qt6 = pytest.mark.skipif(
    # availability of QtAgg signifies Qt6 support
    pg.Qt.QT_LIB in ["PySide6", "PyQt6"] and "QtAgg" not in matplotlib.rcsetup.interactive_bk,
    reason= (
        "installed version of Matplotlib does not support Qt6, "
        "see https://github.com/matplotlib/matplotlib/pull/19255"
    )
)

# see https://github.com/matplotlib/matplotlib/pull/24172
if (
    pg.Qt.QT_LIB == "PySide6"
    and tuple(map(int, pg.Qt.PySide6.__version__.split("."))) > (6, 4)
    and tuple(map(int, version("matplotlib").split("."))) < (3, 6, 2)
):
    pytest.skip(
        "matplotlib + PySide6 6.4 bug",
        allow_module_level=True
    )


@skip_qt6
def test_MatplotlibExporter():
    plt = pg.plot()

    # curve item
    plt.plot([0, 1, 2], [0, 1, 2])
    # scatter item
    plt.plot([0, 1, 2], [1, 2, 3], pen=None, symbolBrush='r')
    # curve + scatter
    plt.plot([0, 1, 2], [2, 3, 4], pen='k', symbolBrush='r')

    exp = MatplotlibExporter(plt.getPlotItem())
    exp.export()

@skip_qt6
def test_MatplotlibExporter_nonplotitem():
    # attempting to export something other than a PlotItem raises an exception
    plt = pg.plot()
    plt.plot([0, 1, 2], [2, 3, 4])
    exp = MatplotlibExporter(plt.getPlotItem().getViewBox())
    with pytest.raises(Exception):
        exp.export()

@skip_qt6
@pytest.mark.parametrize('scale', [1e10, 1e-9])
def test_MatplotlibExporter_siscale(scale):
    # coarse test to verify that plot data is scaled before export when
    # autoSIPrefix is in effect (so mpl doesn't add its own multiplier label)
    plt = pg.plot([0, 1, 2], [(i+1)*scale for i in range(3)])
    # set the label so autoSIPrefix works
    plt.setLabel('left', 'magnitude')
    exp = MatplotlibExporter(plt.getPlotItem())
    exp.export()

    mpw = MatplotlibExporter.windows[-1]
    fig = mpw.getFigure()
    ymin, ymax = fig.axes[0].get_ylim()

    if scale < 1:
        assert ymax > scale
    else:
        assert ymax < scale
