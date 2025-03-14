{
  description = "Open Educational Portal App for IT competency development integrated with Schulstick";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let 
        pkgs = nixpkgs.legacyPackages.${system};
        
        commonPythonBuildInputs = with pkgs.python3Packages; [
          pyqt5
          pyqtwebengine
          pillow
          platformdirs
          qt-material
          setuptools  # Provides pkg_resources
          requests
          pyyaml
          pyxdg
          toml
          fuzzywuzzy
          python-Levenshtein
          dataclass-wizard
          packaging # for release script
        ];
        commonQtBuildInputs = with pkgs.qt5; [ 
          qttools  # Adds lrelease and other Qt tools
          qtbase
          qtwayland
          qtwebchannel
        ];
        commonBuildInputs = commonPythonBuildInputs ++ commonQtBuildInputs;
      in
      rec {
        packages = {
          schulstick-portal = pkgs.python3Packages.buildPythonApplication {
            pname = "schulstick-portal";
            version = "0.1.5";
            src = ./.;
            format = "pyproject";
            
            # Build and install translations
            preBuild = ''
              for package in welcome tutor; do
                cd src/$package
                mkdir -p translations
                for ts in translations/*.ts; do
                  ${pkgs.qt5.qttools.dev}/bin/lrelease $ts
                done
                cd ../..
              done
            '';

            # Include data files in the package
            postInstall = ''
              # Copy translation files
              # for all translations
              for package in welcome tutor; do  
                mkdir -p $out/${pkgs.python3.sitePackages}/$package/translations/
                cp -r src/$package/translations/*.qm $out/${pkgs.python3.sitePackages}/$package/translations/
              done
              cp -r $src/src/vision_assistant/assets $out/${pkgs.python3.sitePackages}/vision_assistant/
            '';
            
            nativeBuildInputs = with pkgs.python3Packages; [
              hatchling

              pkgs.qt5.wrapQtAppsHook
              pkgs.qt5.qttools  # Adds lrelease
            ];
            
            propagatedBuildInputs = commonBuildInputs;

            doCheck = false;
          };
          
          default = packages.schulstick-portal;
        };
        
        apps = {
          vision-assistant = flake-utils.lib.mkApp { 
            drv = self.packages.${system}.schulstick-portal;
            name = "vision-assistant";
          };
          welcome = flake-utils.lib.mkApp {
            drv = self.packages.${system}.schulstick-portal;
            name = "welcome";
          };
          icon-finder = flake-utils.lib.mkApp {
            drv = self.packages.${system}.schulstick-portal;
            name = "icon-finder";
          };
          portal = flake-utils.lib.mkApp {
            drv = self.packages.${system}.schulstick-portal;
            name = "portal";
          };
          tutor = flake-utils.lib.mkApp {
            drv = self.packages.${system}.schulstick-portal;
            name = "tutor";
          };
          release = flake-utils.lib.mkApp {
            drv = self.packages.${system}.schulstick-portal;
            name = "release";
          };
          dataclass-forms-demo = flake-utils.lib.mkApp {
            drv = self.packages.${system}.schulstick-portal;
            name = "dataclass-forms-demo";
          };
          default = self.apps.${system}.portal;
        };

        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            debian-devscripts
            x11docker # for testing the debian build in a XFCE environment
            python3Packages.flake8
          ] ++ commonBuildInputs;
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";

          QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins/platforms";
          
          SCHULSTICK_ENV = "development";
          
          # Add shell aliases for development convenience
          shellHook = ''
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            alias vision-assistant="python -m vision_assistant.main"
            alias welcome="python -m welcome.main"
            alias icon-finder="python -m helper.icon_finder"
            alias portal="python -m portal.main"
            alias tutor="python -m tutor.main"
            alias dataclass-forms-demo="python -m dataclass_forms.demo"
            alias devserver="npx @liascript/devserver --live --input ./OER-materials"  ## broken. might want use: "node dist/index.js -i ../schulstick-portal/OER-materials/"
            
            echo "Development shell aliases available:"
            echo "  vision-assistant - Run the vision assistant"
            echo "  welcome          - Run the welcome wizard"
            echo "  icon-finder      - Run the icon finder utility"
            echo "  portal           - Run the portal app"
            echo "  tutor            - Run the tutor app"
            echo "  devserver        - Run the devserver for the example courses"
          '';
        };
      }
    );
}
