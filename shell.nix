{
    pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
    buildInputs = with pkgs; [
        python3
        python3Packages.pandas
        python3Packages.numpy

        sage
        jupyter-all

        gnumake
        gcc
        bear # C/C++ clangd tool to expose python includes
    ];
}
