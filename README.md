About this repository
=====================

This repository contains some configurations and scripts used on my
systems. I mainly use Linux Mint Debian Edition (LMDE), but most of them should
work on every \*nix system.

**Feel free to contribute and improve the tools!**

Content
=======

vimrc
-----

This folder contains my vimrc. It mainly contains the following features:

* German and english spell checking
* Syntax highlighting for python, markdown, LaTeX...
* Line numbers
* Mark long lines
* Show tabs
* ...


vim-cheatsheet
--------------

A latex document with some useful commands for my vimrc

misc
----

Several tools. Maybe they will help someone...

fun
---

Fun scripts ;-)

apt
---

This directory contains the main files from my `/etc/apt/` directory. The idea
is the following:

1. Use Debian testing as default repository
2. Add experimental and unstable repositories
3. Set the priority to low for experimental and unstable so they are only used
   if the corresponding package was not found in the testing repo (useful for
   Skype). This is done using the files `experimental` and `testing`in the
   directory `preferences.d`
4. Example config to force usage of unstable for Icedove and Iceweasel (I know
   that iceweasel is deprecated and Firefox is available...)

Use `netselect-apt` to figure out the fastest mirror for you location:

    sudo netselect-apt --sources --nonfree testing
