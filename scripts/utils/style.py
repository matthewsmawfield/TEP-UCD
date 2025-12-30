import matplotlib.pyplot as plt

COLORS = {
    'primary': '#2D0140',
    'primary_light': '#6B2D73',
    'secondary': '#495773',
    'accent': '#4A90C2',
    'highlight': '#F39C12',
    'hover': '#A64D79',
    'text': '#220126',
    'background': '#F8F8FF',
    'grid': '#CCCCCC',
    'black': '#111111',
    'gray': '#666666',
    'teal': '#009E73',
    'vermillion': '#D55E00',
    'sky': '#56B4E9',
    'magenta': '#CC79A7',
}

FIG_SIZE = {
    'single_column': (3.5, 2.6),
    'double_column': (7.2, 4.5),
    'full_width': (10.0, 6.0),
    'web_standard': (7.5, 4.6),
    'web_tall': (7.5, 5.4),
    'web_two_panel': (7.5, 4.0),
    'web_quad': (7.5, 5.6),
    'web_dense': (7.5, 6.6),
    'web_grid_3x3': (7.5, 7.2),
    'web_six_panel': (7.5, 5.8),
}

WEB_TARGET_WIDTH_IN = FIG_SIZE['web_standard'][0]
FIG_SCALE = {
    'single_column': 1.0,
    'double_column': 1.0,
    'full_width': 1.0,
    'web_standard': 1.0,
    'web_tall': 1.0,
    'web_two_panel': 1.0,
    'web_quad': 1.0,
    'web_dense': 1.0,
    'web_grid_3x3': 1.0,
    'web_six_panel': 1.0,
}


def set_pub_style(scale=1.0, dpi=600, transparent=True):
    base_font = 9
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
        'mathtext.fontset': 'stix',
        'font.size': base_font * scale,
        'axes.labelsize': base_font * scale,
        'axes.titlesize': (base_font + 1) * scale,
        'xtick.labelsize': (base_font - 1) * scale,
        'ytick.labelsize': (base_font - 1) * scale,
        'legend.fontsize': (base_font - 2) * scale,
        'figure.titlesize': (base_font + 2) * scale,
        'figure.dpi': dpi,
        'savefig.dpi': dpi,
        'savefig.transparent': transparent,
        'figure.facecolor': 'none' if transparent else COLORS['background'],
        'axes.facecolor': 'none' if transparent else COLORS['background'],
        'axes.edgecolor': COLORS['secondary'],
        'axes.labelcolor': COLORS['text'],
        'xtick.color': COLORS['text'],
        'ytick.color': COLORS['text'],
        'legend.frameon': False,
        'legend.framealpha': 0.0,
        'legend.facecolor': 'none',
        'legend.edgecolor': 'none',
        'savefig.facecolor': 'none' if transparent else COLORS['background'],
        'savefig.edgecolor': 'none' if transparent else COLORS['background'],
        'grid.color': COLORS['grid'],
        'grid.linestyle': '--',
        'grid.linewidth': 0.6,
        'grid.alpha': 0.35,
        'axes.linewidth': 0.9,
        'lines.linewidth': 2.0,
        'text.usetex': False,
    })
