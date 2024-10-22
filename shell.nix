{ pkgs ? import <nixpkgs> {} }:
let
  my-python-packages = ps: with ps; [
    (buildPythonPackage rec {
      pname = "futhark-data";
      version = "1.0.2";
      src = fetchPypi {
        inherit pname version;
        sha256 = "sha256-FJOhVr65U3kP408BbA42jbGGD6x+tVh+TNhsYv8bUT0=";
      };
      doCheck = false;
    })
    numpy
  ];
  my-python = pkgs.python3.withPackages my-python-packages;
in my-python.env
