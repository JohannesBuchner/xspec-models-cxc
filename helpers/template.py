"""Generate the code to be built based on the model.dat file.

Note that any error in creating the template will raise a
SystemExit exception.

"""

# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
import sys

from parse_xspec.models import parse_xspec_model_description


__all__ = ("apply", )


def replace_term(txt, term, replace):
    """Replace the first term with replace in txt"""

    idx = txt.find(term)
    if idx < 0:
        sys.stderr.write(f'ERROR: unable to find {term}\n')
        sys.exit(1)

    return txt[:idx] + replace + txt[idx + len(term):]


# At what point does it become woorth using a templating system like
# Jinja2?
#
def apply(modelfile, out_dir):
    """Parse the model.dat file and create the code.

    Parameters
    ----------
    modelfile : pathlib.Path
        The he model.dat file.
    out_dir : pathlib.Path
        The directory where to write the output.

    Returns
    -------
    models : dict
        Information on the different model types that were found and
        the files created.

    Notes
    -----
    The templates/xspec.cxx file is used as the template.

    """

    if not modelfile.is_file():
        sys.stderr.write(f'ERROR: unable to find model.dat file: {modelfile}.\n')
        sys.exit(1)

    allmodels = parse_xspec_model_description(modelfile)
    if len(allmodels) == 0:
        sys.stderr.write(f'ERROR: unable to parse model.fat file: {modelfile}\n')
        sys.exit(1)

    # Filter to the ones we care about
    models = [m for m in allmodels if m.modeltype in ['Add', 'Mul']]
    if len(models) == 0:
        sys.stderr.write(f'ERROR: unable to find any models in: {modelfile}\n')
        sys.exit(1)

    if not out_dir.is_dir():
        sys.stderr.write(f'ERROR: unable to find output directory: {out_dir}\n')
        sys.exit(1)

    # Create the code we want to compile
    #
    template_dir = pathlib.Path('template')
    filename = pathlib.Path('xspec.cxx')
    template = template_dir / filename
    outfile = out_dir / filename

    # Ugly information flow here
    addmodels = []
    mulmodels = []
    f77models = []
    cxxmodels = []
    cmodels = []

    def wrapmod(model):
        """What is the m.def line for this model?"""

        npars = len(model.pars)
        if model.modeltype == 'Add':
            mtype = 'additive'
            addmodels.append(model.name)
        elif model.modeltype == 'Mul':
            mtype = 'multiplicative'
            mulmodels.append(model.name)
        else:
            assert False, model.modeltype

        out = f'    m.def("{model.name}", wrapper'

        if model.language == 'Fortran - single precision':
            out += f'_f<{model.funcname}_'
            f77models.append(model.funcname)
        elif model.language == 'C++ style':
            out += f'_C<C_{model.funcname}'
            cxxmodels.append(model.funcname)
        elif model.language == 'C style':
            out += f'_C<{model.funcname}'
            cmodels.append(model.funcname)
        else:
            assert False, (model.name, model.funcname, model.language)

        out += f', {npars}>, '
        out += f'"The XSPEC {mtype} {model.name} model ({npars} parameters).",'
        out += '"pars"_a,"energies"_a,"spectrum"_a=1'
        if not model.language.startswith('Fortran'):
            out += ',"initStr"_a=""'
        out += ');'
        return out

    mstrs = [wrapmod(m) for m in models]

    with template.open(mode='rt') as ifh:
        out = ifh.read()
        out = replace_term(out, '@@ADDMODELS@@', '\n'.join(addmodels))
        out = replace_term(out, '@@MULMODELS@@', '\n'.join(mulmodels))
        out = replace_term(out, '@@MODELS@@', '\n'.join(mstrs))

    out_dir.mkdir(exist_ok=True)
    with outfile.open(mode='wt') as ofh:
        ofh.write(out)

    return {'outfile': outfile,
            'models': [m.name for m in models],
            'allmodels': [m.name for m in allmodels],
            'additive': addmodels,
            'multiplicative': mulmodels,
            'C++': cxxmodels,
            'C': cmodels,
            'f77': f77models}