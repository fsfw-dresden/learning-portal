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
            anthropic
            pillow
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
            python3Packages.anthropic
            python3Packages.pillow
          ];
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
        };
      }
    );
}
