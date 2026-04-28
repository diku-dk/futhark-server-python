{ pkgs ? import <nixpkgs> {} }:
let
  my-python-packages = ps: with ps; [
    (buildPythonPackage rec {
      pname = "futhark-data";
      version = "1.0.3";
      src = fetchPypi {
        inherit pname version;
        sha256 = "sha256-HoxeSLXt2B1X3PZmfZmnIOipLec4ba3VkUBLtZhVPPU=";
      };
      pyproject = true;
      dependencies = [ numpy ] ;
      build-system = [ setuptools ];
      doCheck = false;
    })
    numpy
  ];
  my-python = pkgs.python3.withPackages my-python-packages;
in my-python.env
