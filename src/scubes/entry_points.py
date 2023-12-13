import sys
from os import getcwd
from shutil import which

from . import __author__, __zp_cat__, __zpcorr_path__
from .constants import WAVE_EFF

from .utilities.io import print_level
from .utilities.args import create_parser

SPLUS_MOTD_TOP = '┌─┐   ┌─┐┬ ┬┌┐ ┌─┐┌─┐ '
SPLUS_MOTD_MID = '└─┐───│  │ │├┴┐├┤ └─┐ '
SPLUS_MOTD_BOT = '└─┘   └─┘└─┘└─┘└─┘└─┘ '
SPLUS_MOTD_SEP = '----------------------'

SPLUS_PROG_DESC = f'''
{SPLUS_MOTD_TOP} | Create S-PLUS galaxies data cubes, a.k.a. S-CUBES. 
{SPLUS_MOTD_MID} | S-CUBES is an organized FITS file with data, errors, 
{SPLUS_MOTD_BOT} | mask and metadata about some galaxy present on any 
{SPLUS_MOTD_SEP} + S-PLUS observed tile. Any problem contact:

   {__author__}

'''

SPLUS_ARGS = {
    # optional arguments
    'redo': ['r', dict(action='store_true', default=False, help='Enable redo mode to overwrite final cubes.')],
    'clean': ['c', dict(action='store_true', default=False, help='Clean intermediate files after processing.')],
    'force': ['f', dict(action='store_true', default=False, help='Force overwrite of existing files.')],
    'bands': ['b', dict(default=list(WAVE_EFF.keys()), nargs='+', help='List of S-PLUS bands (space separated).')],
    'size': ['l', dict(default=500, type=int, help='Size of the cube in pixels.')],
    #'angsize': ['a', dict(default=50, type=float, help="Galaxy's Angular size in arcsec.")],
    'work_dir': ['w', dict(default=getcwd(), help='Working directory.')],
    'output_dir': ['o', dict(default=getcwd(), help='Output directory.')],
    'sextractor': ['x', dict(default='sex', help='Path to SExtractor executable.')],
    'class_star': ['p', dict(default=0.25, type=float, help='SExtractor CLASS_STAR parameter for star/galaxy separation.')],
    'verbose': ['v', dict(action='count', default=0, help='Verbosity level.')],
    'debug': ['D', dict(action='store_true', default=False, help='Enable debug mode.')],
    'satur_level': ['S', dict(default=1600.0, type=float, help='Saturation level for the png images.')],
    'zpcorr_dir': ['Z', dict(default=__zpcorr_path__, help='Zero-point correction directory.')],
    'zp_table': ['z', dict(default=__zp_cat__, help='Zero-point table.')],
    'back_size': ['B', dict(default=64, type=int, help='Background mesh size for SExtractor.')],
    'detect_thresh': ['T', dict(default=1.1, type=float, help='Detection threshold for SExtractor.')],
    'username': ['U', dict(default=None, help='S-PLUS Cloud username.')],
    'password': ['P', dict(default=None, help='S-PLUS Cloud password.')],
    'mask_stars': ['M', dict(action='store_true', default=False, help='Run SExtractor to auto-identify stars on stamp.')],
    'det_img': ['I', dict(action='store_true', default=False, help='Downloads detection image for the stamp. Needed if --mask_stars is active.')],
    'estimate_fwhm': ['F', dict(action='store_true', default=False, help='Runs SExtractor two times estimating the SEEING_FWHM of the detection image.')],

    # positional arguments
    'tile': ['pos', dict(metavar='SPLUS_TILE', help='Name of the S-PLUS tile')],
    'ra': ['pos', dict(metavar='RA', help="Galaxy's right ascension")],
    'dec': ['pos', dict(metavar='DEC', help="Galaxy's declination")],
    'galaxy': ['pos', dict(metavar='GALAXY_NAME', help="Galaxy's name")],
    'specz': ['pos', dict(type=float, metavar='REDSHIFT', help='Spectroscopic or photometric redshift of the galaxy')],
}

