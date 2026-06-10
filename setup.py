from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


PROJECT_ROOT = Path(__file__).resolve().parent
PACKAGE_VERSION = "0.1.3"
PACKAGE_README = "docs/EVIDENCE_COURT_V0_1_PACKAGE_README.md"
EVIDENCE_COURT_PACKAGE_MODULES = {"__init__", "evidence_court"}
EVIDENCE_COURT_EXAMPLES = [
    "examples/evidence-court/bad-run.json",
    "examples/evidence-court/good-run.json",
]


class EvidenceCourtBuildPy(_build_py):
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        if package != "quantagent":
            return []
        return [
            module
            for module in modules
            if module[1] in EVIDENCE_COURT_PACKAGE_MODULES
        ]


setup(
    name="open-mako",
    version=PACKAGE_VERSION,
    description="A local-first auditable agent runtime for coding and data work.",
    long_description=(PROJECT_ROOT / PACKAGE_README).read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/1966536805l-crypto/openmako-evidence-court",
    project_urls={
        "Homepage": "https://github.com/1966536805l-crypto/openmako-evidence-court",
        "Repository": "https://github.com/1966536805l-crypto/openmako-evidence-court",
    },
    author="OpenMako contributors",
    author_email="1966536805l-crypto@users.noreply.github.com",
    license="MIT",
    license_files=["LICENSE"],
    python_requires=">=3.9",
    packages=["quantagent"],
    include_package_data=True,
    data_files=[
        ("share/open-mako/examples/evidence-court", EVIDENCE_COURT_EXAMPLES),
    ],
    entry_points={
        "console_scripts": [
            "mako=quantagent.evidence_court:main",
            "openmako=quantagent.evidence_court:main",
            "qagent=quantagent.evidence_court:main",
        ]
    },
    cmdclass={"build_py": EvidenceCourtBuildPy},
)
