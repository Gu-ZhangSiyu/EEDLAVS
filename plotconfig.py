import matplotlib as mpl
from matplotlib.ticker import FormatStrFormatter,  ScalarFormatter
import matplotlib.axes as _axes
from mpl_toolkits.mplot3d import Axes3D

"""
#--------------------------------------------- 
# Axes patch (global)
_FOUR_DP = FormatStrFormatter('%.4f')       # Create a formatter that keeps four decimal places.
_orig_axes_init = _axes.Axes.__init__       # Save the original __init__.

def _patched_axes_init(self, *args, **kwargs):
    _orig_axes_init(self, *args, **kwargs)
    self.xaxis.set_major_formatter(_FOUR_DP)
    self.yaxis.set_major_formatter(_FOUR_DP)
_axes.Axes.__init__ = _patched_axes_init
"""

#---------------------------------------------
# Axes patch (namespace), redefined using monkey patching.
# Add `from plotconfig import enable_patch, disable_patch` before functions that need it.
# Wrap the relevant helper calls with enable_patch() and disable_patch().
# -- Global switches and formatters
_PATCH_4DP = False
_PATCH_2DP = False
_FOUR_DP = FormatStrFormatter('%.4f')   # Formatter that keeps four decimal places.
_TWO_DP = FormatStrFormatter('%.2f')    # Formatter that keeps two decimal places.
_orig_init = _axes.Axes.__init__        # Save the original __init__.

def _patched_init(self, *args, **kwargs):       # Patch controlled by switches.
    _orig_init(self, *args, **kwargs)
    if _PATCH_4DP:
        self.xaxis.set_major_formatter(_FOUR_DP)
        self.yaxis.set_major_formatter(_FOUR_DP)
        if isinstance(self, Axes3D):
            self.zaxis.set_major_formatter(_FOUR_DP)    # Also handle Axes3D instances.
    elif _PATCH_2DP:
        self.xaxis.set_major_formatter(_TWO_DP)
        self.yaxis.set_major_formatter(_TWO_DP)
        if isinstance(self, Axes3D):
            self.zaxis.set_major_formatter(_TWO_DP)

_axes.Axes.__init__ = _patched_init

# Four-decimal-place interface.
def enable_patch_4dp():
    global _PATCH_4DP, _PATCH_2DP
    _PATCH_4DP = True
    _PATCH_2DP = False

def disable_patch_4dp():
    global _PATCH_4DP
    _PATCH_4DP = False

# Two-decimal-place interface.
def enable_patch_2dp():
    global _PATCH_4DP, _PATCH_2DP
    _PATCH_4DP = False
    _PATCH_2DP = True

def disable_patch_2dp():
    global _PATCH_2DP
    _PATCH_2DP = False

#--------------------------------------------- (Not effective; the reason is unknown.)
# Colorbar patch.
_five_sig = FormatStrFormatter('%.5g')
_sci_sf = ScalarFormatter(useMathText=True)
_sci_sf.set_scientific(True)
_sci_sf.set_powerlimits((-4, 4))    # Use scientific notation below 10^(-4) or above 10^4.

#---------------------------------------------
# Global font-size patch.
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Times New Roman']
mpl.rcParams['mathtext.fontset'] = 'custom'         # The custom/stix gradient requires stix.
mpl.rcParams['mathtext.rm'] = 'Times New Roman'
mpl.rcParams['mathtext.it'] = 'Times New Roman:italic'
mpl.rcParams['mathtext.bf'] = 'Times New Roman:bold'
mpl.rcParams['mathtext.default'] = 'it'
mpl.rcParams['mathtext.fallback'] = 'none'

class PlotConfig:
    @staticmethod
    def apply():
        # Font sizes for different plot elements.
        mpl.rcParams['axes.titlesize'] = 28  # Title.
        mpl.rcParams['axes.labelsize'] = 26  # Axis labels.
        mpl.rcParams['xtick.labelsize'] = 24  # X-axis tick labels.
        mpl.rcParams['ytick.labelsize'] = 24  # Y-axis tick labels.
        mpl.rcParams['legend.fontsize'] = 18  # Legend text.
        mpl.rcParams['figure.titlesize'] = 24  # Overall figure title.