def scubes_argparse(args):
    '''
    A particular parser of the command-line arguments for `scubes` entry-point script.

    Parameters
    ----------
    args : :class:`argparse.Namespace`
        Command-line arguments parsed by :function:`argparse.ArgumentParser.parse_args()`

    Returns
    -------
    :class:`argparse.Namespace`
        Command-line arguments parsed.
    '''
    _sex = which(args.sextractor)
    if _sex is None:
        print_level(f'{args.sextractor}: SExtractor exec not found', 1, args.verbose)
        _SExtr_names = ['sex', 'source-extractor']
        for name in _SExtr_names:
            _sex = which(name)
            if _sex is None:
                print_level(f'{name}: SExtractor exec not found', 2, args.verbose)
            else:
                print_level(f'{name}: SExtractor found. Forcing --sextractor={_sex}', 1, args.verbose)
                args.sextractor = _sex
                pass
        if _sex is None:
            print_level(f'SExtractor not found')
            sys.exit(1)
    return args

def scubes():
    from .core import SCubes

    parser = create_parser(args_dict=SPLUS_ARGS, program_description=SPLUS_PROG_DESC)
    args = scubes_argparse(parser.parse_args(args=sys.argv[1:]))
    scubes = SCubes(args)
    scubes.create_cube(flam_scale=None)

SPLUS_RGB_DESC = f'''
{SPLUS_MOTD_TOP} | Downloads S-PLUS RGB Image.
{SPLUS_MOTD_MID} | It will download a png file containing the
{SPLUS_MOTD_BOT} | RGB image for a stamp created using splusdata
{SPLUS_MOTD_SEP} + API.

   {__author__}

'''

SPLUS_RGB_ARGS = {
    # optional arguments
    'size': ['l', dict(default=500, type=int, help='Size of the cube in pixels.')],
    'verbose': ['v', dict(action='count', default=0, help='Verbosity level.')],
    'username': ['U', dict(default=None, help='S-PLUS Cloud username.')],
    'password': ['P', dict(default=None, help='S-PLUS Cloud password.')],
    'galaxy': ['g', dict(default=None, metavar='GALAXY_NAME', help="Galaxy's name")],

    # positional arguments
    'tile': ['pos', dict(metavar='SPLUS_TILE', help='Name of the S-PLUS tile')],
    'ra': ['pos', dict(metavar='RA', help="Galaxy's right ascension")],
    'dec': ['pos', dict(metavar='DEC', help="Galaxy's declination")],
}

def get_lupton_RGB_argsparse(args):
    '''
    A particular parser of the command-line arguments for `get_lupton_RGB`
    entry-point script.

    Parameters
    ----------
    args : :class:`argparse.Namespace`
        Command-line arguments parsed by :function:`argparse.ArgumentParser.parse_args()`

    Returns
    -------
    :class:`argparse.Namespace`
        Command-line arguments parsed.
    '''
    from .utilities.io import convert_coord_to_degrees

    for key, value in args.__dict__.items():
        print_level(f'control obj - key: {key} - value: {value}', 2, args.verbose)

    args.ra, args.dec = convert_coord_to_degrees(args.ra, args.dec)

    return args

def get_lupton_RGB():
    from PIL import Image
    from .utilities.splusdata import connect_splus_cloud

    parser = create_parser(args_dict=SPLUS_RGB_ARGS, program_description=SPLUS_RGB_DESC)
    args = get_lupton_RGB_argsparse(parser.parse_args(args=sys.argv[1:]))
    conn = connect_splus_cloud(args.username, args.password)
    if args.galaxy is None:
        args.galaxy = 'OBJECT'
    fname = f'{args.galaxy}_{args.tile}_{args.size}x{args.size}.png'
    print_level(f'{args.galaxy} @ {args.tile} - downloading RGB image', 1, args.verbose)
    img = conn.lupton_rgb(ra=args.ra, dec=args.dec, size=args.size, option=args.tile) 
    img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(fname, 'PNG')

def sex_mask_stars_args(args):
    '''TODO'''
    pass

def sex_mask_stars():
    '''TODO'''
    pass
    