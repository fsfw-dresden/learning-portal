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
          setuptools  # Provides pkg_resources
        ] ++ [ pkgs.qt5.qttools ]; # Adds lrelease and other Qt tools
        
        commonPropagatedBuildInputs = [];
        
      in
      rec {
        packages = {
          schulstick = pkgs.python3Packages.buildPythonApplication {
            pname = "schulstick";
            version = "0.1.0";
            src = ./.;
            format = "pyproject";
            
            # Build and install translations
            preBuild = ''
              cd src/welcome
              mkdir -p translations
              for ts in translations/*.ts; do
                ${pkgs.qt5.qttools.dev}/bin/lrelease $ts
              done
              cd ../..
            '';

            # Include data files in the package
            postInstall = ''
              # Copy translation files
              mkdir -p $out/${pkgs.python3.sitePackages}/welcome/translations/
              cp -r src/welcome/translations/*.qm $out/${pkgs.python3.sitePackages}/welcome/translations/
              cp -r $src/src/vision_assistant/assets $out/${pkgs.python3.sitePackages}/vision_assistant/
            '';
            
            nativeBuildInputs = with pkgs.python3Packages; [
              hatchling
            ] ++ [ 
              pkgs.qt5.wrapQtAppsHook
              pkgs.qt5.qttools  # Adds lrelease
            ];
            
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
          portal = flake-utils.lib.mkApp {
            drv = self.packages.${system}.schulstick;
            name = "portal";
          };
          default = self.apps.${system}.vision-assistant;
        };

        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
          ] ++ commonBuildInputs ++ [
            python3Packages.pillow
          ];
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
        };
      }
    );
}
