{
  description = "PyQt5 Hello World Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let 
        pkgs = nixpkgs.legacyPackages.${system};
        
        commonBuildInputs = with pkgs.python3Packages; [
          pyqt5
          pyqtwebengine
          pillow
          qt-material
        ];
        
        commonPropagatedBuildInputs = with pkgs.python3Packages; [
          (buildPythonPackage rec {
            pname = "anthropic";
            version = "0.37.1";
            format = "pyproject";
            
            src = fetchPypi {
              inherit pname version;
              sha256 = "sha256-mfaIJleV2qe6klbuaOry8F1TzZnXQX9KDC3CksEG0Ao=";
            };
            
            nativeBuildInputs = with pkgs.python3Packages; [
              hatchling
              hatch-fancy-pypi-readme
            ];
            
            propagatedBuildInputs = with pkgs.python3Packages; [
              httpx
              pydantic
              typing-extensions
              distro
              boto3
              google-cloud-core
              google-api-core
              google-auth
              tiktoken
              tokenizers
              jiter
            ];
            
            doCheck = false;
          })
        ];
        
      in
      rec {
        packages = {
          vision-assistant = pkgs.python3Packages.buildPythonApplication {
          pname = "vision-assistant";
          version = "0.1.0";
          src = ./.;
          format = "pyproject";
          
          nativeBuildInputs = with pkgs.python3Packages; [
            hatchling
          ] ++ [ pkgs.qt5.wrapQtAppsHook ];
          
          propagatedBuildInputs = with pkgs.python3Packages; [
            pyqt5
            pyqtwebengine
            pillow
            platformdirs
            qt-material
            (buildPythonPackage rec {
              pname = "anthropic";
              version = "0.37.1";
              format = "pyproject";
              
              src = fetchPypi {
                inherit pname version;
                sha256 = "sha256-mfaIJleV2qe6klbuaOry8F1TzZnXQX9KDC3CksEG0Ao=";
              };
              
              nativeBuildInputs = with pkgs.python3Packages; [
                hatchling
                hatch-fancy-pypi-readme
              ];
              
              propagatedBuildInputs = with pkgs.python3Packages; [
                httpx
                pydantic
                typing-extensions
                distro
                google-cloud-core
                google-api-core
                google-auth
                boto3
                tiktoken
                tokenizers
                jiter
              ];
              
              doCheck = false;
            })
          ];
          
          doCheck = false;  # Skip tests since we don't have any
        };
        
          welcome = pkgs.python3Packages.buildPythonApplication {
            pname = "welcome";
            version = "0.1.0";
            src = ./.;
            format = "pyproject";
            
            nativeBuildInputs = with pkgs.python3Packages; [
              hatchling
            ] ++ [ pkgs.qt5.wrapQtAppsHook ];
            
            propagatedBuildInputs = commonBuildInputs ++ commonPropagatedBuildInputs;
            
            doCheck = false;
          };
          
          default = packages.vision-assistant;
        };
        
        apps = {
          vision-assistant = flake-utils.lib.mkApp { 
            drv = self.packages.${system}.vision-assistant;
            name = "vision-assistant";
          };
          welcome = flake-utils.lib.mkApp {
            drv = self.packages.${system}.welcome;
            name = "welcome";
          };
          default = self.apps.${system}.vision-assistant;
        };

        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
          ] ++ commonBuildInputs ++ [
            (python3.pkgs.buildPythonPackage rec {
              pname = "anthropic";
              version = "0.37.1";
              format = "pyproject";
              
              src = python3.pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-mfaIJleV2qe6klbuaOry8F1TzZnXQX9KDC3CksEG0Ao=";
              };
              
              nativeBuildInputs = with python3.pkgs; [
                hatchling
                hatch-fancy-pypi-readme
              ];
              
              propagatedBuildInputs = with python3.pkgs; [
                httpx
                pydantic
                typing-extensions
                distro
                tiktoken
                tokenizers
                jiter
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
