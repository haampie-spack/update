import re
import os
import random

import spack.repo
from llnl.util.filesystem import working_dir
from spack.util.executable import Executable

blacklisted_packages = set((
    "intel-parallel-studio",
    "intel-oneapi-mpi",
    "intel-mpi",
    "cuda",
    "qt",
    "intel-mkl",
    "intel-oneapi-mkl",
    "git",
    "intel-tbb",
    "fenics"
))

blacklisted_versions = {
    "amdblis": set(("2.2-4")),
    "amdlibflame": set(("2.2-4", "5.1.0")),
    "amdscalapack": set(("2.2-4")),
}

def is_allowed_version(v):
    return all(isinstance(x, int) for x in v.version)

def try_and_update(pkg):
    try:
        versions = pkg.fetch_remote_versions()
        # filter versions that are > current max, and skip release candidates etc
        # todo: allow new patch versions of older minor versions
        current_max = max(pkg.versions.keys())
        keys = sorted([v for v in versions.keys() if v > current_max and is_allowed_version(v)], reverse=True)

        if pkg.name in blacklisted_versions:
            skip_list = blacklisted_versions[pkg.name]
            keys = [k for k in keys if k not in skip_list]

        if len(keys) == 0:
            return

        print("- Considering {}".format(keys))

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

def main():
    list_of_packages = [p for p in spack.repo.path.all_packages() if p.name not in blacklisted_packages]

    # shuffle to ensure we get updates even when there's timeouts etc
    random.shuffle(list_of_packages)

    for (num, p) in enumerate(list_of_packages):
        print("[{0}/{1}] {2}".format(num + 1, len(list_of_packages), p.name))
        try_and_update(p)

if __name__ == "__main__":
    main()