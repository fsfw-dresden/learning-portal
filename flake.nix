{
  description = "PyQt5 Hello World Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let 
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages.default = pkgs.python3Packages.buildPythonApplication {
          pname = "hello-pyqt";
          version = "0.1.0";
          src = ./.;
          format = "setuptools";
          
          propagatedBuildInputs = with pkgs.python3Packages; [
            pyqt5
            pillow
            (buildPythonPackage rec {
              pname = "anthropic";
              version = "0.18.1";  # Latest stable version
              format = "pyproject";
              
              src = fetchPypi {
                inherit pname version;
                sha256 = "sha256-Hs+T8VpLGvkHQhzszjVJJsRoXb2r5vXZwFkRiHmhxQE=";
              };
              
              propagatedBuildInputs = with pkgs.python3Packages; [
                httpx
                pydantic
                typing-extensions
                distro
              ];
              
              doCheck = false;
            })
          ];
          
          nativeBuildInputs = with pkgs; [
            qt5.wrapQtAppsHook
          ];

          doCheck = false;  # Skip tests since we don't have any
        };

        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            python3Packages.pyqt5
            (python3.pkgs.buildPythonPackage rec {
              pname = "anthropic";
              version = "0.18.1";
              format = "pyproject";
              
              src = python3.pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-Hs+T8VpLGvkHQhzszjVJJsRoXb2r5vXZwFkRiHmhxQE=";
              };
              
              propagatedBuildInputs = with python3.pkgs; [
                httpx
                pydantic
                typing-extensions
                distro
              ];
              
              doCheck = false;
            })
            python3Packages.pillow
          ];
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
        };
      }
    );
}
