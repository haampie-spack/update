import re
import os
import spack.repo
from llnl.util.filesystem import working_dir
from spack.util.executable import Executable

def is_allowed_version(v):
    return all(isinstance(x, int) for x in v.version)

def try_and_update(name):
    try:
        print("Checking {0}".format(name))
        pkg = spack.repo.get(name)
        versions = pkg.fetch_remote_versions()
        # filter versions that are > current max, and skip release candidates etc
        # todo: allow new patch versions of older minor versions
        current_max = max(pkg.versions.keys())
        keys = sorted([v for v in versions.keys() if v > current_max and is_allowed_version(v)], reverse=True)
        if len(keys) == 0:
            return
        print("Considering {} for {}".format(keys, name))
        filtered_map = {k: versions[k] for k in keys}
        result = spack.stage.get_checksums_for_versions(filtered_map, pkg.name, keep_stage=False, batch=True, fetch_options=pkg.fetch_options)
        packagedotpy = os.path.join(pkg.package_dir, "package.py")
        with open(packagedotpy, "r") as file:
            contents = file.read()
        regex = re.compile("    version\\(")
        replaced = regex.sub(result + "\n    version(", contents, 1)
        with open(packagedotpy, "w") as file:
            file.write(replaced)
        with working_dir(pkg.package_dir):
            Executable("git")("add", ".")
            Executable("git")("commit", "-m", "Add new versions of {0}".format(pkg.name))
    except:
        print("Failure updating {0}".format(name))

def main(packages):
    for pkgname in packages:
        try_and_update(pkgname)

if __name__ == "__main__":
    main([
        "python",
        "py-setuptools",
        "r",
        "cmake",
        "perl",
        "pkg-config",
        "pkgconf",
        "py-numpy",
        "zlib",
        "libtool",
        "autoconf",
        "automake",
        "openmpi",
        "m4",
        "nvhpc",
        "mpich",
        "mvapich2",
        "mvapich2-gdr",
        "mvapich2x",
        "spectrum-mpi",
        "mpilander",
        "mpt",
        "cray-mpich",
        "fujitsu-mpi",
        "py-six",
        "boost",
        "icedtea",
        "jdk",
        "util-macros",
        "openjdk",
        "ibm-java",
        "libx11",
        "py-scipy",
        "r-rcpp",
        "py-matplotlib",
        "hdf5",
        "py-cython",
        "ncurses",
        "openssl",
        "py-azure-cli",
        "netlib-lapack",
        "r-seurat",
        "py-requests",
        "atlas",
        "libxml2",
        "root",
        "openblas",
        "r-ggplot2",
        "xproto",
        "py-msrest",
        "flexiblas",
        "cray-libsci",
        "fujitsu-ssl2",
        "veclibfort",
        "py-sphinx",
        "glib",
        "r-biobase",
        "bison",
        "py-azure-common",
        "py-msrestazure",
        "gdal",
        "flex",
        "curl",
        "r-mass",
        "gettext",
        "essl",
        "amdblis",
        "blis",
        "r-biocgenerics",
        "netlib-xblas",
        "fftw",
        "r-matrix",
        "amdlibflame",
        "libflame",
        "go",
        "libpng",
        "py-pyyaml",
        "geant4-data",
        "py-azure-mgmt-nspkg",
        "biopieces",
        "py-torch",
        "py-pandas",
        "gsl",
        # "git", # git has a bit of a special structure
        "r-rlang",
        "r-magrittr",
        "libxt",
        "libxext",
        "r-dplyr",
        "py-pytest",
        "gmake",
        "netcdf-c",
        "bzip2"
    ])