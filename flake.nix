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
          platformdirs
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
          schulstick = pkgs.python3Packages.buildPythonApplication {
            pname = "schulstick";
            version = "0.1.0";
            src = ./.;
            format = "pyproject";
            
            nativeBuildInputs = with pkgs.python3Packages; [
              hatchling
            ] ++ [ pkgs.qt5.wrapQtAppsHook ];
            
            propagatedBuildInputs = commonBuildInputs ++ commonPropagatedBuildInputs;
            
            doCheck = false;
          };
          
          default = packages.schulstick;
        };
        
        apps = {
          vision-assistant = flake-utils.lib.mkApp { 
            drv = self.packages.${system}.schulstick;
            name = "vision-assistant";
          };
          welcome = flake-utils.lib.mkApp {
            drv = self.packages.${system}.schulstick;
            name = "welcome";
          };
          icon-finder = flake-utils.lib.mkApp {
            drv = self.packages.${system}.schulstick;
            name = "icon-finder";
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
